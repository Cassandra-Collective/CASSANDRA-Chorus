"""P4: concurrent conditional-commit writers on one branch (docs/implementations/2026-10-14-solo-prototypes.md).

Separate processes on this machine stand for pilot members; all use the
``chorus-prototypes`` token. Repository: ``<org>/proto-log`` (private).

The free plan allows 128 commit-creation requests per hour per account, and
rejected conditional commits appear to count (first attempt:
``results/prototypes/p4_attempt1_rate_limit.md``). The phases are therefore
ordered by importance and sized to fit about 80 attempts:

1. Close races: in each trial 5 writers commit ``<run>/race/<trial>/close.json``
   with their own content and the same parent, at the same instant.
   Pass: exactly one succeeds and the file holds that writer's content.
2. Multi-file visibility: one commit adds 50 files while a second process
   lists the tree as fast as it can. Recorded: whether a listing ever showed
   only some of the 50.
3. Appends: W writers each append E entries; every commit carries
   ``parent_commit`` = the head the writer last read; on HTTP 412 the writer
   re-reads the head, waits a random 0 to 0.5 s and retries. Pass: every
   entry a writer was told succeeded is in the final tree, none it was told
   failed is, and nothing else is.

Every commit attempt is recorded with its HTTP status. A 429 (rate limit)
ends the phase for that writer cleanly, and results are written after every
phase. The token is never printed or written.

Usage:
    python scripts/proto/p4_log_writers.py --org cassandra-chorus [--run r2] [--trials 10] [--visibility 2] [--writers 3] [--entries 4]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.proto.common import RESULTS_DIR, guarded_token, record_hub_resource, write_json  # noqa: E402

RESULT_JSON = RESULTS_DIR / "p4_log_writers.json"
RESULT_MD = RESULTS_DIR / "p4_log_writers.md"


def _api(token: str):
    from huggingface_hub import HfApi

    return HfApi(token=token)


def _status(e: Exception) -> int | None:
    return getattr(getattr(e, "response", None), "status_code", None)


def append_worker(token: str, repo_id: str, writer: str, prefix: str, entries: int, start_at: float) -> dict[str, Any]:
    """Append up to ``entries`` entries as ``writer``; return every attempt and what the writer was told."""
    from huggingface_hub import CommitOperationAdd

    api = _api(token)
    rng = random.Random(f"{prefix}/{writer}")
    time.sleep(max(0.0, start_at - time.time()))
    head = api.repo_info(repo_id).sha
    attempts: list[dict[str, Any]] = []
    told: dict[str, str] = {}
    for seq in range(entries):
        path = f"{prefix}/{writer}-{seq:03d}.json"
        body = json.dumps({"writer": writer, "seq": seq}).encode()
        other_errors = 0
        while True:
            t = time.time()
            try:
                info = api.create_commit(repo_id, [CommitOperationAdd(path, body)], commit_message=f"{writer} {seq}",
                                         parent_commit=head)
                attempts.append({"path": path, "t": t, "status": 200})
                head = info.oid
                told[path] = "success"
                break
            except Exception as e:  # noqa: BLE001
                status = _status(e)
                attempts.append({"path": path, "t": t, "status": status, "error": type(e).__name__})
                if status == 429:
                    told[path] = "rate-limited"
                    return {"writer": writer, "attempts": attempts, "told": told, "stopped_by_429": True}
                if status != 412:
                    other_errors += 1
                    if other_errors >= 3:
                        told[path] = "failed"
                        break
                time.sleep(rng.uniform(0, 0.5))
                head = api.repo_info(repo_id).sha
    return {"writer": writer, "attempts": attempts, "told": told, "stopped_by_429": False}


def race_worker(token: str, repo_id: str, writer: str, path: str, parent: str, start_at: float) -> dict[str, Any]:
    """One attempt to commit ``path`` with this writer's content on ``parent`` at ``start_at``."""
    from huggingface_hub import CommitOperationAdd

    api = _api(token)
    time.sleep(max(0.0, start_at - time.time()))
    sent = time.time()
    try:
        info = api.create_commit(repo_id, [CommitOperationAdd(path, writer.encode())], commit_message=f"close by {writer}",
                                 parent_commit=parent)
        return {"writer": writer, "ok": True, "status": 200, "oid": info.oid, "sent": sent, "returned": time.time()}
    except Exception as e:  # noqa: BLE001
        return {"writer": writer, "ok": False, "status": _status(e), "error": type(e).__name__, "sent": sent,
                "returned": time.time()}


def visibility_reader(token: str, repo_id: str, prefix: str, expected: int, start_at: float, seconds: float) -> list[dict[str, Any]]:
    """List the tree under ``prefix`` repeatedly; record how many of the expected files each listing saw."""
    api = _api(token)
    time.sleep(max(0.0, start_at - time.time()))
    seen = []
    end = time.time() + seconds
    while time.time() < end:
        t = time.time()
        try:
            n = sum(1 for f in api.list_repo_tree(repo_id, path_in_repo=prefix, recursive=True) if f.path.endswith(".json"))
        except Exception as e:  # noqa: BLE001 (before the commit the folder does not exist)
            n = 0 if _status(e) == 404 else -1
        seen.append({"t": t, "count": n})
        if n == expected:
            break
        time.sleep(0.2)  # keeps the reader well inside the 1,000 requests per 300 s API window
    return seen


