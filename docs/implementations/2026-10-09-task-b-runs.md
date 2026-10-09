# 2026-10-09 · Task B: run scripts, learning check and the run matrix (PLAN step 10, part b)

| | |
|---|---|
| PLAN step | 10 · Task B on text8, part b |
| Branch | `stage0/10-task-b` |
| SRS requirements | S0-F-13, S0-F-14, S0-F-19, S0-F-20, S0-F-26, S0-A-04, S0-A-06; decisions D17, D25, D26 |
| Status | Planned |

## Problem / Motivation

The owner fixed the Task B design on 2026-10-08 and 2026-10-09:

- **D25:** four arms, seeds 7, 11 and 19.
- **D26:**
  - the 46.1M model;
  - 20,000 steps of 32 × 256 characters per run;
  - the Gate A setting for the simulated arms (N = 4, capacity 4, H = 125, so R = 40);
  - a 2,000-step centralized learning check first.

Part b builds the two run scripts, runs the learning check, and then the 12-run matrix. The matrix analysis and the S0-A-04 verdict follow as part c.

## What Changed

To be completed after implementation. Planned:

| File | Description |
|---|---|
| `scripts/train_task_b_centralized.py` | Centralized training on text8: validation curve every `eval_every` steps, test bits per character at the end, final model saved. |
| `scripts/train_task_b_sliced.py` | The simulated arms on text8 (`sim.mode` sliced, partial or full), with the step 6 harness: per-round slices, workers, merge, checkpoint, `--resume`. |
| `configs/task_b/centralized.toml`, `configs/task_b/sliced.toml` | The D26 settings. |
| `configs/queues/task_b_matrix.toml` | The 12 runs. |
| `tests/test_task_b_scripts.py` | End-to-end on CPU against a tiny synthetic corpus, resume identity, and a check that the configurations match D25 and D26. |

## Implementation Approach

The scripts mirror the Task A pair (`train_task_a_centralized.py`, `train_task_a_sliced.py`), which have tested resume and logging. Only the data and the evaluation differ:

- **Batches:**
  - centralized: `Text8.sample` from a generator seeded by `derive_seed(seed, "task_b/train")`;
  - workers: one stream per worker and round, `data_generator(seed, worker, round)` as in Task A.
- **Evaluation:**
  - learning curve: bits per character on the first 1M validation characters, every 1,000 steps centralized, and after every merge in the simulated arms;
  - S0-A-04: test bits per character once, at the end, on the whole test split.
- **Unchanged from Task A:** ops (preflight, keep-awake, power log), run logs and seeds.
- **Not carried over:** Task A's map-routing diagnostics, which have no meaning without maps. Expert usage per layer is still logged from the model's own counts.

The learning check is the centralized script with `train.steps = 2000` and `train.eval_every = 250`, at commit-clean code. It checks two things:

- the validation curve falls well below the untrained 4.96 bits per character;
- the loss stays finite and falls smoothly.

If either fails, the owner hears before any matrix run.

## Mathematical / Statistical Details

- **Equal compute (D17):** 4 workers × 125 steps × 40 rounds = 20,000 worker steps of 32 sequences, the same as the centralized run's 20,000 steps.
- **Bits per character:** as in part a.
- **S0-A-04:** (bpc_sliced − bpc_centralized) / bpc_centralized ≤ 0.05, per seed (S0-A-06).

## Design Decisions

| Decision | Chosen | Alternatives | Decided by |
|---|---|---|---|
| Size, budget, arms, learning check | As in D25 and D26 | | Owner, 2026-10-08 and 2026-10-09 |
| Script structure | Separate Task B scripts mirroring Task A's | One shared driver for both tasks | Engineering default: Task A's scripts are verified (bitwise resume) and stay untouched; a shared driver can come later |
| Curve frequency | Every 1,000 steps centralized; every round (500 worker steps) in the simulated arms | Every round for all | Engineering default: about 20 s per evaluation; cost is in the part a projections |

## Verification

To be completed after implementation.

## Related Docs

- `docs/implementations/2026-10-09-task-b-data-and-timing-pilot.md` (part a)
- `docs/implementations/2026-10-08-simulation-harness.md` (the harness, resume)
- `docs/SRS.md`: D17, D25, D26, S0-A-04
