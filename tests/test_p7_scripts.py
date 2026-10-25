"""Tiny CPU pipelines and original-loop regression; these are not P7 runs."""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys

import pytest
import torch

from cassandra_chorus import repro
from cassandra_chorus.config import load_config
from cassandra_chorus.coordinator import WorkerResult, merge
from cassandra_chorus.data.text8 import Text8
from cassandra_chorus.model import MoETransformer
from cassandra_chorus.paths import DATA_DIR_ENV, REPO_ROOT, RUNS_DIR_ENV
from cassandra_chorus.sim import data_generator, dropped_workers, make_outer, round_slices, train_worker, worker_specs
from scripts.train_task_b_sliced import SlicedTaskBConfig, plan_rounds
from test_task_b_scripts import corpus, records, run, TINY_MODEL  # noqa: F401


@pytest.mark.parametrize("extra", [[], ["sim.outer=nesterov"], ["sim.drop_prob=0.5"],
                                   ["sim.mode=partial", "sim.router_rule=all"],
                                   ["sim.mode=full", "sim.router_rule=all"]])
def test_features_off_matches_original_round_loop_bit_for_bit(corpus, monkeypatch, extra, restore_torch_determinism):
    tmp_path, data_overrides = corpus
    overrides = ['run.device="cpu"', "run.name=p7-legacy-regression", *TINY_MODEL, *data_overrides,
                 "sim.local_steps=1", "sim.rounds=2", "sim.equal_compute_steps=8", "eval.curve_max_chars=100",
                 "optim.batch_size=2", "optim.warmup_steps=1", *extra]
    runs = run("scripts.train_task_b_sliced", "configs/task_b/sliced.toml", overrides, tmp_path)
    (run_dir,) = list(runs.iterdir())
    actual = torch.load(run_dir / "checkpoint.pt", map_location="cpu", weights_only=True)
    cfg = load_config(REPO_ROOT / "configs/task_b/sliced.toml", SlicedTaskBConfig, overrides)
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path / "data"))
    data = Text8(cfg.text8)
    repro.set_cpu_threads(cfg.run.cpu_threads)
    repro.seed_everything(cfg.run.seed)
    repro.apply_determinism(cfg.run.determinism)
    current = {k: v.clone() for k, v in MoETransformer(cfg.model).state_dict().items()}
    outer = make_outer(cfg.sim)
    # Original a30dd6a round loop, kept independent of every new P7 helper.
    for r, (first_step, local_steps) in enumerate(plan_rounds(cfg)):
        assigned = round_slices(cfg.sim, cfg.model.n_layers, cfg.model.n_experts, cfg.model.top_k, r, cfg.run.seed)
        dropped = dropped_workers(cfg.sim, r, cfg.run.seed)
        results = []
        for i, spec in enumerate(worker_specs(cfg.sim)):
            if spec.name in dropped:
                continue
            generator = data_generator(cfg.run.seed, i, r)

            def next_batch(generator=generator):
                return data.sample(cfg.optim.batch_size, generator)

            wr = train_worker(cfg.model, cfg.optim, current, assigned[spec.name], cfg.sim.mode, next_batch,
                              r, local_steps, cfg.sim.rounds * cfg.sim.local_steps, "cpu", start_step=first_step)
            results.append(WorkerResult(assigned[spec.name], wr.state, wr.stats.sequences))
        current, _ = merge(current, results, cfg.sim.router_rule, outer)
    assert actual["global_state"].keys() == current.keys()
    assert all(torch.equal(actual["global_state"][k], current[k]) for k in current)
    if cfg.sim.outer == "nesterov":
        assert actual["outer_velocity"].keys() == outer.velocity.keys()
        assert all(torch.equal(actual["outer_velocity"][k], outer.velocity[k]) for k in outer.velocity)
    assert "simulation" not in actual


