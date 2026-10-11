"""Task B timing pilot (PLAN step 10, part a; SRS D25): step times of three model sizes on text8.

Usage, from the repository root (normally through scripts/ops/launch_visible.ps1)::

    python -m scripts.pilot_task_b_timing --config configs/task_b/pilot.toml

For each model width and batch size it times, on real text8 training batches,
one optimizer step of: the centralized model; a sliced worker (a slice model
holding its experts only); a partial-update worker; and a full-averaging
worker, each with the exact code the runs will use (``build_worker_model``,
``make_optimizer``, ``train_steps``). It also times a merge of N worker results
and one evaluation of the whole test split. Medians of ``timed_steps`` steps
after ``warmup_steps``; peak GPU memory per measurement. The models are
untrained: the losses mean nothing, only the times and memory do.

Logs a run (configuration, environment, every measurement) and writes
``results/task_b_timing_pilot.md``.
See docs/implementations/2026-10-09-task-b-data-and-timing-pilot.md.
"""

from __future__ import annotations

import argparse
import dataclasses
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from cassandra_chorus import paths, repro
from cassandra_chorus.config import RunSection, load_config
from cassandra_chorus.coordinator import WorkerResult, merge
from cassandra_chorus.data.text8 import Text8, Text8Section
from cassandra_chorus.metrics.task_b import evaluate_bpc
from cassandra_chorus.model import ModelSection, MoETransformer, count_parameters
from cassandra_chorus.ops import enforce, load_ops_settings, operations, run_preflight
from cassandra_chorus.runlog import RunLogger, make_run_id
from cassandra_chorus.sim.harness import SimSection, make_outer, round_slices
from cassandra_chorus.sim.worker import build_worker_model, returned_state
from cassandra_chorus.train import OptimSection, make_optimizer, train_steps

MODES = ("centralized", "sliced", "partial", "full")


@dataclasses.dataclass(frozen=True)
class PilotSection:
    widths: tuple[int, ...] = (256, 320, 384)
    n_layers: int = 6
    n_experts: int = 8
    top_k: int = 2
    head_width: int = 64          # heads = width / head_width
    expert_ratio: int = 2         # expert hidden size = ratio × width
    batch_sizes: tuple[int, ...] = (32, 64)
    warmup_steps: int = 10
    timed_steps: int = 50
    merge_repeats: int = 5
    schedule_steps: int = 20000   # only shapes the learning-rate schedule during timing


@dataclasses.dataclass(frozen=True)
class PilotConfig:
    run: RunSection
    text8: Text8Section = dataclasses.field(default_factory=Text8Section)
    optim: OptimSection = dataclasses.field(default_factory=OptimSection)
    sim: SimSection = dataclasses.field(default_factory=SimSection)
    pilot: PilotSection = dataclasses.field(default_factory=PilotSection)


def model_config(width: int, pilot: PilotSection, data: Text8) -> ModelSection:
    return ModelSection(vocab_size=data.vocab_size, context_length=data.cfg.context_length, d_model=width,
                        n_layers=pilot.n_layers, n_heads=width // pilot.head_width,
                        expert_hidden=pilot.expert_ratio * width, n_experts=pilot.n_experts, top_k=pilot.top_k,
                        dispatch="sparse")


