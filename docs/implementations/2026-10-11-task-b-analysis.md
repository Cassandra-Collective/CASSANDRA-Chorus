# 2026-10-11 · Task B analysis and the Gate B report (PLAN step 10, part c)

| | |
|---|---|
| PLAN step | 10 · Task B on text8, part c; prepares Decision gate B (step 12) |
| Branch | `stage0/10-task-b` |
| SRS requirements | S0-A-04, S0-A-06, S0-F-20, S0-F-23; decisions D25 to D27 |
| Status | Implemented and run on the complete matrix; Gate B decision with the owner |

## Problem / Motivation

The 12-run Task B matrix (D25, D26, D27) is complete or nearly so. Its runs have been recorded one by one in `RESULTS.md`; what is missing is a single reproducible report that:

- evaluates S0-A-04 per seed, then S0-A-06 over seeds;
- splits the sliced arm's gap into the parts the comparison arms separate;
- states the Gate B outcomes that PLAN section 5 defines.

As at Gate A, the numbers come from run logs only, mechanically, and missing runs are reported as missing, never as passes.

## What Changed

| File | Description |
|---|---|
| `scripts/analyze_task_b.py` | Collects the completed Task B matrix runs and writes `results/task_b_gate_b.md`. |
| `tests/test_analyze_task_b.py` | Collection, verdicts and decomposition on synthetic run folders. |
| `RESULTS.md` | The Task B entry and the Gate B framing. |

## Implementation Approach

- **Run selection.** A run belongs to the analysis when its log has a `final` record and a last `end` record with status `completed`.
  - The arm comes from the run name: `taskB-central`, `taskB-sliced-coverage`, `taskB-partial`, `taskB-fullavg`.
  - Learning checks, smoke runs and unfinished folders never match.
  - Two completed runs for the same arm and seed are refused by name, not silently chosen.
- **Per run:** test bits per character on the whole test split (the `final` record), final validation bits per character, expert usage on the test split, commit and dirty flag, hours.
- **Per seed:** each arm's relative gap to the centralized run with the same seed.
  - S0-A-04 is evaluated for the sliced arm, the method under test; the other arms diagnose.
  - S0-A-06 requires S0-A-04 on every seed.
- **Decomposition, per seed.** The sliced arm's gap is split into three steps, each defined by two arms that differ in one thing:
  - local averaging: full-model averaging against centralized;
  - partial updates: partial update against full-model averaging;
  - masked routing: sliced against partial update.
- **Report.** The criteria verdict, the per-seed table, the decomposition, expert usage, and PLAN section 5's Gate B outcomes. The decision itself is the owner's.

## Mathematical / Statistical Details

Let b_a,s be the test bits per character of arm a on seed s, with c = centralized.

- **Relative gap:** g_a,s = (b_a,s − b_c,s) / b_c,s. S0-A-04 on seed s: g_sliced,s ≤ 0.05.
- **Decomposition (exact, additive in bits per character):**

  b_sliced − b_c = (b_full − b_c) + (b_partial − b_full) + (b_sliced − b_partial)

  Each term is also reported relative to b_c,s, so the three shares sum to g_sliced,s.
- **Across seeds:** the mean and the range (minimum to maximum) of each quantity. With three seeds no standard error is claimed; the per-seed values are shown.

## Design Decisions

| Decision | Chosen | Alternatives | Decided by |
|---|---|---|---|
| Arm for S0-A-04 | Sliced (the method) | Every simulated arm | SRS 4.4: the criterion concerns the merged sliced model |
| Decomposition order | Centralized, full averaging, partial update, sliced | Other orders of the same steps | Engineering default: each step adds one restriction, the order PLAN step 7 laid out |
| Gate B wording | PLAN section 5's three outcomes, with no "moderate" threshold chosen | A numeric threshold | The owner's: PLAN section 5 leaves "moderate" and "large" undefined |

## Verification

- **Tests:** `python -m pytest tests/test_analyze_task_b.py`, 6 passed. They cover:
  - a full matrix failing S0-A-04, with the three decomposition steps summing exactly to the sliced gap;
  - a pass needing every seed;
  - missing runs giving "incomplete", never a pass;
  - run selection ignoring unfinished folders and other names, and refusing duplicates by name;
  - expert usage and resume counts;
  - the written report.
- **On 11 of 12 runs** (before run 12 finished), the report marked seed 19's full-averaging run as missing and its decomposition as n/a.
- **Final report:** `python -m scripts.analyze_task_b` at commit `ee2a7dd`, clean tree, on all 12 completed runs, written to `results/task_b_gate_b.md`.
- **Cross-check:** every test value in the report matches the per-run figures recorded in `RESULTS.md` as each run finished. Those were read from the same logs by separate one-off scripts.

**Not tested:** significance beyond three seeds (per-seed values are reported instead of a test).

## Related Docs

- `docs/implementations/2026-10-09-task-b-runs.md` (part b)
- `docs/PLAN.md`: section 5 (Gate B)
- `docs/SRS.md`: section 4.4, D25 to D27
