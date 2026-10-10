"""Write the Task B report for Decision gate B from run logs (PLAN step 10, part c; SRS S0-A-04, S0-A-06).

Usage, from the repository root::

    python -m scripts.analyze_task_b [--runs-dir <runs folder>] [--out results/task_b_gate_b.md]

Reads only completed Task B matrix runs (by run name), evaluates S0-A-04 per seed
for the sliced arm and S0-A-06 over seeds, splits the sliced arm's gap into the
steps the comparison arms separate, and writes one Markdown report. Missing runs
are reported as missing, never as passes.
See docs/implementations/2026-10-11-task-b-analysis.md.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from cassandra_chorus.paths import REPO_ROOT, runs_root

SEEDS = (7, 11, 19)
ARMS = {"taskB-central": "centralized", "taskB-sliced-coverage": "sliced", "taskB-partial": "partial",
        "taskB-fullavg": "full"}
TITLES = {"centralized": "Centralized", "full": "Full-model averaging", "partial": "Partial update", "sliced": "Sliced"}
LIMIT = 0.05            # S0-A-04: at most 5% relative
NEGLIGIBLE = 0.025      # 0.1 x k/E with k = 2, E = 8 (the Task A convention)


class AmbiguousRunsError(ValueError):
    """Two completed runs claim the same arm and seed."""


@dataclasses.dataclass
class Row:
    run_id: str
    arm: str
    seed: int
    test_bpc: float
    final_validation_bpc: float | None
    least_share: float
    negligible: int
    commit: str | None
    dirty: bool | None
    resumes: int


def read(run_dir: Path) -> list[dict]:
    out = []
    for line in (run_dir / "log.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def run_row(run_dir: Path) -> Row | None:
    if not (run_dir / "log.jsonl").exists():
        return None
    recs = read(run_dir)
    header = next((r for r in recs if r["type"] == "header"), None)
    finals = [r for r in recs if r["type"] == "final"]
    ends = [r for r in recs if r["type"] == "end"]
    if header is None or not finals or not ends or ends[-1].get("status") != "completed":
        return None
    name, seed = header["config"]["run"]["name"], int(header["config"]["run"]["seed"])
    if name not in ARMS:
        return None
    final = finals[-1]
    curve = [r for r in recs if r["type"] in ("round", "eval") and "bpc" in r]
    shares = [[c / (sum(layer) / 2) for c in layer] for layer in final["test"]["expert_counts"]]
    git = header.get("git") or {}
    return Row(run_id=header["run_id"], arm=ARMS[name], seed=seed, test_bpc=final["test"]["bpc"],
               final_validation_bpc=curve[-1]["bpc"] if curve else None,
               least_share=min(min(layer) for layer in shares),
               negligible=sum(s < NEGLIGIBLE for layer in shares for s in layer),
               commit=git.get("commit"), dirty=git.get("dirty"), resumes=sum(r["type"] == "resume" for r in recs))


def collect(run_dirs) -> dict[tuple[str, int], Row]:
    rows: dict[tuple[str, int], Row] = {}
    for d in sorted(run_dirs):
        row = run_row(d)
        if row is None:
            continue
        key = (row.arm, row.seed)
        if key in rows:
            raise AmbiguousRunsError(f"two completed runs for {key}: {rows[key].run_id} and {row.run_id}")
        rows[key] = row
    return rows


def evaluate(rows: dict[tuple[str, int], Row]) -> dict:
    """Per seed: gaps of every arm, the S0-A-04 verdict for the sliced arm, the decomposition; then S0-A-06."""
    per_seed = {}
    for s in SEEDS:
        b = {arm: rows[(arm, s)].test_bpc for arm in TITLES if (arm, s) in rows}
        if "centralized" not in b:
            per_seed[s] = {"verdict": "missing", "detail": "no centralized run", "gaps": {}, "steps": None}
            continue
        c = b["centralized"]
        gaps = {arm: (v - c) / c for arm, v in b.items() if arm != "centralized"}
        if "sliced" in gaps:
            verdict = "pass" if gaps["sliced"] <= LIMIT else "fail"
            detail = f"sliced {100 * gaps['sliced']:+.1f}% (limit +{100 * LIMIT:.0f}%)"
        else:
            verdict, detail = "missing", "no sliced run"
        steps = None
        if all(a in b for a in ("full", "partial", "sliced")):
            steps = {"local averaging": (b["full"] - c) / c, "partial updates": (b["partial"] - b["full"]) / c,
                     "masked routing": (b["sliced"] - b["partial"]) / c}
        per_seed[s] = {"verdict": verdict, "detail": detail, "gaps": gaps, "steps": steps}
    verdicts = [per_seed[s]["verdict"] for s in SEEDS]
    if all(v == "pass" for v in verdicts):
        overall = "pass"
    elif "fail" in verdicts:
        overall = "fail"  # S0-A-06: every seed must pass, so one failure decides it
    else:
        overall = "incomplete"
    return {"per_seed": per_seed, "overall": overall}


def span(values, fmt):
    values = [v for v in values if v is not None]
    if not values:
        return "n/a"
    lo, hi, mean = min(values), max(values), sum(values) / len(values)
    return f"{fmt(mean)} ({fmt(lo)} to {fmt(hi)})" if len(values) > 1 else fmt(mean)


def report(rows, result, runs_dir: Path) -> str:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    if subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip():
        commit += " with uncommitted changes"
    pct = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    lines = [
        "# Task B · Gate B report",
        "",
        f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC by `python -m scripts.analyze_task_b` (code `{commit}`) "
        f"from the run logs in `{runs_dir}`, {len(rows)} completed matrix runs. Test bits per character on the whole "
        "text8 test split (4,999,936 characters); lower is better.",
        "",
        f"## S0-A-04 for the sliced arm: {result['overall'].upper()}",
        "",
        "| Seed | Verdict | Detail |",
        "|---|---|---|",
    ]
    for s in SEEDS:
        p = result["per_seed"][s]
        lines.append(f"| {s} | {p['verdict']} | {p['detail']} |")
    lines += ["", "S0-A-06 requires the criterion on every seed. The other arms are reported for diagnosis.", "",
              "## Test bits per character by arm and seed", "",
              "| Arm | " + " | ".join(f"Seed {s}" for s in SEEDS) + " | Gap to centralized: mean (range) |",
              "|---|" + "---|" * (len(SEEDS) + 1)]
    for arm, title in TITLES.items():
        cells = []
        for s in SEEDS:
            r = rows.get((arm, s))
            g = result["per_seed"][s]["gaps"].get(arm)
            cells.append("missing" if r is None else f"{r.test_bpc:.4f}" + ("" if g is None else f" ({pct(g)})"))
        gap_cell = "reference" if arm == "centralized" else span([result["per_seed"][s]["gaps"].get(arm) for s in SEEDS], pct)
        lines.append(f"| {title} | " + " | ".join(cells) + f" | {gap_cell} |")
    lines += ["", "## Where the sliced arm's gap comes from", "",
              "Each step adds one restriction, measured by two arms that differ only in it (percent of centralized "
              "bits per character, same seed). The steps sum to the sliced arm's gap.", "",
              "| Step | Arms compared | " + " | ".join(f"Seed {s}" for s in SEEDS) + " | Mean (range) |",
              "|---|---|" + "---|" * (len(SEEDS) + 1)]
    pairs = {"local averaging": "full-model averaging vs centralized", "partial updates": "partial update vs full-model averaging",
             "masked routing": "sliced vs partial update"}
    for step, arms in pairs.items():
        vals = [result["per_seed"][s]["steps"][step] if result["per_seed"][s]["steps"] else None for s in SEEDS]
        lines.append(f"| {step} | {arms} | " + " | ".join("n/a" if v is None else pct(v) for v in vals) + f" | {span(vals, pct)} |")
    lines += ["", "## Runs", "",
              "| Arm | Seed | Run ID | Commit | Final validation bpc | Least-used expert share | Negligible experts | Resumed |",
              "|---|---|---|---|---|---|---|---|"]
    for (arm, s), r in sorted(rows.items(), key=lambda kv: (list(TITLES).index(kv[0][0]), kv[0][1])):
        c = "unknown" if r.commit is None else r.commit[:7] + (" (dirty)" if r.dirty else "")
        v = "n/a" if r.final_validation_bpc is None else f"{r.final_validation_bpc:.4f}"
        lines.append(f"| {TITLES[arm]} | {s} | `{r.run_id}` | `{c}` | {v} | {r.least_share:.3f} | {r.negligible} | {r.resumes} |")
    lines += ["", "## Decision gate B (PLAN section 5)", "",
              "- Gap within the criterion: proceed to Stage 1.",
              "- Moderate gap: report it, and decide whether the flagship is still worth building at that cost.",
              "- Large gap: treat as a negative result, publish it, and reconsider the architecture.",
              "",
              "PLAN leaves \"moderate\" and \"large\" undefined; which applies, and what follows, is the owner's decision.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "task_b_gate_b.md")
    args = parser.parse_args(argv)
    runs_dir = args.runs_dir or runs_root()
    rows = collect(p for p in runs_dir.iterdir() if p.is_dir())
    result = evaluate(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report(rows, result, runs_dir), encoding="utf-8", newline="\n")
    print(f"{len(rows)} runs; S0-A-04 {result['overall']}; report written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
