from __future__ import annotations

import json

from scripts.ops import continue_queue
from scripts.ops.run_queue import load_queue
from cassandra_chorus.paths import REPO_ROOT

MATRIX = REPO_ROOT / "configs" / "queues" / "task_b_matrix.toml"


def make_run(runs, run_id, status=None, checkpoint=False, broken_tail=False):
    d = runs / run_id
    d.mkdir(parents=True)
    lines = [json.dumps({"type": "header", "run_id": run_id})]
    if status:
        lines.append(json.dumps({"type": "end", "status": status}))
    text = "\n".join(lines) + "\n" + ('{"type": "rou' if broken_tail else "")
    (d / "log.jsonl").write_text(text, encoding="utf-8")
    if checkpoint:
        (d / "checkpoint.pt").write_bytes(b"x")
    return d


def test_identity_reads_config_and_overrides():
    entries, _ = load_queue(MATRIX)
    assert continue_queue.entry_identity(entries[0]) == ("taskB-central", 7)
    assert continue_queue.entry_identity(entries[1]) == ("taskB-sliced-coverage", 7)
    assert continue_queue.entry_identity(entries[2]) == ("taskB-partial", 7)
    assert continue_queue.entry_identity(entries[11]) == ("taskB-fullavg", 19)


def test_plan_skips_completed_resumes_checkpointed_and_reruns_the_rest(tmp_path):
    entries, _ = load_queue(MATRIX)
    make_run(tmp_path, "20261009T060425Z_taskB-central_s7", "completed")
    make_run(tmp_path, "20261009T194909Z_taskB-sliced-coverage_s7", "completed")
    make_run(tmp_path, "20261009T220408Z_taskB-partial_s7", "completed")
    fullavg = make_run(tmp_path, "20261010T002852Z_taskB-fullavg_s7", checkpoint=True, broken_tail=True)  # killed mid-write
    make_run(tmp_path, "20261010T120000Z_taskB-central_s11")  # centralized, killed: cannot resume
    make_run(tmp_path, "20261010T050539Z_taskB-learncheck_s7", "completed")  # another name: ignored
    steps = continue_queue.plan(entries, tmp_path)
    actions = [a for a, _, _ in steps]
    assert actions == ["skip", "skip", "skip", "resume"] + ["run"] * 8
    assert steps[3][1] == {"module": "scripts.train_task_b_sliced", "args": ["--resume", fullavg.as_posix()]}
    assert "unfinished folders left as they are: 20261010T120000Z_taskB-central_s11" in steps[4][2]
    assert steps[4][1] is entries[4]  # rerun with its original arguments


def test_a_stopped_run_without_checkpoint_is_rerun_and_the_newest_checkpoint_resumed(tmp_path):
    entries, _ = load_queue(MATRIX)
    make_run(tmp_path, "20261010T010000Z_taskB-sliced-coverage_s7", "stopped", checkpoint=True)
    newer = make_run(tmp_path, "20261010T020000Z_taskB-sliced-coverage_s7", checkpoint=True)
    steps = continue_queue.plan(entries[:2], tmp_path)
    assert [a for a, _, _ in steps] == ["run", "resume"]
    assert steps[1][1]["args"] == ["--resume", newer.as_posix()]


def test_written_queue_runs_only_the_remaining_entries(tmp_path):
    entries, _ = load_queue(MATRIX)
    make_run(tmp_path, "20261009T060425Z_taskB-central_s7", "completed")
    steps = continue_queue.plan(entries[:2], tmp_path)
    path = tmp_path / "q.toml"
    path.write_text(continue_queue.toml_queue(steps, MATRIX), encoding="utf-8")
    runs, stop = load_queue(path)
    assert stop is False and runs == [entries[1]]
