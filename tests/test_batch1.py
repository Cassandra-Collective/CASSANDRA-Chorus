"""PLAN step 11, batch 1: gradient accumulation, per-step losses, the round plan, sliding-window scoring.

See docs/implementations/2026-10-13-averaging-gap-batch-1.md.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest
import torch

from cassandra_chorus.data.text8 import Text8, Text8Section
from cassandra_chorus.metrics.task_b import evaluate_bpc
from cassandra_chorus.model import ModelSection, MoETransformer
from cassandra_chorus.paths import DATA_DIR_ENV, REPO_ROOT, RUNS_DIR_ENV
from cassandra_chorus.sim import SimSection, round_plan, validate_sim
from cassandra_chorus.train import OptimSection, check_schedule, make_optimizer, train_steps
from scripts.analyze_task_b_curves import simulated_curve
from test_task_b_scripts import TEXT, TINY_MODEL, corpus, records, run  # noqa: F401  (corpus is a fixture)

TINY = ModelSection(vocab_size=27, context_length=16, d_model=32, n_layers=2, n_heads=2, expert_hidden=32,
                    balance_coef=0.0, dispatch="dense")


def tiny_model(seed=0, cfg=TINY):
    torch.manual_seed(seed)
    return MoETransformer(cfg)


def batches(n_rows, seed=1):
    g = torch.Generator().manual_seed(seed)
    x = torch.randint(0, 27, (n_rows, 17), generator=g)
    return x[:, :-1], x[:, 1:]


# ---------------------------------------------------------------------------
# Gradient accumulation and per-step losses


def one_step(model, optim_cfg, feeds):
    feeds = iter(feeds)
    opt = make_optimizer(model, optim_cfg)
    return train_steps(model, opt, lambda: next(feeds), 1, optim_cfg, "cpu")


def grads(model):
    """The gradients left by the last step (after clipping); ``train_steps`` clears them only at the next step."""
    return [torch.zeros_like(p) if p.grad is None else p.grad.clone() for p in model.parameters()]


def test_accumulating_four_quarter_batches_matches_one_full_batch_without_balance_loss():
    inputs, targets = batches(32)
    a, b = tiny_model(), tiny_model()
    full = OptimSection(batch_size=32, warmup_steps=0)
    accum = dataclasses.replace(full, batch_size=8, grad_accum=4)
    stats_full = one_step(a, full, [(inputs, targets)])
    stats_acc = one_step(b, accum, [(inputs[i:i + 8], targets[i:i + 8]) for i in range(0, 32, 8)])
    for g, h in zip(grads(a), grads(b), strict=True):
        torch.testing.assert_close(g, h, rtol=1e-4, atol=1e-7)
    assert stats_acc.sequences == stats_full.sequences == 32
    assert stats_acc.scored_targets == stats_full.scored_targets == 32 * 16
    assert stats_acc.mean_loss == pytest.approx(stats_full.mean_loss, rel=1e-5)


def test_accumulation_with_the_balance_loss_differs_only_slightly():
    cfg = dataclasses.replace(TINY, balance_coef=0.01)
    inputs, targets = batches(32)
    a, b = tiny_model(cfg=cfg), tiny_model(cfg=cfg)
    full = OptimSection(batch_size=32, warmup_steps=0)
    one_step(a, full, [(inputs, targets)])
    one_step(b, dataclasses.replace(full, batch_size=8, grad_accum=4),
             [(inputs[i:i + 8], targets[i:i + 8]) for i in range(0, 32, 8)])
    worst = max((g - h).abs().max().item() for g, h in zip(grads(a), grads(b), strict=True))
    largest = max(g.abs().max().item() for g in grads(a))
    assert 0.0 < worst < 0.01 * largest  # per-micro-batch balance statistics are not the full batch's


def test_step_losses_are_recorded_only_when_asked():
    inputs, targets = batches(8)
    on = OptimSection(batch_size=8, warmup_steps=0, log_step_losses=True)
    model = tiny_model()
    stats = train_steps(model, make_optimizer(model, on), lambda: (inputs, targets), 3, on, "cpu")
    assert len(stats.step_losses) == 3 and all(math.isfinite(v) for v in stats.step_losses)
    assert stats.mean_loss == pytest.approx(sum(stats.step_losses) / 3)
    off = dataclasses.replace(on, log_step_losses=False)
    model = tiny_model()
    assert train_steps(model, make_optimizer(model, off), lambda: (inputs, targets), 1, off, "cpu").step_losses is None


def test_schedule_check_rejects_no_accumulation_steps():
    with pytest.raises(ValueError, match="grad_accum"):
        check_schedule(OptimSection(grad_accum=0), 100)


# ---------------------------------------------------------------------------
# Round plan


def test_round_plan_without_decay_phase_is_unchanged():
    sim = SimSection(local_steps=125, rounds=40, equal_compute_steps=20000)
    assert round_plan(sim, 4000) == [(r * 125, 125) for r in range(40)]


def test_round_plan_with_a_shorter_h_during_the_decay():
    sim = SimSection(local_steps=125, rounds=40, equal_compute_steps=20000, decay_local_steps=25)
    plan = round_plan(sim, 4000)
    assert len(plan) == 32 + 40
    assert plan[0] == (0, 125) and plan[31] == (3875, 125) and plan[32] == (4000, 25) and plan[-1] == (4975, 25)
    assert sum(steps for _, steps in plan) == 5000  # equal compute is kept
    assert all(first == prev_first + prev_steps for (prev_first, prev_steps), (first, _) in zip(plan, plan[1:]))


def test_round_plan_refuses_phases_that_do_not_divide():
    with pytest.raises(ValueError, match="cannot split"):
        round_plan(SimSection(local_steps=125, rounds=40, decay_local_steps=30), 4000)
    with pytest.raises(ValueError, match="cannot split"):
        round_plan(SimSection(local_steps=150, rounds=40, decay_local_steps=25), 4000)
    with pytest.raises(ValueError, match="decay_local_steps"):
        validate_sim(SimSection(decay_local_steps=-1, rounds=10), 8, 2)


def test_curve_analysis_uses_logged_round_steps():
    recs = [{"type": "header", "config": {"sim": {"n_workers": 4, "local_steps": 125}}},
            {"type": "round", "round": 31, "start_step": 3875, "local_steps": 125, "bpc": 1.6},
            {"type": "round", "round": 32, "start_step": 4000, "local_steps": 25, "bpc": 1.59}]
    assert simulated_curve(recs) == {16000: 1.6, 16100: 1.59}


# ---------------------------------------------------------------------------
# Sliding-window scoring


@pytest.fixture
def tiny_text8(tmp_path):
    (tmp_path / "text8").mkdir()
    (tmp_path / "text8" / "text8").write_bytes(TEXT.encode("ascii"))
    cfg = Text8Section(sha256=hashlib.sha256(TEXT.encode("ascii")).hexdigest(), total=20000, train_end=16000,
                       valid_end=18000, context_length=16)
    return Text8(cfg, data_dir=tmp_path)


def test_stride_equal_to_the_context_is_the_original_protocol(tiny_text8):
    model = tiny_model()
    original = evaluate_bpc(model, tiny_text8, "test", "cpu")
    same = evaluate_bpc(model, tiny_text8, "test", "cpu", stride=16)
    assert same == original


@pytest.mark.parametrize("stride", [1, 4, 8])
def test_sliding_windows_score_exactly_the_original_characters(tiny_text8, stride):
    class Uniform(torch.nn.Module):  # every position costs ln 27, so bpc reveals any miscount
        def forward(self, inputs):
            return SimpleNamespace(logits=torch.zeros(*inputs.shape, 27))

    original = evaluate_bpc(Uniform(), tiny_text8, "test", "cpu")
    sliding = evaluate_bpc(Uniform(), tiny_text8, "test", "cpu", stride=stride)
    assert sliding["scored"] == original["scored"] == ((2000 - 1) // 16) * 16
    assert sliding["bpc"] == pytest.approx(math.log2(27)) and sliding["stride"] == stride
    assert "expert_counts" not in sliding


def test_sliding_windows_give_a_real_model_more_context(tiny_text8):
    model = tiny_model()
    original = evaluate_bpc(model, tiny_text8, "test", "cpu")
    sliding = evaluate_bpc(model, tiny_text8, "test", "cpu", stride=4)
    assert sliding["scored"] == original["scored"] and sliding["bpc"] != original["bpc"]


def test_strides_that_do_not_divide_the_context_are_refused(tiny_text8):
    with pytest.raises(ValueError, match="stride"):
        evaluate_bpc(tiny_model(), tiny_text8, "test", "cpu", stride=5)


# ---------------------------------------------------------------------------
# End to end through the scripts (CPU, tiny model)


def test_centralized_task_b_with_accumulation_logs_the_effective_batch(corpus):
    tmp_path, data_overrides = corpus
    overrides = ['run.device="cpu"', "run.name=central-accum-test", *TINY_MODEL, *data_overrides, "train.steps=4",
                 "train.eval_every=2", "train.curve_max_chars=500", "optim.batch_size=4", "optim.warmup_steps=1",
                 "optim.grad_accum=2", "optim.log_step_losses=true"]
    runs = run("scripts.train_task_b_centralized", "configs/task_b/centralized.toml", overrides, tmp_path)
    (run_dir,) = list(runs.iterdir())
    recs = records(run_dir)
    evals = [r for r in recs if r["type"] == "eval" and r["step"] > 0]
    assert [r["train"]["sequences"] for r in evals] == [2 * 4 * 2, 2 * 4 * 2]
    assert all(len(r["train"]["step_losses"]) == 2 for r in evals)
    (final,) = [r for r in recs if r["type"] == "final"]
    assert final["characters"] == 4 * 4 * 2 * 16


def test_simulated_task_b_with_a_shorter_h_during_the_decay(corpus):
    tmp_path, data_overrides = corpus
    # Trajectory 5 x 2 = 10 worker steps; the decay (last 20%) starts at step 8: rounds of 2, then of 1.
    overrides = ['run.device="cpu"', "run.name=sim-decay-test", *TINY_MODEL, *data_overrides, "sim.mode=full",
                 "sim.router_rule=all", "sim.local_steps=2", "sim.rounds=5", "sim.equal_compute_steps=40",
                 "sim.decay_local_steps=1", "eval.curve_max_chars=500", "optim.batch_size=4", "optim.warmup_steps=2",
                 "optim.log_step_losses=true"]
    runs = run("scripts.train_task_b_sliced", "configs/task_b/sliced.toml", overrides, tmp_path)
    (run_dir,) = list(runs.iterdir())
    rounds = [r for r in records(run_dir) if r["type"] == "round"]
    assert [(r["start_step"], r["local_steps"]) for r in rounds] == [(0, 2), (2, 2), (4, 2), (6, 2), (8, 1), (9, 1)]
    assert all(len(w["train"]["step_losses"]) == r["local_steps"] for r in rounds for w in r["workers"])
    (final,) = [r for r in records(run_dir) if r["type"] == "final"]
    assert final["rounds"] == 6 and final["worker_steps"] == 40


def test_task_a_refuses_the_task_b_only_options(tmp_path):
    env = {**os.environ, RUNS_DIR_ENV: str(tmp_path / "runs"), DATA_DIR_ENV: str(tmp_path)}
    for option in ("sim.decay_local_steps=1", "optim.grad_accum=2"):
        result = subprocess.run([sys.executable, "-m", "scripts.train_task_a_sliced", "--config",
                                 "configs/task_a/sliced.toml", "--set", 'run.device="cpu"', "--set", option],
                                cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=300)
        assert result.returncode != 0 and "only supported on Task B" in result.stderr


def test_rescoring_reproduces_the_logged_score_and_resumes(corpus, monkeypatch):
    import json

    from scripts.rescore_task_b import main as rescore

    tmp_path, data_overrides = corpus
    overrides = ['run.device="cpu"', "run.name=taskB-central", "run.seed=7", *TINY_MODEL, *data_overrides,
                 "train.steps=4", "train.eval_every=2", "train.curve_max_chars=500", "optim.batch_size=4",
                 "optim.warmup_steps=1"]
    runs = run("scripts.train_task_b_centralized", "configs/task_b/centralized.toml", overrides, tmp_path)
    out_json, out_md = tmp_path / "rescore.json", tmp_path / "rescore.md"
    monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path / "data"))
    args = ["--runs-dir", str(runs), "--device", "cpu", "--stride", "4", "--json", str(out_json), "--out", str(out_md)]
    assert rescore(args) == 0
    (result,) = json.loads(out_json.read_text(encoding="utf-8")).values()
    assert result["original_bpc"] == pytest.approx(result["logged_bpc"], abs=1e-6)
    assert result["sliding_bpc"] != result["original_bpc"] and result["seed"] == 7
    first = out_json.read_text(encoding="utf-8")
    assert rescore(args) == 0  # nothing left to score: the stored result is kept as it is
    assert out_json.read_text(encoding="utf-8") == first
    assert "| Centralized | 7 |" in out_md.read_text(encoding="utf-8")