def visibility_writer(token: str, repo_id: str, prefix: str, files: int, start_at: float) -> dict[str, Any]:
    from huggingface_hub import CommitOperationAdd

    api = _api(token)
    time.sleep(max(0.0, start_at - time.time()))
    ops = [CommitOperationAdd(f"{prefix}/f{i:03d}.json", json.dumps({"i": i}).encode()) for i in range(files)]
    sent = time.time()
    try:
        info = api.create_commit(repo_id, ops, commit_message=f"{files} files at once")
        return {"ok": True, "status": 200, "sent": sent, "returned": time.time(), "oid": info.oid}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "status": _status(e), "error": type(e).__name__, "sent": sent, "returned": time.time()}


def _save(report: dict[str, Any]) -> None:
    write_json(RESULT_JSON, report)
    RESULT_MD.write_text(summary_markdown(report), encoding="utf-8")


def run(org: str, run_id: str, trials: int, visibility: int, writers: int, entries: int) -> dict[str, Any]:
    token = guarded_token(org)
    api = _api(token)
    repo_id = f"{org}/proto-log"
    record_hub_resource("repo", repo_id, "P4")
    api.create_repo(repo_id, private=True, exist_ok=True)
    report: dict[str, Any] = {
        "prototype": "P4 concurrent log writers", "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
        "org": org, "repo": repo_id, "run": run_id, "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "limits_known": "free plan: 128 commit-creation requests per hour per account; API 1,000 requests per 300 s",
        "races": [], "visibility": [], "appends": None, "attempts_by_status": {}, "first_429_after_attempts": None,
    }
    attempt_count = 0

    def count(statuses: list[int | None]) -> None:
        nonlocal attempt_count
        for s in statuses:
            attempt_count += 1
            key = str(s)
            report["attempts_by_status"][key] = report["attempts_by_status"].get(key, 0) + 1
            if s == 429 and report["first_429_after_attempts"] is None:
                report["first_429_after_attempts"] = attempt_count

    with cf.ProcessPoolExecutor(max_workers=6) as pool:
        # 1. Close races (5 writers)
        for trial in range(trials):
            parent = api.repo_info(repo_id).sha
            path = f"{run_id}/race/{trial:02d}/close.json"
            start_at = time.time() + 3
            outs = [f.result() for f in [pool.submit(race_worker, token, repo_id, f"m{i}", path, parent, start_at) for i in range(5)]]
            count([o["status"] for o in outs])
            winners = [o["writer"] for o in outs if o["ok"]]
            content = None
            if winners:
                from huggingface_hub import hf_hub_download

                content = Path(hf_hub_download(repo_id, path, token=token, force_download=True)).read_text()
            report["races"].append({"trial": trial, "successes": len(winners), "winner": winners[0] if winners else None,
                                    "file_content": content, "statuses": sorted(str(o["status"]) for o in outs),
                                    "send_spread_ms": round(1000 * (max(o["sent"] for o in outs) - min(o["sent"] for o in outs)), 1),
                                    "pass": len(winners) == 1 and content == winners[0]})
            print(f"[p4] race {trial}: {len(winners)} success(es), statuses {report['races'][-1]['statuses']}", flush=True)
            _save(report)
            if any(o["status"] == 429 for o in outs):
                print("[p4] rate limited: stopping the races", flush=True)
                break
            time.sleep(2)

        # 2. Multi-file visibility
        for k in range(visibility if report["first_429_after_attempts"] is None else 0):
            prefix = f"{run_id}/visibility/{k:02d}"
            start_at = time.time() + 5
            reader = pool.submit(visibility_reader, token, repo_id, prefix, 50, start_at - 1, 60)
            writer = pool.submit(visibility_writer, token, repo_id, prefix, 50, start_at)
            w, seen = writer.result(), reader.result()
            count([w["status"]])
            counts = [s["count"] for s in seen]
            report["visibility"].append({
                "trial": k, "commit_status": w["status"], "listings": len(seen),
                "partial_seen": any(0 < c < 50 for c in counts), "counts_seen": sorted(set(counts)),
                "first_full_after_commit_returned_s": next((round(s["t"] - w["returned"], 2) for s in seen if s["count"] == 50), None),
                "commit_seconds": round(w["returned"] - w["sent"], 2)})
            print(f"[p4] visibility {k}: status {w['status']}, partial seen = {report['visibility'][-1]['partial_seen']}", flush=True)
            _save(report)
            if w["status"] == 429:
                break
            time.sleep(5)

        # 3. Appends
        if report["first_429_after_attempts"] is None:
            prefix = f"{run_id}/appends/w{writers}"
            start_at = time.time() + 8
            results = [f.result() for f in [pool.submit(append_worker, token, repo_id, f"m{i}", prefix, entries, start_at)
                                            for i in range(writers)]]
            for r in results:
                count([a["status"] for a in sorted(r["attempts"], key=lambda a: a["t"])])
            tree = {f.path for f in api.list_repo_tree(repo_id, path_in_repo=prefix, recursive=True) if f.path.endswith(".json")}
            told = {p: v for r in results for p, v in r["told"].items()}
            ok = {p for p, v in told.items() if v == "success"}
            not_ok = {p for p, v in told.items() if v != "success"}
            report["appends"] = {
                "writers": writers, "entries_each": entries,
                "told": {v: sum(1 for x in told.values() if x == v) for v in sorted(set(told.values()))},
                "missing_after_success": sorted(ok - tree), "present_after_not_success": sorted(not_ok & tree),
                "unexpected_in_tree": sorted(tree - set(told)),
                "attempts": sum(len(r["attempts"]) for r in results),
                "statuses": {s: sum(1 for r in results for a in r["attempts"] if str(a["status"]) == s)
                             for s in sorted({str(a["status"]) for r in results for a in r["attempts"]})},
                "stopped_by_429": any(r["stopped_by_429"] for r in results),
                "pass": not (ok - tree) and not (not_ok & tree) and not (tree - set(told)),
            }
            print(f"[p4] appends: pass = {report['appends']['pass']}, told {report['appends']['told']}", flush=True)
            _save(report)

    commits = api.list_repo_commits(repo_id)
    report["commits_in_repo"] = len(commits)
    report["attempts_total"] = attempt_count
    report["server_commit_times_sample"] = [c.created_at.isoformat() for c in commits[:3]]
    report["all_pass"] = (bool(report["races"]) and all(r["pass"] for r in report["races"])
                          and not any(v["partial_seen"] for v in report["visibility"])
                          and (report["appends"] is None or report["appends"]["pass"]))
    _save(report)
    return report


