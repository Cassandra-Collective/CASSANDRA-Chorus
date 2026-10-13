"""Re-score the saved Task B models on the test split with sliding windows (PLAN step 11, batch 1, analysis 2).

Usage, from the repository root (normally through scripts/ops/launch_visible.ps1)::

    python -m scripts.rescore_task_b [--runs-dir <runs folder>] [--stride 64] [--device cuda] [--limit N]

For every completed Task B matrix run (selected as ``scripts.analyze_task_b`` selects them) it loads the
run's configuration and ``final_model.pt``, recomputes the test bits per character with the original
protocol (non-overlapping 256-character windows) and checks it against the value the run logged, then
scores the same characters with sliding windows of the given stride. Results accumulate in
``results/task_b_rescore.json`` so an interrupted session resumes where it stopped (``--limit`` scores at
most N new runs per call); ``results/task_b_rescore.md`` is rewritten from that file each time. Run
folders are only read. See docs/implementations/2026-10-13-averaging-gap-batch-1.md.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from cassandra_chorus.config import load_config
from cassandra_chorus.data.text8 import Text8
from cassandra_chorus.metrics.task_b import evaluate_bpc
from cassandra_chorus.model import MoETransformer
from cassandra_chorus.paths import REPO_ROOT, runs_root
from scripts.analyze_task_b import SEEDS, TITLES, collect, read
from scripts.analyze_task_b_curves import git_commit
from scripts.train_task_b_centralized import CentralizedTaskBConfig
from scripts.train_task_b_sliced import SlicedTaskBConfig

LOGGED_TOLERANCE = 1e-6  # recomputed original-protocol bpc must match the logged test bpc this closely


def load_model(run_dir: Path, arm: str, device: torch.device):
    """The run's configuration and its saved final model, in evaluation mode on ``device``."""
    schema = CentralizedTaskBConfig if arm == "centralized" else SlicedTaskBConfig
    cfg = load_config(run_dir / "config.json", schema)
    with torch.random.fork_rng(devices=[]):
        model = MoETransformer(cfg.model)
    model.load_state_dict(torch.load(run_dir / "final_model.pt", map_location="cpu"), strict=True)
    return cfg, model.to(device).eval()


def rescore_run(run_dir: Path, arm: str, seed: int, stride: int, device: torch.device) -> dict:
    """Both protocols for one run, with the logged test bpc and the check between them."""
    cfg, model = load_model(run_dir, arm, device)
    data = Text8(cfg.text8)
    logged = next(r for r in reversed(read(run_dir)) if r["type"] == "final")["test"]["bpc"]
    t0 = time.perf_counter()
    original = evaluate_bpc(model, data, "test", device)
    sliding = evaluate_bpc(model, data, "test", device, stride=stride)
    if abs(original["bpc"] - logged) > LOGGED_TOLERANCE:
        raise RuntimeError(f"{run_dir.name}: recomputed test bpc {original['bpc']:.8f} differs from the logged "
                           f"{logged:.8f}; the model or data was not reconstructed exactly")
    if sliding["scored"] != original["scored"]:
        raise RuntimeError(f"{run_dir.name}: the protocols scored {sliding['scored']} and {original['scored']} characters")
    return {"run_id": run_dir.name, "arm": arm, "seed": seed, "logged_bpc": logged, "original_bpc": original["bpc"],
            "sliding_bpc": sliding["bpc"], "stride": stride, "scored": original["scored"],
            "seconds": time.perf_counter() - t0}


def report(results: dict, stride: int) -> str:
    rows = {(r["arm"], r["seed"]): r for r in results.values()}
    lines = [
        "# Task B · Test bits per character, original and sliding-window protocols",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by `python -m scripts.rescore_task_b` "
        f"(code `{git_commit()}`). Plan: `docs/implementations/2026-10-13-averaging-gap-batch-1.md`.",
        "",
        f"Original: non-overlapping 256-character windows, context reset per window (each run's logged test value, "
        f"recomputed and matched within {LOGGED_TOLERANCE:g}). Sliding: windows every {stride} characters; the first "
        f"scores all 256 positions, each later one its last {stride}, so the same characters are scored with at "
        f"least {256 - stride} characters of context.",
        "",
        "| Arm | Seed | Original bpc | Sliding bpc | Change |",
        "|---|---|---|---|---|",
    ]
    for arm in TITLES:
        for seed in SEEDS:
            r = rows.get((arm, seed))
            if r:
                lines.append(f"| {TITLES[arm]} | {seed} | {r['original_bpc']:.4f} | {r['sliding_bpc']:.4f} | "
                             f"{r['sliding_bpc'] - r['original_bpc']:+.4f} |")
    lines += ["", "## Gaps to centralized under each protocol, percent", "",
              "| Arm | Original, mean (range) | Sliding, mean (range) | Seeds |", "|---|---|---|---|"]
    for arm in (a for a in TITLES if a != "centralized"):
        gaps = {"original": [], "sliding": []}
        for seed in SEEDS:
            c, r = rows.get(("centralized", seed)), rows.get((arm, seed))
            if c and r:
                for p in gaps:
                    gaps[p].append(r[f"{p}_bpc"] / c[f"{p}_bpc"] - 1.0)
        if gaps["original"]:
            cells = [f"{100 * statistics.fmean(g):+.1f} ({100 * min(g):+.1f} to {100 * max(g):+.1f})"
                     for g in gaps.values()]
            lines.append(f"| {TITLES[arm]} | {cells[0]} | {cells[1]} | {len(gaps['original'])} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument("--stride", type=int, default=64)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--limit", type=int, default=None, help="score at most this many new runs, then stop")
    parser.add_argument("--json", type=Path, default=REPO_ROOT / "results" / "task_b_rescore.json")
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "results" / "task_b_rescore.md")
    args = parser.parse_args(argv)
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("--device cuda requested but CUDA is not available")
    runs_dir = args.runs_dir or runs_root()
    rows = collect(p for p in runs_dir.iterdir() if p.is_dir())
    results = json.loads(args.json.read_text(encoding="utf-8")) if args.json.exists() else {}
    todo = [row for row in sorted(rows.values(), key=lambda r: r.run_id)
            if row.run_id not in results or results[row.run_id]["stride"] != args.stride]
    for row in todo[: args.limit]:
        print(f"re-scoring {row.run_id} ({row.arm}, seed {row.seed}) ...", flush=True)
        results[row.run_id] = rescore_run(runs_dir / row.run_id, row.arm, row.seed, args.stride, device)
        r = results[row.run_id]
        print(f"  original {r['original_bpc']:.4f}  sliding {r['sliding_bpc']:.4f}  ({r['seconds']:.0f}s)", flush=True)
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(results, indent=2), encoding="utf-8", newline="\n")  # after every run
    args.out.write_text(report(results, args.stride), encoding="utf-8", newline="\n")
    print(f"{len(results)} of {len(rows)} runs scored; report written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
