"""Sliced and local-averaging training on Task B, text8, simulated on one GPU (PLAN step 10).

Usage, from the repository root (normally through scripts/ops/launch_visible.ps1)::

    python -m scripts.train_task_b_sliced --config configs/task_b/sliced.toml [--set ...]
    python -m scripts.train_task_b_sliced --resume <run folder>

Each round assigns slices, trains the surviving workers one after another on
their own random text8 windows, merges with the coordinator, evaluates the
merged full model's bits per character on the first ``curve_max_chars``
validation characters, and writes a checkpoint, so a run resumes from its last
completed round (S0-N-04). ``sim.mode`` selects sliced training, the
partial-update arm (S0-F-26) or full-model local averaging (S0-F-14). At the
end the merged model is evaluated on the whole test split (S0-A-04). Mirrors
scripts/train_task_a_sliced.py; see docs/implementations/2026-10-09-task-b-runs.md.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
import time
from pathlib import Path

import torch

from cassandra_chorus import paths, repro
from cassandra_chorus.config import RunSection, config_hash, load_config
from cassandra_chorus.coordinator import WorkerResult, merge
from cassandra_chorus.data.text8 import Text8, Text8Section
from cassandra_chorus.metrics.task_b import evaluate_bpc
from cassandra_chorus.model import ModelSection, MoETransformer, count_parameters
from cassandra_chorus.ops import enforce, load_ops_settings, operations, run_preflight
from cassandra_chorus.runlog import RunLogger, git_state, make_run_id
from cassandra_chorus.sim import (
    SimSection,
    data_generator,
    dropped_workers,
    load_checkpoint,
    make_outer,
    round_plan,
    round_slices,
    save_checkpoint,
    train_worker,
    validate_sim,
    worker_specs,
)
from cassandra_chorus.train import OptimSection, check_schedule, decay_start


@dataclasses.dataclass(frozen=True)
class EvalSection:
    curve_max_chars: int = 1_000_000
    save_model: bool = True


@dataclasses.dataclass(frozen=True)
class SlicedTaskBConfig:
    run: RunSection
    model: ModelSection
    text8: Text8Section = dataclasses.field(default_factory=Text8Section)
    optim: OptimSection = dataclasses.field(default_factory=OptimSection)
    eval: EvalSection = dataclasses.field(default_factory=EvalSection)
    sim: SimSection = dataclasses.field(default_factory=SimSection)


class StopAfterRound(Exception):
    """Raised by --stop-after-round to simulate an interruption at a known point."""


def check(cfg: SlicedTaskBConfig, data: Text8) -> None:
    problems = []
    if cfg.model.vocab_size != data.vocab_size:
        problems.append(f"model.vocab_size is {cfg.model.vocab_size} but text8 needs {data.vocab_size}")
    if cfg.model.context_length != cfg.text8.context_length:
        problems.append(f"model.context_length is {cfg.model.context_length} but text8.context_length is {cfg.text8.context_length}")
    if cfg.sim.skew != 0.0:
        problems.append("sim.skew must be 0 on text8: skew is defined over Task A's maps")
    if cfg.eval.curve_max_chars <= cfg.text8.context_length:
        problems.append("eval.curve_max_chars must be longer than one window")
    for check_fn in (lambda: validate_sim(cfg.sim, cfg.model.n_experts, cfg.model.top_k),
                     lambda: check_schedule(cfg.optim, cfg.sim.rounds * cfg.sim.local_steps),
                     lambda: plan_rounds(cfg)):
        try:
            check_fn()
        except ValueError as exc:
            problems.append(str(exc))
    if problems:
        raise ValueError("inconsistent configuration: " + "; ".join(problems))


def plan_rounds(cfg: SlicedTaskBConfig) -> list[tuple[int, int]]:
    """``(first worker step, local steps)`` of every round; the decay starts where the schedule's decay does."""
    trajectory = cfg.sim.rounds * cfg.sim.local_steps
    return round_plan(cfg.sim, decay_start(cfg.optim, trajectory))


