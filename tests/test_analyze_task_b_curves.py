from __future__ import annotations

import json

import pytest

from scripts.analyze_task_b import collect
from scripts.analyze_task_b_curves import centralized_curve, curves_by_seed, main, mean_over_seeds, pair, simulated_curve

COUNTS = [[250] * 8 for _ in range(6)]
SIM = {"n_workers": 4, "local_steps": 125}


def write_run(root, name, seed, curve, sim=True):
    """A completed run whose validation curve is ``curve``: ``{step: bpc}`` (centralized) or ``{round: bpc}``."""
    run_id = f"2026T{seed}_{name}_s{seed}"
    d = root / run_id
    d.mkdir(parents=True)
    config = {"run": {"name": name, "seed": seed}}
    if sim:
        config["sim"] = SIM
        points = [{"type": "round", "round": r, "bpc": b} for r, b in curve.items()]
    else:
        points = [{"type": "eval", "step": s, "bpc": b} for s, b in curve.items()]
    recs = [{"type": "header", "run_id": run_id, "config": config, "git": {"commit": "abc", "dirty": False}},
            *points,
            {"type": "final", "test": {"bpc": 1.5, "expert_counts": COUNTS}},
            {"type": "end", "status": "completed"}]
    (d / "log.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return d


def test_simulated_steps_are_total_worker_steps_after_each_round():
    recs = [{"type": "header", "config": {"sim": SIM}}, {"type": "round", "round": 0, "bpc": 3.0},
            {"type": "round", "round": 1, "bpc": 2.0}, {"type": "round", "round": 39, "bpc": 1.5}]
    assert simulated_curve(recs) == {500: 3.0, 1000: 2.0, 20000: 1.5}


def test_centralized_curve_reads_eval_steps():
    recs = [{"type": "eval", "step": 0, "bpc": 4.9}, {"type": "eval", "step": 1000, "bpc": 2.1}, {"type": "power"}]
    assert centralized_curve(recs) == {0: 4.9, 1000: 2.1}


def test_pairing_uses_equal_compute_and_skips_step_zero_and_unmatched_steps():
    central = {0: 4.9, 1000: 2.0, 2000: 1.8, 3000: 1.7}
    arms = {"full": {500: 2.5, 1000: 2.2, 2000: 1.89}, "sliced": {1000: 2.4, 2000: 1.98}}
    rows = pair(central, arms)
    assert [r["step"] for r in rows] == [1000, 2000]  # 3000 is missing from the arms; 0 is the untrained model
    assert rows[0]["full_gap"] == pytest.approx(0.1)
    assert rows[1]["sliced_gap"] == pytest.approx(0.1)


def test_end_to_end_pairs_rounds_with_centralized_steps_and_averages_seeds(tmp_path):
    for seed, scale in ((7, 1.10), (11, 1.20)):
        write_run(tmp_path, "taskB-central", seed, {0: 5.0, 1000: 2.0, 2000: 1.5}, sim=False)
        write_run(tmp_path, "taskB-fullavg", seed, {0: 2.6, 1: 2.0 * scale, 3: 1.5 * scale})
    rows = collect(tmp_path.iterdir())
    per_seed = curves_by_seed(rows, tmp_path)
    assert [r["step"] for r in per_seed[7]] == [1000, 2000]  # rounds 1 and 3 used 1,000 and 2,000 worker steps
    means = mean_over_seeds(per_seed)
    m, lo, hi, n = means[0]["full"]
    assert (m, lo, hi, n) == (pytest.approx(0.15), pytest.approx(0.10), pytest.approx(0.20), 2)
    out = tmp_path / "report.md"
    assert main(["--runs-dir", str(tmp_path), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "| 1,000 | 50% | +15.0 (+10.0 to +20.0)" in text
