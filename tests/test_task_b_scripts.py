from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import pytest

from cassandra_chorus.paths import DATA_DIR_ENV, REPO_ROOT, RUNS_DIR_ENV

TEXT = ("the quick brown fox jumps over the lazy dog and runs " * 400)[:20000]  # 20,000 characters, 27 symbols
TINY_MODEL = ["model.d_model=32", "model.n_heads=2", "model.n_layers=2", "model.expert_hidden=32",
              "model.context_length=16"]


@pytest.fixture
def corpus(tmp_path):
    (tmp_path / "data" / "text8").mkdir(parents=True)
    (tmp_path / "data" / "text8" / "text8").write_bytes(TEXT.encode("ascii"))
    overrides = [f'text8.sha256="{hashlib.sha256(TEXT.encode("ascii")).hexdigest()}"', "text8.total=20000",
                 "text8.train_end=16000", "text8.valid_end=18000", "text8.context_length=16"]
    return tmp_path, overrides


def run(module, config, overrides, tmp_path, extra_args=()):
    args = [sys.executable, "-m", module, "--config", config, *extra_args]
    for o in overrides:
        args += ["--set", o]
    runs = tmp_path / "runs"
    runs.mkdir(exist_ok=True)
    env = {**os.environ, RUNS_DIR_ENV: str(runs), DATA_DIR_ENV: str(tmp_path / "data")}
    result = subprocess.run(args, cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert result.returncode == 0, result.stderr
    return runs


def records(run_dir):
    return [json.loads(line) for line in (run_dir / "log.jsonl").read_text(encoding="utf-8").splitlines()]


def test_centralized_task_b_end_to_end_on_cpu(corpus):
    tmp_path, data_overrides = corpus
    overrides = ['run.device="cpu"', "run.name=central-b-test", *TINY_MODEL, *data_overrides, "train.steps=6",
                 "train.eval_every=3", "train.curve_max_chars=500", "optim.batch_size=4", "optim.warmup_steps=2"]
    runs = run("scripts.train_task_b_centralized", "configs/task_b/centralized.toml", overrides, tmp_path)
    (run_dir,) = list(runs.iterdir())
    recs = records(run_dir)
    assert [r["type"] for r in recs][:2] == ["header", "setup"] and recs[-1]["status"] == "completed"
    evals = [r for r in recs if r["type"] == "eval"]
    assert [r["step"] for r in evals] == [0, 3, 6]
    assert evals[0]["windows"] == (500 - 1) // 16 and len(evals[0]["expert_counts"]) == 2
    (final,) = [r for r in recs if r["type"] == "final"]
    assert final["test"]["windows"] == (2000 - 1) // 16 and final["test"]["bpc"] > 0
    assert final["characters"] == 6 * 4 * 16
    assert (run_dir / "final_model.pt").exists()


def test_task_b_configs_match_the_owner_decisions():
    from cassandra_chorus.config import load_config
    from scripts.train_task_b_centralized import CentralizedTaskBConfig

    cfg = load_config(REPO_ROOT / "configs" / "task_b" / "centralized.toml", CentralizedTaskBConfig)
    from cassandra_chorus.model import MoETransformer, count_parameters

    assert count_parameters(MoETransformer(cfg.model))["total"] == 46_050_432  # D26
    assert (cfg.train.steps, cfg.optim.batch_size, cfg.text8.context_length) == (20000, 32, 256)  # D26
    assert (cfg.model.attention, cfg.model.dispatch) == ("explicit", "sparse")  # owner decisions 2026-10-09, 2026-10-07
    assert (cfg.optim.lr, cfg.optim.decay_fraction, cfg.optim.final_lr_ratio) == (1e-3, 0.2, 0.1)  # Task A's optimizer