def full_model(cfg: SlicedTaskBConfig, state, device) -> MoETransformer:
    with torch.random.fork_rng(devices=[]):
        model = MoETransformer(cfg.model)
    model.load_state_dict(state, strict=True)
    return model.to(device)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path)
    parser.add_argument("--set", dest="overrides", action="append", default=[], metavar="SECTION.KEY=VALUE")
    parser.add_argument("--resume", type=Path, help="run folder to resume from its last completed round")
    parser.add_argument("--stop-after-round", type=int, default=None, help="stop cleanly after this round (testing)")
    args = parser.parse_args(argv)
    if (args.config is None) == (args.resume is None):
        parser.error("give exactly one of --config or --resume")
    if args.resume is not None and args.overrides:
        parser.error("--set cannot be combined with --resume; a resumed run keeps its configuration")

    config_path = args.config if args.config is not None else args.resume / "config.json"
    cfg = load_config(config_path, SlicedTaskBConfig, args.overrides)
    data = Text8(cfg.text8)
    check(cfg, data)
    sim = cfg.sim
    repro.prepare_process(cfg.run.determinism)  # before any CUDA work
    repro.set_cpu_threads(cfg.run.cpu_threads)
    device = torch.device(cfg.run.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("the configuration asks for 'cuda' but CUDA is not available")
    total_steps = sim.n_workers * sim.local_steps * sim.rounds
    characters_per_step = cfg.optim.batch_size * cfg.optim.grad_accum * cfg.text8.context_length
    plan = plan_rounds(cfg)
    trajectory = sim.rounds * sim.local_steps
    ops_settings, ops_source = load_ops_settings()
    checks = run_preflight(ops_settings, paths.runs_root() if args.resume is None else args.resume,
                           expected_seconds=total_steps * ops_settings.seconds_per_step)
    enforce(checks)

    n_layers, n_experts, top_k = cfg.model.n_layers, cfg.model.n_experts, cfg.model.top_k
    chash = config_hash(cfg)
    outer = make_outer(sim)
    seeds = repro.seed_everything(cfg.run.seed)
    if args.resume is not None:
        log = RunLogger.reopen(args.resume)
        determinism = repro.apply_determinism(cfg.run.determinism)
        start_round, global_state = load_checkpoint(args.resume, chash, outer, device)
        log.write("resume", from_round=start_round, environment=repro.environment_info(),
                  determinism=determinism, git=git_state()[0])
    else:
        log = RunLogger.create(paths.runs_root(), make_run_id(cfg.run.name, cfg.run.seed))
        determinism = repro.apply_determinism(cfg.run.determinism)
        global_state = {k: v.to(device) for k, v in MoETransformer(cfg.model).state_dict().items()}  # same init as centralized
        log.write_header(config=cfg, config_path=config_path, seeds=seeds,
                         environment=repro.environment_info(), determinism=determinism)
        log.write("setup", parameters=count_parameters(MoETransformer(cfg.model)), vocab_size=data.vocab_size,
                  text8_path=str(data.path), text8_sha256=cfg.text8.sha256, worker_steps=total_steps,
                  characters=total_steps * characters_per_step)
        start_round = 0

    batch_size = cfg.optim.batch_size
    stopped = False
    with log:
        try:
            with operations(log, ops_settings, ops_source, checks), log.capture_warnings():
                for r in range(start_round, len(plan)):
                    first_step, local_steps = plan[r]
                    t0 = time.perf_counter()
                    slices = round_slices(sim, n_layers, n_experts, top_k, r, cfg.run.seed)
                    dropped = dropped_workers(sim, r, cfg.run.seed)
                    results, workers = [], []
                    for i, spec in enumerate(worker_specs(sim)):
                        held = {layer: list(e) for layer, e in slices[spec.name].experts.items()}
                        if spec.name in dropped:
                            workers.append({"worker": spec.name, "dropped": True, "held": held})
                            continue
                        generator = data_generator(cfg.run.seed, i, r)

                        def next_batch(generator=generator):
                            return data.sample(batch_size, generator)

                        wr = train_worker(cfg.model, cfg.optim, global_state, slices[spec.name], sim.mode, next_batch,
                                          r, local_steps, trajectory, device, start_step=first_step)
                        workers.append({"worker": spec.name, "dropped": False, "held": held,
                                        "train": dataclasses.asdict(wr.stats)})
                        results.append(WorkerResult(slices[spec.name], wr.state, wr.stats.sequences))
                        del wr
                    global_state, report = merge(global_state, results, sim.router_rule, outer)
                    merged = evaluate_bpc(full_model(cfg, global_state, device), data, "valid", device,
                                          max_chars=cfg.eval.curve_max_chars)
                    seconds = time.perf_counter() - t0
                    log.write("round", round=r, start_step=first_step, local_steps=local_steps, seconds=seconds,
                              dropped=dropped, workers=workers, merge=dataclasses.asdict(report), **merged)
                    save_checkpoint(log.run_dir, r, global_state, outer, chash)
                    print(f"round {r + 1:3d}/{len(plan)}  merged validation bpc {merged['bpc']:.4f}  "
                          f"dropped {len(dropped)}  ({seconds:.0f}s)", flush=True)
                    if args.stop_after_round is not None and r >= args.stop_after_round and r < len(plan) - 1:
                        raise StopAfterRound(r)

                model = full_model(cfg, global_state, device)
                test = evaluate_bpc(model, data, "test", device)
                if cfg.eval.save_model:
                    torch.save(model.state_dict(), log.run_dir / "final_model.pt")
                log.write("final", rounds=len(plan), worker_steps=total_steps,
                          characters=total_steps * characters_per_step, test=test,
                          model_file="final_model.pt" if cfg.eval.save_model else None)
        except StopAfterRound as stop:
            log.close("stopped", after_round=stop.args[0])
            stopped = True

    print(f"run folder: {log.run_dir}")
    if stopped:
        print("stopped after round", args.stop_after_round, "- resume with --resume", log.run_dir)
        return 3
    print(f"test bits per character {test['bpc']:.4f} over {test['scored']:,} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
