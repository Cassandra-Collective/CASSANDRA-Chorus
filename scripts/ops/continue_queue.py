"""Continue a run matrix after an interruption (power loss, restart): run only what is not finished.

Usage, from the repository root (normally through scripts/ops/launch_visible.ps1)::

    python -m scripts.ops.continue_queue configs/queues/task_b_matrix.toml [--dry-run]

For each entry of the queue, in order, it looks in the runs folder for runs
with the entry's run name and seed:

- a completed run (its last ``end`` record has status ``completed``): skipped;
- an unfinished run with ``checkpoint.pt`` whose script accepts ``--resume``
  (the ``*_sliced`` scripts): the newest one is resumed;
- otherwise: run from the start.

The remaining entries are written to ``<runs>/queues/<queue>_continue_<time>.toml``
with ``stop_on_failure = false`` and run by the queue runner. Refuses while a
process is computing on the GPU, so a run still in progress is never resumed twice.
See docs/implementations/2026-10-10-continue-queue.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from cassandra_chorus.config import apply_overrides, read_config_file
from cassandra_chorus.paths import REPO_ROOT, runs_root
from scripts.ops import run_queue

RESUMABLE_SUFFIX = "_sliced"  # scripts with --resume (train_task_a_sliced, train_task_b_sliced)


def entry_identity(entry: dict) -> tuple[str, int]:
    """Run name and seed of a queue entry, from its configuration file and --set overrides."""
    args = entry.get("args", [])
    if "--config" not in args:
        raise ValueError(f"entry {entry} has no --config; continue works from the original matrix, not a resume queue")
    config = REPO_ROOT / args[args.index("--config") + 1]
    overrides = [args[i + 1] for i, a in enumerate(args) if a == "--set"]
    data = apply_overrides(read_config_file(config), overrides)
    return data["run"]["name"], int(data["run"]["seed"])


def run_status(run_dir: Path) -> str:
    """'completed', 'resumable' (unfinished, has a checkpoint) or 'unfinished'."""
    log = run_dir / "log.jsonl"
    ends = []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:  # a line cut short by a power loss
                    continue
                if record.get("type") == "end":
                    ends.append(record.get("status"))
    if ends and ends[-1] == "completed":
        return "completed"
    return "resumable" if (run_dir / "checkpoint.pt").exists() else "unfinished"


def plan(entries: list[dict], runs_dir: Path) -> list[tuple[str, dict, str]]:
    """For each entry: (action, queue entry to run or the original, explanation). Action is skip, resume or run."""
    folders = [d for d in runs_dir.iterdir() if d.is_dir()] if runs_dir.exists() else []
    out = []
    for entry in entries:
        name, seed = entry_identity(entry)
        mine = sorted(d for d in folders if d.name.partition("_")[2] == f"{name}_s{seed}")
        status = {d: run_status(d) for d in mine}
        done = [d for d in mine if status[d] == "completed"]
        resumable = [d for d in mine if status[d] == "resumable"]
        if done:
            out.append(("skip", entry, f"{name} seed {seed}: completed in {done[-1].name}"))
        elif resumable and entry["module"].endswith(RESUMABLE_SUFFIX):
            target = resumable[-1]
            out.append(("resume", {"module": entry["module"], "args": ["--resume", target.as_posix()]},
                        f"{name} seed {seed}: resume {target.name}"))
        else:
            note = f" (unfinished folders left as they are: {', '.join(d.name for d in mine)})" if mine else ""
            out.append(("run", entry, f"{name} seed {seed}: run from the start{note}"))
    return out


def gpu_busy() -> list[str]:
    """Processes computing on the GPU, as nvidia-smi reports them (empty if none or no nvidia-smi)."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def toml_queue(steps: list[tuple[str, dict, str]], source: Path) -> str:
    lines = [f"# Written by scripts/ops/continue_queue.py from {source.as_posix()} at "
             f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC.", "stop_on_failure = false", ""]
    for action, entry, why in steps:
        if action == "skip":
            continue
        lines += [f"# {why}", "[[run]]", f"module = {json.dumps(entry['module'])}",
                  "args = [" + ", ".join(json.dumps(a) for a in entry.get("args", [])) + "]", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("queue", type=Path, help="the original matrix queue file")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, run nothing")
    args = parser.parse_args(argv)
    entries, _ = run_queue.load_queue(args.queue)
    steps = plan(entries, runs_root())
    for action, _, why in steps:
        print(f"[continue] {action:6s} {why}", flush=True)
    remaining = [s for s in steps if s[0] != "skip"]
    if not remaining:
        print("[continue] nothing left to run: every entry has a completed run", flush=True)
        return 0
    if args.dry_run:
        return 0
    busy = gpu_busy()
    if busy:
        print(f"[continue] refusing: the GPU is in use ({'; '.join(busy)}). Is a queue still running?", flush=True)
        return 2
    out = runs_root() / "queues" / f"{args.queue.stem}_continue_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.toml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(toml_queue(steps, args.queue), encoding="utf-8", newline="\n")
    print(f"[continue] {len(remaining)} entries written to {out}; starting them", flush=True)
    return run_queue.main([str(out)])


if __name__ == "__main__":
    sys.exit(main())