def assert_same_tree(a, b):
    """Assert equality of nested checkpoint state, including tensor bits."""
    if isinstance(a, torch.Tensor):
        assert torch.equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            assert_same_tree(a[key], b[key])
    elif isinstance(a, (tuple, list)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            assert_same_tree(x, y)
    else:
        assert a == b


@pytest.mark.parametrize("mode, outer", [("deadline", "plain"), ("deadline", "nesterov"),
                                         ("synchronous", "plain"), ("centralized", "plain")])
def test_p7_cpu_pipeline_and_resume_use_saved_tape(corpus, mode, outer):
    tmp_path, data_overrides = corpus
    tape = tmp_path / "churn.toml"
    tape.write_text('[[event]]\nround=1\nat=0.0\nworker="w0"\naction="depart"\n'
                    '[[event]]\nround=2\nat=0.0\nworker="w0"\naction="arrive"\n'
                    '[[holder_drop]]\nround=0\nat=1.0\nlayer=0\nexpert=0\nremaining=1\n'
                    '[[holder_drop]]\nround=1\nat=1.0\nlayer=0\nexpert=0\nremaining=0\n', encoding="utf-8")
    digest = hashlib.sha256(tape.read_bytes()).hexdigest()
    overrides = ['run.device="cpu"', *TINY_MODEL, *data_overrides, "model.n_experts=4",
                 "sim.n_workers=3", "sim.capacities=[3,3,2]", "sim.local_steps=2", "sim.rounds=3",
                 "sim.equal_compute_steps=18", "sim.policy=rolling", f"sim.round_mode={mode}", f"sim.outer={outer}",
                 "sim.deadline=2.0", "sim.round_length=4.0", "sim.grace=1.0", "sim.sync_timeout=4.0",
                 "sim.speed_min=1.0", "sim.speed_max=1.0", "sim.upload_min=0.0", "sim.upload_max=0.0",
                 f'sim.churn_file="{tape.as_posix()}"', f'sim.churn_sha256="{digest}"', "sim.holder_quality=true",
                 "eval.curve_max_chars=100", "optim.batch_size=2", "optim.warmup_steps=1"]
    runs = run("scripts.train_task_b_sliced", "configs/task_b/sliced.toml", overrides + ["run.name=p7-whole"], tmp_path)
    (whole_dir,) = list(runs.iterdir())
    args = [sys.executable, "-m", "scripts.train_task_b_sliced", "--config", "configs/task_b/sliced.toml",
            "--stop-after-round", "0"]
    for setting in overrides + ["run.name=p7-resumed"]:
        args += ["--set", setting]
    env = {**os.environ, RUNS_DIR_ENV: str(runs), DATA_DIR_ENV: str(tmp_path / "data")}
    result = subprocess.run(args, cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=180)
    assert result.returncode == 3, result.stderr
    (split_dir,) = [p for p in runs.iterdir() if "p7-resumed" in p.name]
    # Resume must use the verified snapshot even when the original tape changes.
    tape.write_text("version=2\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "scripts.train_task_b_sliced", "--resume", str(split_dir)],
                            cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stderr
    whole = torch.load(whole_dir / "checkpoint.pt", weights_only=True)
    split = torch.load(split_dir / "checkpoint.pt", weights_only=True)
    for key in ("global_state", "outer_velocity", "simulation"):
        assert_same_tree(whole[key], split[key])
    rounds = [r for r in records(whole_dir) if r["type"] == "round"]
    resumed_rounds = [r for r in records(split_dir) if r["type"] == "round"]
    for a, b in zip(rounds, resumed_rounds):
        for key in ("bpc", "timing", "holder_quality", "cumulative_steps_run", "cumulative_steps_merged"):
            assert a[key] == b[key]
    assert len(rounds) == len(resumed_rounds) == 3
    assert rounds[0]["timing"]["intervention_holders"]["0"][0] == 1
    assert rounds[1]["timing"]["intervention_holders"]["0"][0] == 0
    assert rounds[0]["steps_run"] > 0
    final = next(r for r in records(whole_dir) if r["type"] == "final")
    assert final["worker_steps"] == sum(r["steps_run"] for r in rounds)
    assert final["steps_merged"] == sum(r["steps_merged"] for r in rounds)
    assert final["characters"] == final["tokens_run"] == final["steps_run"] * 2 * 16
    if mode == "centralized":
        assert final["steps_merged"] == final["steps_run"]
    else:
        assert final["steps_merged"] < final["steps_run"]
        assert any(r["holder_quality"] for r in rounds)

    # A changed saved tape is rejected instead of changing a resumed experiment.
    (split_dir / "churn.toml").write_text("version=2\n", encoding="utf-8")
    refused = subprocess.run([sys.executable, "-m", "scripts.train_task_b_sliced", "--resume", str(split_dir)],
                             cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=180)
    assert refused.returncode != 0 and "SHA-256" in refused.stderr
