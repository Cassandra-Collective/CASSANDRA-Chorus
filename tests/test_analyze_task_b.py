from __future__ import annotations

import json

import pytest

from scripts.analyze_task_b import AmbiguousRunsError, collect, evaluate, main, run_row

COUNTS = [[250] * 8 for _ in range(6)]  # 1,000 tokens x k = 2 per layer, perfectly balanced
BPC = {"taskB-central": 1.44, "taskB-fullavg": 1.53, "taskB-partial": 1.55, "taskB-sliced-coverage": 1.60}


def write_run(root, name, seed, bpc=None, status="completed", run_id=None, counts=None, resumed=False):
    run_id = run_id or f"2026T{seed}_{name}_s{seed}"
    d = root / run_id
    d.mkdir(parents=True)
    recs = [{"type": "header", "run_id": run_id, "config": {"run": {"name": name, "seed": seed}},
             "git": {"commit": "abcdef1234", "dirty": False}},
            {"type": "eval", "step": 20000, "bpc": 1.3},
            *([{"type": "resume", "from_round": 20}] if resumed else []),
            {"type": "final", "test": {"bpc": BPC[name] if bpc is None else bpc, "expert_counts": counts or COUNTS}},
            {"type": "end", "status": status}]
    (d / "log.jsonl").write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return d


def matrix(root, seeds=(7, 11, 19)):
    for s in seeds:
        for name in BPC:
            write_run(root, name, s)


def test_full_matrix_fails_s0_a_04_and_decomposes_exactly(tmp_path):
    matrix(tmp_path)
    result = evaluate(collect(tmp_path.iterdir()))
    assert result["overall"] == "fail"
    p = result["per_seed"][7]
    assert p["gaps"]["sliced"] == pytest.approx((1.60 - 1.44) / 1.44)
    assert sum(p["steps"].values()) == pytest.approx(p["gaps"]["sliced"])  # the steps sum to the sliced gap
    assert p["steps"]["local averaging"] == pytest.approx(0.09 / 1.44)
    assert p["steps"]["masked routing"] == pytest.approx(0.05 / 1.44)


def test_pass_needs_every_seed(tmp_path):
    for s in (7, 11, 19):
        write_run(tmp_path, "taskB-central", s, bpc=1.44)
        write_run(tmp_path, "taskB-sliced-coverage", s, bpc=1.50 if s != 19 else 1.52)  # 4.2% and 5.6%
    result = evaluate(collect(tmp_path.iterdir()))
    assert [result["per_seed"][s]["verdict"] for s in (7, 11, 19)] == ["pass", "pass", "fail"]
    assert result["overall"] == "fail"


def test_missing_runs_are_incomplete_not_pass(tmp_path):
    for s in (7, 11):
        write_run(tmp_path, "taskB-central", s, bpc=1.44)
        write_run(tmp_path, "taskB-sliced-coverage", s, bpc=1.45)
    result = evaluate(collect(tmp_path.iterdir()))
    assert result["per_seed"][19]["verdict"] == "missing" and result["overall"] == "incomplete"


def test_selection_ignores_unfinished_and_other_names_and_refuses_duplicates(tmp_path):
    write_run(tmp_path, "taskB-central", 7, status="stopped", run_id="a_stopped")
    d = tmp_path / "b_nofinal"
    d.mkdir()
    (d / "log.jsonl").write_text(json.dumps({"type": "header", "run_id": "b", "config": {"run": {"name": "taskB-central", "seed": 7}}}) + "\n", encoding="utf-8")
    write_run(tmp_path, "taskB-central", 7, run_id="c_done")
    assert list(collect(tmp_path.iterdir())) == [("centralized", 7)]
    write_run(tmp_path, "taskB-central", 7, run_id="d_again")
    with pytest.raises(AmbiguousRunsError, match="c_done"):
        collect(tmp_path.iterdir())


def test_row_reports_usage_and_resumes(tmp_path):
    starved = [[400, 400, 400, 400, 200, 176, 24, 0]] + [[250] * 8] * 5
    row = run_row(write_run(tmp_path, "taskB-fullavg", 7, counts=starved, resumed=True))
    assert row.negligible == 2 and row.least_share == 0.0 and row.resumes == 1


def test_report_is_written(tmp_path):
    runs, out = tmp_path / "runs", tmp_path / "report.md"
    matrix(runs)
    assert main(["--runs-dir", str(runs), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "## S0-A-04 for the sliced arm: FAIL" in text and "| masked routing |" in text
    assert "PLAN leaves \"moderate\" and \"large\" undefined" in text