def sync(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize()


def time_steps(model, optim: OptimSection, next_batch, device, pilot: PilotSection) -> dict:
    """Median seconds per optimizer step and peak memory, after warm-up."""
    optimizer = make_optimizer(model, optim)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    times = []
    for i in range(pilot.warmup_steps + pilot.timed_steps):
        sync(device)
        t0 = time.perf_counter()
        train_steps(model, optimizer, next_batch, 1, optim, device, start_step=i, total_steps=pilot.schedule_steps)
        sync(device)
        if i >= pilot.warmup_steps:
            times.append(time.perf_counter() - t0)
    peak = torch.cuda.max_memory_allocated() / 2**20 if device.type == "cuda" else None
    return {"median_seconds": statistics.median(times), "min_seconds": min(times), "max_seconds": max(times), "peak_mib": peak}


def free(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.empty_cache()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--set", dest="overrides", action="append", default=[], metavar="SECTION.KEY=VALUE")
    parser.add_argument("--out", type=Path, default=paths.REPO_ROOT / "results" / "task_b_timing_pilot.md")
    args = parser.parse_args(argv)

    cfg = load_config(args.config, PilotConfig, args.overrides)
    repro.prepare_process(cfg.run.determinism)  # before any CUDA work
    repro.set_cpu_threads(cfg.run.cpu_threads)
    device = torch.device(cfg.run.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("the configuration asks for 'cuda' but CUDA is not available")
    data = Text8(cfg.text8)
    pilot, sim = cfg.pilot, cfg.sim
    ops_settings, ops_source = load_ops_settings()
    checks = run_preflight(ops_settings, paths.runs_root(), expected_seconds=900)
    enforce(checks)

    rows = []
    with RunLogger.create(paths.runs_root(), make_run_id(cfg.run.name, cfg.run.seed)) as log:
        seeds = repro.seed_everything(cfg.run.seed)
        seeds["pilot_data"] = repro.derive_seed(cfg.run.seed, "task_b/pilot")
        determinism = repro.apply_determinism(cfg.run.determinism)
        log.write_header(config=cfg, config_path=args.config, seeds=seeds,
                         environment=repro.environment_info(), determinism=determinism)
        log.write("setup", text8_path=str(data.path), text8_sha256=cfg.text8.sha256,
                  test_windows=data.n_windows("test"))
        generator = torch.Generator().manual_seed(seeds["pilot_data"])
        t_start = time.perf_counter()
        with operations(log, ops_settings, ops_source, checks), log.capture_warnings():
            for width in pilot.widths:
                mcfg = model_config(width, pilot, data)
                with torch.random.fork_rng(devices=[]):
                    central = MoETransformer(mcfg).to(device)
                n_params = count_parameters(central)["total"]
                # The global model stays on the CPU while workers are timed, so a worker's peak memory is its own.
                global_state = {k: v.detach().cpu().clone() for k, v in central.state_dict().items()}
                slices = round_slices(sim, mcfg.n_layers, mcfg.n_experts, mcfg.top_k, 0, cfg.run.seed)
                first = sorted(slices)[0]
                for batch_size in pilot.batch_sizes:
                    def next_batch(batch_size=batch_size):
                        return data.sample(batch_size, generator)
                    optim = dataclasses.replace(cfg.optim, batch_size=batch_size)
                    for mode in MODES:
                        if mode == "centralized":
                            model = central.to(device)
                        else:
                            central.to("cpu")
                            free(device)
                            model = build_worker_model(mcfg, global_state, slices[first], mode, device)
                        result = time_steps(model, optim, next_batch, device, pilot)
                        if mode != "centralized":
                            del model
                        free(device)
                        row = {"width": width, "parameters": n_params, "batch": batch_size, "mode": mode, **result}
                        rows.append(row)
                        log.write("timing", **row)
                        print(f"width {width} batch {batch_size} {mode:11s} {1000 * result['median_seconds']:7.1f} ms/step  "
                              f"peak {result['peak_mib']:.0f} MiB", flush=True)
                    central.load_state_dict(global_state)  # undo the timing steps before the next batch size
                central.to(device)
                # Merge of N sliced worker results (untrained copies; only the time matters).
                results = []
                for name in sorted(slices):
                    worker = build_worker_model(mcfg, global_state, slices[name], "sliced", device)
                    results.append(WorkerResult(slices[name], returned_state(worker, slices[name], "sliced"), 1))
                    del worker
                device_state = {k: v.to(device) for k, v in global_state.items()}  # merged on the device, as in the runs
                merge_times = []
                for _ in range(pilot.merge_repeats):
                    sync(device)
                    t0 = time.perf_counter()
                    merge(device_state, results, sim.router_rule, make_outer(sim))
                    sync(device)
                    merge_times.append(time.perf_counter() - t0)
                del results, device_state
                free(device)
                sync(device)
                t0 = time.perf_counter()
                test = evaluate_bpc(central, data, "test", device)
                sync(device)
                eval_seconds = time.perf_counter() - t0
                t0 = time.perf_counter()
                evaluate_bpc(central, data, "valid", device, max_chars=1_000_000)
                sync(device)
                curve_seconds = time.perf_counter() - t0
                extra = {"width": width, "parameters": n_params, "merge_seconds": statistics.median(merge_times),
                         "test_eval_seconds": eval_seconds, "curve_eval_seconds": curve_seconds,
                         "untrained_test_bpc": test["bpc"]}
                rows.append({"mode": "other", **extra})
                log.write("timing_other", **extra)
                print(f"width {width}: merge {1000 * extra['merge_seconds']:.0f} ms, test eval {eval_seconds:.0f} s, "
                      f"curve eval {curve_seconds:.1f} s", flush=True)
                del central
                free(device)
        log.write("final", total_seconds=time.perf_counter() - t_start)
        run_id = log.run_id
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report(rows, run_id, args.config, cfg), encoding="utf-8", newline="\n")
    print(f"report written to {args.out}")
    return 0


def report(rows, run_id: str, config_path: Path, cfg: PilotConfig) -> str:
    import subprocess

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=paths.REPO_ROOT, capture_output=True, text=True).stdout.strip()
    if subprocess.run(["git", "status", "--porcelain"], cwd=paths.REPO_ROOT, capture_output=True, text=True).stdout.strip():
        commit += " with uncommitted changes"
    timing = [r for r in rows if r["mode"] != "other"]
    other = {r["width"]: r for r in rows if r["mode"] == "other"}
    lines = [
        "# Task B · Timing pilot",
        "",
        f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC by `python -m scripts.pilot_task_b_timing` "
        f"(code `{commit}`, config `{config_path.as_posix()}`, run `{run_id}`). Untrained models: times and memory "
        "only. Median of the timed steps after warm-up; fp32, explicit attention, sparse dispatch (owner decisions). "
        "Peak memory is each model's own: model, optimizer state and activations, with nothing else on the GPU.",
        "",
        "## Milliseconds per optimizer step (peak GPU memory, MiB)",
        "",
        "| Parameters | Width | Batch × 256 | Centralized | Sliced worker | Partial-update worker | Full-averaging worker |",
        "|---|---|---|---|---|---|---|",
    ]
    for width in cfg.pilot.widths:
        for batch in cfg.pilot.batch_sizes:
            cells = {r["mode"]: r for r in timing if r["width"] == width and r["batch"] == batch}
            params = next(iter(cells.values()))["parameters"]
            fmt = lambda m: f"{1000 * cells[m]['median_seconds']:.0f} ({cells[m]['peak_mib']:.0f})"  # noqa: E731
            lines.append(f"| {params:,} | {width} | {batch} | {fmt('centralized')} | {fmt('sliced')} | {fmt('partial')} | {fmt('full')} |")
    lines += ["", "## Merge and evaluation", "",
              "| Parameters | Merge of 4 results (ms) | Whole test split (s) | Validation curve, first 1M characters (s) |",
              "|---|---|---|---|"]
    for width in cfg.pilot.widths:
        o = other[width]
        lines.append(f"| {o['parameters']:,} | {1000 * o['merge_seconds']:.0f} | {o['test_eval_seconds']:.0f} | {o['curve_eval_seconds']:.1f} |")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
