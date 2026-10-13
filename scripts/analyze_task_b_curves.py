"""Pair the Task B validation curves at equal compute: when does each arm's gap open? (PLAN step 11, batch 1).

Usage, from the repository root::

    python -m scripts.analyze_task_b_curves [--runs-dir <runs folder>] [--out results/task_b_gap_curves.md]

Reads the completed Task B runs, selected exactly as ``scripts.analyze_task_b`` selects them. Centralized
runs log validation bits per character every 1,000 steps; simulated runs log it after every merge, when
round r has used N x H x (r + 1) worker steps in total. Every step, centralized or worker, is one batch
of 32 sequences, so centralized step s is paired with the round whose total worker steps equal s (equal
compute, D17). Validation is the first 1M validation characters in both. No GPU, no side effects except
writing the report. See docs/implementations/2026-10-13-averaging-gap-batch-1.md.
"""

from __future__ import annotations

import argparse
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from cassandra_chorus.paths import REPO_ROOT, runs_root
from scripts.analyze_task_b import SEEDS, TITLES, collect, read

SIM_ARMS = ("full", "partial", "sliced")


def centralized_curve(recs: list[dict]) -> dict[int, float]:
    """``{step: validation bpc}`` from a centralized run's ``eval`` records (step 0 is the untrained model)."""
    return {int(r["step"]): float(r["bpc"]) for r in recs if r.get("type") == "eval" and "bpc" in r}


def simulated_curve(recs: list[dict]) -> dict[int, float]:
    """``{total worker steps: validation bpc of the merged model}`` from a simulated run's ``round`` records.

    Total worker steps after round r is ``n_workers x local_steps x (r + 1)``, read from the run's header.
    """
    header = next(r for r in recs if r.get("type") == "header")
    sim = header["config"]["sim"]
    per_round = int(sim["n_workers"]) * int(sim["local_steps"])
    return {per_round * (int(r["round"]) + 1): float(r["bpc"])
            for r in recs if r.get("type") == "round" and "bpc" in r}


def pair(central: dict[int, float], arms: dict[str, dict[int, float]]) -> list[dict]:
    """One row per centralized step after 0 that every given arm also reached.

    Each row: ``step``, ``centralized`` bpc, and per arm its bpc and relative gap ``bpc / centralized - 1``.
    """
    rows = []
    for step in sorted(s for s in central if s > 0):
        if all(step in curve for curve in arms.values()):
            c = central[step]
            row = {"step": step, "centralized": c}
            for arm, curve in arms.items():
                row[arm] = curve[step]
                row[f"{arm}_gap"] = curve[step] / c - 1.0
            rows.append(row)
    return rows


def curves_by_seed(rows_by_key: dict, runs_dir: Path) -> dict[int, list[dict]]:
    """Paired rows for every seed that has a centralized run and at least one simulated arm."""
    out = {}
    for seed in SEEDS:
        if ("centralized", seed) not in rows_by_key:
            continue
        central = centralized_curve(read(runs_dir / rows_by_key[("centralized", seed)].run_id))
        arms = {arm: simulated_curve(read(runs_dir / rows_by_key[(arm, seed)].run_id))
                for arm in SIM_ARMS if (arm, seed) in rows_by_key}
        if arms:
            out[seed] = pair(central, arms)
    return out


def mean_over_seeds(per_seed: dict[int, list[dict]]) -> list[dict]:
    """Mean gap per step and arm over the seeds that have that step and arm, with the min and max."""
    steps = sorted({row["step"] for rows in per_seed.values() for row in rows})
    out = []
    for step in steps:
        row = {"step": step, "seeds": 0}
        for arm in SIM_ARMS:
            gaps = [r[f"{arm}_gap"] for rows in per_seed.values() for r in rows
                    if r["step"] == step and f"{arm}_gap" in r]
            if gaps:
                row[arm] = (statistics.fmean(gaps), min(gaps), max(gaps), len(gaps))
        row["seeds"] = max((v[3] for k, v in row.items() if k in SIM_ARMS), default=0)
        out.append(row)
    return out


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def pct(x: float) -> str:
    return f"{100 * x:+.1f}"


def report(rows_by_key: dict, per_seed: dict[int, list[dict]], means: list[dict], runs_dir: Path) -> str:
    total = max((r["step"] for r in means), default=0)
    lines = [
        "# Task B · When the gap opens: validation curves at equal compute",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by "
        f"`python -m scripts.analyze_task_b_curves` (code `{git_commit()}`) from the run logs in `{runs_dir}`. "
        "Plan: `docs/implementations/2026-10-13-averaging-gap-batch-1.md`.",
        "",
        "Validation bits per character on the first 1M validation characters (non-overlapping 256-character "
        "windows), not the test split. Gap = arm / centralized - 1 at the same total compute: centralized "
        "step s against the merged model after the round whose total worker steps equal s. Both learning-rate "
        "decays start at 80% of compute (centralized step 16,000; worker step 4,000 of 5,000).",
        "",
        "## Mean gap over seeds, percent",
        "",
        "| Worker steps (all workers) | Share of compute | " + " | ".join(
            f"{TITLES[a]} mean (min to max)" for a in SIM_ARMS) + " | Seeds |",
        "|---|---|" + "---|" * len(SIM_ARMS) + "---|",
    ]
    for row in means:
        cells = []
        for arm in SIM_ARMS:
            if arm in row:
                m, lo, hi, _ = row[arm]
                cells.append(f"{pct(m)} ({pct(lo)} to {pct(hi)})")
            else:
                cells.append("n/a")
        share = f"{100 * row['step'] / total:.0f}%" if total else "n/a"
        lines.append(f"| {row['step']:,} | {share} | " + " | ".join(cells) + f" | {row['seeds']} |")
    for seed, rows in per_seed.items():
        arms = [a for a in SIM_ARMS if rows and a in rows[0]]
        lines += ["", f"## Seed {seed}", "",
                  "| Worker steps | Centralized bpc | " + " | ".join(f"{TITLES[a]} bpc (gap %)" for a in arms) + " |",
                  "|---|---|" + "---|" * len(arms)]
        for r in rows:
            lines.append(f"| {r['step']:,} | {r['centralized']:.4f} | "
                         + " | ".join(f"{r[a]:.4f} ({pct(r[f'{a}_gap'])})" for a in arms) + " |")
    lines += ["", "## Runs read", "", "| Arm | Seed | Run |", "|---|---|---|"]
    for (arm, seed), row in sorted(rows_by_key.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        lines.append(f"| {TITLES[arm]} | {seed} | `{row.run_id}` |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "task_b_gap_curves.md")
    args = parser.parse_args(argv)
    runs_dir = args.runs_dir or runs_root()
    rows_by_key = collect(p for p in runs_dir.iterdir() if p.is_dir())
    per_seed = curves_by_seed(rows_by_key, runs_dir)
    means = mean_over_seeds(per_seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report(rows_by_key, per_seed, means, runs_dir), encoding="utf-8", newline="\n")
    print(f"{len(rows_by_key)} runs, {len(per_seed)} seeds paired; report written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
