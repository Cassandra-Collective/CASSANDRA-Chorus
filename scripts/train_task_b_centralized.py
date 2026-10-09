"""Centralized training on Task B, text8 (PLAN step 10; SRS S0-F-13, S0-F-19, S0-F-20).

Usage, from the repository root (normally through scripts/ops/launch_visible.ps1)::

    python -m scripts.train_task_b_centralized --config configs/task_b/centralized.toml [--set ...]

Trains the full model on random text8 training windows, evaluates bits per
character on the first ``curve_max_chars`` validation characters every
``eval_every`` steps, and at the end on the whole test split (S0-A-04). Saves
the final weights in the run folder. Mirrors scripts/train_task_a_centralized.py;
see docs/implementations/2026-10-09-task-b-runs.md.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
import time
from pathlib import Path

import torch

from cassandra_chorus import paths, repro
from cassandra_chorus.config import RunSection, load_config
from cassandra_chorus.data.text8 import Text8, Text8Section
from cassandra_chorus.metrics.task_b import evaluate_bpc
from cassandra_chorus.model import ModelSection, MoETransformer, count_parameters
from cassandra_chorus.ops import enforce, load_ops_settings, operations, run_preflight
from cassandra_chorus.runlog import RunLogger, make_run_id
from cassandra_chorus.train import OptimSection, check_schedule, make_optimizer, train_steps


@dataclasses.dataclass(frozen=True)
class TrainSection:
    steps: int = 20000
    eval_every: int = 1000
    curve_max_chars: int = 1_000_000
    save_model: bool = True


@dataclasses.dataclass(frozen=True)
class CentralizedTaskBConfig:
    run: RunSection
    model: ModelSection
    text8: Text8Section = dataclasses.field(default_factory=Text8Section)
    optim: OptimSection = dataclasses.field(default_factory=OptimSection)
    train: TrainSection = dataclasses.field(default_factory=TrainSection)


def check_consistency(cfg: CentralizedTaskBConfig, data: Text8) -> None:
    problems = []
    if cfg.model.vocab_size != data.vocab_size:
        problems.append(f"model.vocab_size is {cfg.model.vocab_size} but text8 needs {data.vocab_size}")
    if cfg.model.context_length != cfg.text8.context_length:
        problems.append(f"model.context_length is {cfg.model.context_length} but text8.context_length is {cfg.text8.context_length}")
    if cfg.train.steps < 1 or cfg.train.eval_every < 1 or cfg.train.curve_max_chars <= cfg.text8.context_length:
        problems.append("train.steps and train.eval_every must be positive and curve_max_chars longer than one window")
    else:
        try:
            check_schedule(cfg.optim, cfg.train.steps)
        except ValueError as exc:
            problems.append(str(exc))
    if problems:
        raise ValueError("inconsistent configuration: " + "; ".join(problems))


def resolve_device(name: str) -> torch.device:
    if name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("the configuration asks for 'cuda' but CUDA is not available; set run.device=\"cpu\" deliberately")
    return torch.device(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--set", dest="overrides", action="append", default=[], metavar="SECTION.KEY=VALUE")
    args = parser.parse_args(argv)

    cfg = load_config(args.config, CentralizedTaskBConfig, args.overrides)
    data = Text8(cfg.text8)
    check_consistency(cfg, data)
    repro.prepare_process(cfg.run.determinism)  # before any CUDA work
    repro.set_cpu_threads(cfg.run.cpu_threads)
    device = resolve_device(cfg.run.device)
    ops_settings, ops_source = load_ops_settings()
    checks = run_preflight(ops_settings, paths.runs_root(), expected_seconds=cfg.train.steps * ops_settings.seconds_per_step)
    enforce(checks)

    with RunLogger.create(paths.runs_root(), make_run_id(cfg.run.name, cfg.run.seed)) as log:
        seeds = repro.seed_everything(cfg.run.seed)
        seeds["train_data"] = repro.derive_seed(cfg.run.seed, "task_b/train")
        determinism = repro.apply_determinism(cfg.run.determinism)
        model = MoETransformer(cfg.model).to(device)
        log.write_header(config=cfg, config_path=args.config, seeds=seeds,
                         environment=repro.environment_info(), determinism=determinism)
        log.write("setup", parameters=count_parameters(model), vocab_size=data.vocab_size,
                  text8_path=str(data.path), text8_sha256=cfg.text8.sha256,
                  characters_per_step=cfg.optim.batch_size * cfg.text8.context_length)
        generator = torch.Generator().manual_seed(seeds["train_data"])
        batch_size = cfg.optim.batch_size

        def next_batch():
            return data.sample(batch_size, generator)

        def curve():
            return evaluate_bpc(model, data, "valid", device, max_chars=cfg.train.curve_max_chars)

        optimizer = make_optimizer(model, cfg.optim)
        with operations(log, ops_settings, ops_source, checks), log.capture_warnings():
            step, train_seconds = 0, 0.0
            log.write("eval", step=0, characters=0, **curve())
            while step < cfg.train.steps:
                n = min(cfg.train.eval_every, cfg.train.steps - step)
                if device.type == "cuda":
                    torch.cuda.synchronize()
                t0 = time.perf_counter()
                stats = train_steps(model, optimizer, next_batch, n, cfg.optim, device, start_step=step,
                                    total_steps=cfg.train.steps)
                if device.type == "cuda":
                    torch.cuda.synchronize()
                train_seconds += time.perf_counter() - t0
                step += n
                result = curve()
                log.write("eval", step=step, characters=step * batch_size * cfg.text8.context_length,
                          train=dataclasses.asdict(stats), train_seconds=train_seconds, **result)
                print(f"step {step:6d}  train ce {stats.mean_ce_loss:.4f}  validation bpc {result['bpc']:.4f}  "
                      f"({train_seconds:.0f}s)", flush=True)
            test = evaluate_bpc(model, data, "test", device)
            if cfg.train.save_model:
                torch.save(model.state_dict(), log.run_dir / "final_model.pt")
            log.write("final", step=step, characters=step * batch_size * cfg.text8.context_length,
                      train_seconds=train_seconds, test=test,
                      model_file="final_model.pt" if cfg.train.save_model else None)

    print(f"run folder: {log.run_dir}")
    print(f"test bits per character {test['bpc']:.4f} over {test['scored']:,} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
