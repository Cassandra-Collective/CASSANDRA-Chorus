"""P5: a week at the planned commit rate (docs/implementations/2026-10-14-solo-prototypes.md).

Simulates one run's commit traffic on the Hub from one account:

* 30-minute rounds (48 a day) for 7 days;
* per round, in order: one 1 MB update commit to each of 5 member
  repositories (``<org>/proto-p5-m0`` to ``m4``), then 7 commits to the log
  repository (``<org>/proto-p5-log``): one combined entry per member, a close
  entry and a checkpoint pointer, each with ``parent_commit``;
* steps about 10 s apart, so a round's 12 commits take about 2 minutes and
  the account makes 24 commits an hour, under the free plan's 128.

Every attempt is appended to a JSON-lines log (in the runs folder) before
the next step, and a restart resumes from it: rounds whose 30 minutes have
passed while the laptop was off are recorded as gaps, never made up late.
Every 6th round also times a few reads (``repo_info``, a tree listing), so
that latency can be plotted against the log's commit count. ``--finish``
squashes the log repository's history and times it, plus a few commits after.

Keep-awake is held while running (the laptop's power history: see the plan).
The token is never printed or written.

Usage:
    python scripts/proto/p5_commit_rate.py --org cassandra-chorus [--days 7] [--finish]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cassandra_chorus.paths import runs_root  # noqa: E402
from scripts.proto.common import RESULTS_DIR, guarded_token, record_hub_resource, write_json  # noqa: E402

MEMBERS = 5
ROUND_SECONDS = 30 * 60
STEP_SPACING_SECONDS = 10
READS_EVERY_ROUNDS = 6


def round_steps(members: int = MEMBERS) -> list[str]:
    """The commit steps of one round, in order."""
    return [f"update/m{i}" for i in range(members)] + [f"entry/m{i}" for i in range(members)] + ["close", "checkpoint"]


@dataclasses.dataclass(frozen=True)
class NextAction:
    """What to do now: ``kind`` is "step", "wait" or "done"; ``gaps`` are rounds to record as missed."""

    kind: str
    round_index: int = -1
    step: str = ""
    wait_seconds: float = 0.0
    gaps: tuple[int, ...] = ()


def plan_next(done: set[tuple[int, str]], recorded_gaps: set[int], t0: float, now: float, rounds: int,
              steps: list[str]) -> NextAction:
    """The next action, given the steps already attempted and the time. Pure function.

    Round r runs from t0 + r * ROUND_SECONDS for ROUND_SECONDS. A round whose
    window has passed with steps left undone (and not yet recorded as a gap)
    becomes a gap; its steps are never attempted late.
    """
    current = int((now - t0) // ROUND_SECONDS)
    if current >= rounds:
        last_gaps = tuple(r for r in range(rounds) if r not in recorded_gaps and any((r, s) not in done for s in steps))
        return NextAction("done", gaps=last_gaps)
    gaps = tuple(r for r in range(max(current, 0)) if r not in recorded_gaps and any((r, s) not in done for s in steps))
    if current < 0:
        return NextAction("wait", wait_seconds=t0 - now, gaps=gaps)
    for s in steps:
        if (current, s) not in done:
            return NextAction("step", round_index=current, step=s, gaps=gaps)
    return NextAction("wait", wait_seconds=t0 + (current + 1) * ROUND_SECONDS - now, gaps=gaps)


class AttemptLog:
    """Append-only JSON-lines log of attempts and events; the state for resuming."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.records: list[dict[str, Any]] = []
        if path.exists():
            self.records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def append(self, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            f.flush()
        self.records.append(record)

    def t0(self) -> float | None:
        return next((r["t0"] for r in self.records if r.get("event") == "start"), None)

    def done(self) -> set[tuple[int, str]]:
        return {(r["round"], r["step"]) for r in self.records if r.get("event") == "attempt"}

    def gaps(self) -> set[int]:
        return {r["round"] for r in self.records if r.get("event") == "gap"}


def _status(e: Exception) -> int | None:
    return getattr(getattr(e, "response", None), "status_code", None)


def attempt(api, org: str, round_index: int, step: str) -> dict[str, Any]:
    """Make one commit for ``step`` of ``round_index``; return a record of the attempt."""
    import os

    from huggingface_hub import CommitOperationAdd

    log_repo = f"{org}/proto-p5-log"
    t = time.time()
    try:
        if step.startswith("update/"):
            member = step.split("/")[1]
            repo = f"{org}/proto-p5-{member}"
            api.create_commit(repo, [CommitOperationAdd(f"round-{round_index:06d}/update.bin", os.urandom(2**20))],
                              commit_message=f"update r{round_index}")
        else:
            repo = log_repo
            name = step.replace("/", ".")
            body = json.dumps({"schema": 1, "round": round_index, "type": step, "t": t}).encode()
            parent = api.repo_info(log_repo).sha
            api.create_commit(log_repo, [CommitOperationAdd(f"rounds/{round_index:06d}/{name}.json", body),
                                         CommitOperationAdd(f"rounds/{round_index:06d}/{name}.json.sig", b"0" * 88)],
                              commit_message=f"{step} r{round_index}", parent_commit=parent)
        return {"event": "attempt", "round": round_index, "step": step, "repo": repo, "t": t,
                "seconds": round(time.time() - t, 3), "status": 200}
    except Exception as e:  # noqa: BLE001
        resp = getattr(e, "response", None)
        return {"event": "attempt", "round": round_index, "step": step, "t": t, "seconds": round(time.time() - t, 3),
                "status": _status(e), "error": type(e).__name__,
                "retry_after": resp.headers.get("retry-after") if resp is not None else None}


def timed_reads(api, org: str, round_index: int) -> dict[str, Any]:
    log_repo = f"{org}/proto-p5-log"
    out: dict[str, Any] = {"event": "reads", "round": round_index, "t": time.time()}
    for name, fn in (("repo_info", lambda: api.repo_info(log_repo)),
                     ("list_round_folder", lambda: list(api.list_repo_tree(log_repo, path_in_repo=f"rounds/{round_index:06d}")))):
        t = time.time()
        try:
            fn()
            out[name] = round(time.time() - t, 3)
        except Exception as e:  # noqa: BLE001
            out[name] = f"error {_status(e)}"
    return out


def run(org: str, days: int, log_path: Path) -> None:
    from huggingface_hub import HfApi

    from cassandra_chorus.ops.power import keep_awake

    token = guarded_token(org)
    api = HfApi(token=token)
    log = AttemptLog(log_path)
    rounds = days * 24 * 3600 // ROUND_SECONDS
    steps = round_steps()
    if log.t0() is None:
        for repo in [f"{org}/proto-p5-log"] + [f"{org}/proto-p5-m{i}" for i in range(MEMBERS)]:
            record_hub_resource("repo", repo, "P5")
            api.create_repo(repo, private=True, exist_ok=True)
        log.append({"event": "start", "t0": time.time(), "rounds": rounds, "members": MEMBERS})
    else:
        log.append({"event": "resume", "t": time.time()})
    t0 = log.t0()
    with keep_awake() as awake:
        log.append({"event": "keep_awake", "t": time.time(), "state": str(awake)})
        while True:
            action = plan_next(log.done(), log.gaps(), t0, time.time(), rounds, steps)
            for g in action.gaps:
                log.append({"event": "gap", "round": g, "t": time.time()})
            if action.kind == "done":
                break
            if action.kind == "wait":
                time.sleep(min(action.wait_seconds, 60))
                continue
            record = attempt(api, org, action.round_index, action.step)
            log.append(record)
            if record["status"] == 429:
                print(f"[p5] 429 at round {action.round_index} {action.step}; retry-after {record.get('retry_after')}", flush=True)
            if action.step == steps[-1] and action.round_index % READS_EVERY_ROUNDS == 0:
                log.append(timed_reads(api, org, action.round_index))
            if action.step == steps[-1]:
                print(f"[p5] round {action.round_index} done", flush=True)
            time.sleep(STEP_SPACING_SECONDS)
    log.append({"event": "end", "t": time.time()})


def finish(org: str, log_path: Path) -> None:
    """Squash the log repository's history, time it, then time 3 more commits."""
    from huggingface_hub import HfApi

    api = HfApi(token=guarded_token(org))
    log = AttemptLog(log_path)
    log_repo = f"{org}/proto-p5-log"
    before = len(api.list_repo_commits(log_repo))
    t = time.time()
    try:
        api.super_squash_history(log_repo)
        log.append({"event": "squash", "t": t, "seconds": round(time.time() - t, 2), "commits_before": before,
                    "commits_after": len(api.list_repo_commits(log_repo))})
    except Exception as e:  # noqa: BLE001
        log.append({"event": "squash", "t": t, "status": _status(e), "error": type(e).__name__, "commits_before": before})
    for k in range(3):
        rec = attempt(api, org, 10**6 + k, "close")
        rec["event"] = "after_squash"
        log.append(rec)
        time.sleep(STEP_SPACING_SECONDS)
    summarize(log_path)


def summarize(log_path: Path) -> dict[str, Any]:
    """Results JSON and Markdown from the attempt log."""
    log = AttemptLog(log_path)
    attempts = [r for r in log.records if r.get("event") == "attempt"]
    by_status: dict[str, int] = {}
    for r in attempts:
        by_status[str(r["status"])] = by_status.get(str(r["status"]), 0) + 1
    log_commits = [r for r in attempts if r.get("repo", "").endswith("proto-p5-log") and r["status"] == 200]
    latencies = [r["seconds"] for r in log_commits]
    chunks = [latencies[i:i + 336] for i in range(0, len(latencies), 336)]
    report = {
        "prototype": "P5 a week at the planned commit rate", "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
        "attempts": len(attempts), "by_status": by_status, "gaps": sorted(log.gaps()),
        "log_commit_latency_by_day": [{"day": i, "n": len(c), "median_s": sorted(c)[len(c) // 2] if c else None,
                                       "max_s": max(c) if c else None} for i, c in enumerate(chunks)],
        "reads": [r for r in log.records if r.get("event") == "reads"],
        "squash": [r for r in log.records if r.get("event") == "squash"],
        "after_squash": [r for r in log.records if r.get("event") == "after_squash"],
    }
    write_json(RESULTS_DIR / "p5_commit_rate.json", report)
    lines = ["# P5 a week at the planned commit rate", "",
             f"Attempts: {report['attempts']} by status {report['by_status']}. Rounds missed (laptop off or asleep): "
             f"{len(report['gaps'])}.", "", "| Day | Log commits | Median latency (s) | Max latency (s) |", "|---|---|---|---|"]
    lines += [f"| {d['day']} | {d['n']} | {d['median_s']} | {d['max_s']} |" for d in report["log_commit_latency_by_day"]]
    lines += ["", f"Squash: {report['squash']}", ""]
    (RESULTS_DIR / "p5_commit_rate.md").write_text("\n".join(lines), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--log", type=Path, default=None, help="attempt log (default: runs folder)")
    parser.add_argument("--finish", action="store_true", help="squash the log repository and write the results")
    args = parser.parse_args(argv)
    log_path = args.log or (runs_root() / "proto-p5" / "attempts.jsonl")
    if args.finish:
        finish(args.org, log_path)
    else:
        run(args.org, args.days, log_path)
        summarize(log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
