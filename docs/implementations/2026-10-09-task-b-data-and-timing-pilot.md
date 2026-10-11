# 2026-10-09 · Task B: text8 data, bits per character, and the timing pilot (PLAN step 10, part a)

| | |
|---|---|
| PLAN step | 10 · Task B on text8, part a: everything needed to choose a model size and budget (SRS D25) |
| Branch | `stage0/10-task-b` |
| SRS requirements | S0-F-19, S0-F-20 (bits per character), S0-N-02 (20M to 50M parameters), S0-A-04; decisions D25 |
| Status | Implemented and run; timing pilot recorded in `RESULTS.md`; size and budget await the owner |

## Problem / Motivation

The owner decided on 2026-10-08 (D25):

- Task B runs four arms on seeds 7, 11 and 19: centralized, sliced (Gate A main setting), full-model averaging and partial update.
- A timing pilot of three model sizes comes first.
- A size and compute budget are then proposed for the owner's approval.

Nothing for Task B exists yet. Part a builds what the pilot needs, the same parts the runs will use:

- the text8 data path;
- the bits-per-character evaluation;
- the pilot itself.

Part b, the run scripts and the run matrix, is planned after the owner approves a size and budget.

## What Changed

As planned, plus `cassandra_chorus/paths.py` (`data_root`, from `CHORUS_DATA_DIR`), `.gitignore` (`/data/`) and `scripts/ops/launch_visible.ps1` (`-DataDir`). The pilot report is `results/task_b_timing_pilot.md`.

| File | Description |
|---|---|
| `cassandra_chorus/data/text8.py` | `Text8Section` (file path, expected SHA-256, context length, split bounds); loading with a hash check; character encoding; random training windows; non-overlapping evaluation windows. |
| `cassandra_chorus/metrics/task_b.py` | `evaluate_bpc`: bits per character of a model on a split, over non-overlapping windows. |
| `scripts/pilot_task_b_timing.py` | Times the three sizes in every worker mode on real text8 batches and writes `results/task_b_timing_pilot.md`. |
| `configs/task_b/pilot.toml` | The pilot's configuration. |
| `tests/test_text8.py`, `tests/test_metrics_task_b.py` | Tests below. |
| `RESULTS.md` | The pilot's entry and the size and budget proposal. |

## Implementation Approach

### Data

- **Source.** The parent project's local copy of text8 (`CASSANDRA/experiments/tiny_language_lab/corpus/text8/text8`): 100,000,000 characters, alphabet a to z plus space. No download is needed.
- **Location and check.**
  - The file is copied once to a data folder outside OneDrive (`C:\Users\senso\chorus-data\text8`) and never modified.
  - The configuration carries its SHA-256, `6e890197040d37d85beb962ae1f041ff1d9a9ca8d20c7d99c85027eebf51dca7`, measured on 2026-10-09. Loading refuses a file whose hash differs.
- **Splits.** The conventional ones, as in the parent project: train 0 to 90M, validation 90M to 95M, test 95M to 100M characters.
- **Encoding.** Space is 0 and a to z are 1 to 26 (vocabulary 27). The whole corpus is held as a 100 MB tensor of bytes.
- **Training batches.** Each sequence is a window of L + 1 characters starting at a uniformly random offset in the train split: inputs are the first L, targets the last L. Offsets are drawn with replacement from a generator seeded per worker and round, as in Task A (`derive_seed`). A worker therefore sees its own stream, and runs are reproducible from configuration and seed.
- **Context.** L = 256 characters, the parent model's context and the step 2 sizing.

### Bits per character

- **Windows.** The split is cut into non-overlapping windows of L inputs and L targets, and the context is reset at each window. On the 5M-character test split that is 19,531 windows and 4,999,936 scored characters, the parent project's protocol, so the numbers are comparable with its 1.336.
- **Metric.** bits per character = total cross-entropy in nats over every scored character, divided by (scored characters × ln 2).
- **When.** The test split is used once per run, at the end (S0-A-04). A fixed slice of the validation split (the first 1M characters, 3,906 windows) gives the learning curve during training.

### Timing pilot

Configurations, all with 6 layers, 8 experts per layer, k = 2, context 256, vocabulary 27, sparse dispatch (decided for Task B on 2026-10-07):