def summary_markdown(r: dict[str, Any]) -> str:
    lines = ["# P4 concurrent log writers", "",
             f"Plan: `{r['plan']}`. Repository `{r['repo']}` (private), run `{r['run']}` started {r['time_utc']}. "
             f"Writers are separate processes on one machine, one account and token. Known limits: {r['limits_known']}. "
             f"Commit attempts by HTTP status: {r['attempts_by_status']}; first 429 after attempt "
             f"{r['first_429_after_attempts'] or 'none'}.", "",
             "## Close races (5 writers, same parent, same instant)", ""]
    races = r["races"]
    if races:
        lines += ["| Trial | Successes | Winner | File content | Statuses | Send spread (ms) | Pass |", "|---|---|---|---|---|---|---|"]
        for x in races:
            lines.append(f"| {x['trial']} | {x['successes']} | {x['winner']} | {x['file_content']} | {', '.join(x['statuses'])} | "
                         f"{x['send_spread_ms']} | {'yes' if x['pass'] else '**no**'} |")
    lines += ["", "## Multi-file visibility (50 files in one commit)", ""]
    if r["visibility"]:
        lines += ["| Trial | Commit status | Listings | Counts seen | Partial seen | Full after commit returned (s) | Commit took (s) |",
                  "|---|---|---|---|---|---|---|"]
        for v in r["visibility"]:
            lines.append(f"| {v['trial']} | {v['commit_status']} | {v['listings']} | {v['counts_seen']} | "
                         f"{'**yes**' if v['partial_seen'] else 'no'} | {v['first_full_after_commit_returned_s']} | {v['commit_seconds']} |")
    else:
        lines.append("Not run.")
    lines += ["", "## Appends", ""]
    a = r["appends"]
    if a:
        lines += [f"{a['writers']} writers, {a['entries_each']} entries each. Told: {a['told']}. Attempts: {a['attempts']} "
                  f"by status {a['statuses']}. Missing after success: {len(a['missing_after_success'])}; present after "
                  f"failure: {len(a['present_after_not_success'])}; unexpected: {len(a['unexpected_in_tree'])}. "
                  f"Pass: **{'yes' if a['pass'] else 'no'}**."]
    else:
        lines.append("Not run.")
    if "all_pass" in r:
        lines += ["", f"Commits in the repository afterwards: {r['commits_in_repo']}. All checks passed: "
                  f"**{'yes' if r['all_pass'] else 'no'}**."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", required=True)
    parser.add_argument("--run", default="r2", help="prefix for this run's paths in the repository")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--visibility", type=int, default=2)
    parser.add_argument("--writers", type=int, default=3)
    parser.add_argument("--entries", type=int, default=4)
    args = parser.parse_args(argv)
    report = run(args.org, args.run, args.trials, args.visibility, args.writers, args.entries)
    print(summary_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