| Name | Width | Heads | Expert hidden | Parameters |
|---|---|---|---|---|
| small | 256 | 4 | 512 | 20,476,672 |
| medium | 320 | 5 | 640 | 31,985,600 |
| large | 384 | 6 | 768 | 46,050,432 |

For each configuration the pilot measures, on real text8 batches:

1. **Centralized step:** the full model, all experts trainable.
2. **Sliced worker step:** a slice model holding 4 of 8 experts, routing masked to them.
3. **Partial-update worker step:** the full model, routing over all 8, 4 experts trainable.
4. **Full-averaging worker step:** the full model, everything trainable. Same work as centralized; timed once to confirm.
5. **Merge** of 4 worker results.
6. **One full test-split evaluation.**

Each step time is the median of 50 optimizer steps after 10 warm-up steps. Peak GPU memory is recorded too. Two batch sizes are timed, 32 × 256 and 64 × 256. Every timing runs with keep-awake held, and the pilot's configuration, environment and results are logged as a run (S0-N-08).

### From timings to a proposal

The proposal states:

- the model size;
- the batch size;
- the total number of steps S, for centralized and, by D17, for each arm;
- for the sliced arms, R = S / (N × H) with the Gate A setting N = 4, H = 125;
- the estimated hours per run and for the matrix of 12 runs.

A short learning check is proposed with it. It is not part of the pilot.

## Mathematical / Statistical Details

- **Bits per character:** bpc = (Σ over scored characters of −ln p(correct character)) / (n_scored · ln 2).
- **Characters per step:** B × L. At 32 × 256 that is 8,192.
- **Run time estimate:** S × (step time) + (evaluations) × (evaluation time). Merge time × R is added for the sliced arms.
- **Equal compute (D17):** N × H × R = S worker steps of the same batch size.

## Design Decisions

| Decision | Chosen | Alternatives | Decided by |
|---|---|---|---|
| Arms, seeds, pilot first | As in D25 | | Owner, 2026-10-08 |
| Dispatch | Sparse | Dense (E/k times the expert compute) | Owner, 2026-10-07 |
| Data source | Parent's local copy, hash-checked | Download | Engineering default: no download needed, and the same file as the parent's numbers |
| Evaluation protocol | Parent's: non-overlapping 256-character windows, full test split | Sliding windows (lower bpc, slower) | Engineering default: comparable with CASSANDRA's 1.336 |
| Sizes timed | The three of D25 | | Owner, 2026-10-08 |
| Precision and attention kernel | fp32 with the explicit (deterministic) attention path only, as in Task A | Also time bf16 mixed precision; also time fused attention (non-deterministic backward) | Owner, 2026-10-09: every Task B run stays reproducible bit for bit from configuration and seed |

## Verification

- **Tests:** `python -m pytest -q`, 260 passed, CPU and GPU, at `51b8a91`. Six new tests use a synthetic corpus with known answers:
  - hash, length and alphabet refusals;
  - encoding and split bounds;
  - training windows that are shifted copies inside the train split;
  - reproducible sampling;
  - evaluation windows that tile the split, scoring every character once;
  - bits per character of a uniform model equal to log₂ 27, and of an oracle near 0.
- **Real corpus:** it loads in 2.5 s, hash verified. It has 19,531 test windows (4,999,936 scored characters, the parent project's count) and 3,906 windows in the first 1M validation characters.
- **Smoke run:** one size, a few steps, before the full pilot. It caught a measurement flaw: with the centralized model left on the GPU, worker peak memory included it. The global model now stays on the CPU while workers are timed.
- **Pilot:** run `20261009T044556Z_taskB-timing-pilot_s7`, 917 s, at `51b8a91` with a clean tree; see `RESULTS.md`.
  - Untrained test bits per character: 4.85 to 4.96, near the uniform log₂ 27 = 4.75, as expected for a random initialization.
  - 25 mains drop-outs overlapped 17 of the 24 timings, so the medians are inflated. Minima and medians are both reported.

**Not tested:** training on text8; the Task B run scripts (part b); throughput under a stable mains supply.

## Related Docs

- `docs/SRS.md`: S0-F-19, S0-N-02, S0-A-04, D17, D25
- `docs/PLAN.md`: step 10
- `docs/implementations/2026-10-07-moe-transformer.md`: sparse dispatch, determinism, the step 2 footprint (46M at 212 ms per step, 3,423 MiB)
- Parent project: `experiments/tiny_language_lab/eval_text8.py` (its test protocol)
