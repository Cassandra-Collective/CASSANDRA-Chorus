# 2026-10-13 · Averaging gap, batch 1: what the +6.1% is made of

| | |
|---|---|
| PLAN step | 11 (sweeps), first batch; reopened after Stage 0's close-out as part of reconsidering the architecture (D28) |
| Branch | `stage0/11-sweeps` |
| SRS requirements | S0-F-23 (sweeps), S0-F-10 (outer optimizer), S0-F-20 (bits per character), S0-N-07 (state limits) |
| Status | Analysis 1 implemented and verified (2026-10-13). Analysis 2, the code changes and the four runs are planned; the runs wait for the laptop's charger service (owner decision 2026-10-13) |

## Problem / Motivation

In Stage 0's Task B, full-model local averaging ended **+6.1%** in test bits per character behind centralized training (seeds 7, 11, 19; `docs/stage0-report.md` §3.3). It is the largest of the three measured costs, and every Chorus design pays it. The literature report (`docs/research/2026-10-11-stage0-literature-report.md`, §3.1) found that every published gap near our setting is smaller. It names several handicaps that papers measure one at a time:

1. our centralized baseline takes 4× more sequential optimizer steps (20,000 against 5,000 per worker);
2. we use plain averaging, with no outer optimizer;
3. our model is small;
4. H = 125 over 40 rounds;
5. AdamW is reset every round.

No paper splits a gap like ours among these, and the report's section 6 lists the runs our harness could use to do it. This batch takes the cheapest and most informative of them.

The product target is now a local assistant trained from scratch by Chorus (owner, 2026-10-13). Distributed pretraining is on its critical path, so the averaging cost has to be understood before any networked stage.

## Scope (owner decisions, 2026-10-13)

- **Batch 1 only:** the analyses below, two centralized baselines, two outer optimizers, and (added by the owner after analysis 1) one run that synchronizes more often during the final learning-rate decay. Whether to run the H sweep and the keep-against-reset AdamW comparison is decided after seeing these.
- **Re-scoring (analysis 2) runs on an evening session**, not during the day (owner, 2026-10-13).
- **Seed 7 only** for the runs in this batch.
- **No long training runs until the laptop's charger or battery handover is serviced** (`docs/stage0-closeout.md` §3.2). Analyses of existing logs, code changes and tests can proceed now.

## What Changed (planned)

| File | Description |
|---|---|
| `scripts/analyze_task_b_curves.py` | New. Reads the existing Task B run logs. For each seed it pairs the centralized validation curve with the merged models' validation curves at equal compute, and writes the gap at each point. No GPU. |
| `results/task_b_gap_curves.md` | New. The table produced by that script. |
| `cassandra_chorus/metrics/task_b.py` | Adds a sliding-window option to the bits-per-character evaluation; the default stays the non-overlapping protocol. |
| `scripts/rescore_task_b.py` | New. Re-scores saved Task B models on the test split with sliding windows. |
| `results/task_b_rescore.md` | New. Non-overlapping and sliding-window bits per character for the 12 saved Task B models, and the gaps under both. |
| `cassandra_chorus/train/loop.py` | Adds `OptimSection.grad_accum` (default 1, today's behaviour) and an optional per-step loss record in `TrainStats`. |
| `scripts/train_task_b_centralized.py` | Counts characters per step as `batch_size × grad_accum × context`, so accumulation runs log the right data volume. |
| `cassandra_chorus/sim/harness.py` | Adds `SimSection.decay_local_steps` and `round_plan`. |
| `cassandra_chorus/sim/worker.py` | `train_worker` takes an optional explicit start step. |
| `scripts/train_task_b_sliced.py` | Runs the rounds of `round_plan`, and logs each round's `start_step` and `local_steps`. |
| `scripts/train_task_a_sliced.py` | Refuses `decay_local_steps` other than 0. |
| `scripts/analyze_task_b_curves.py` | Uses the logged `start_step` and `local_steps` when present. |
| `cassandra_chorus/data/text8.py` | Adds windows at a given stride, for sliding-window scoring. |
| `configs/queues/sweeps_batch1.toml` | New. The four runs of this batch as overrides of the existing Task B configurations. |
| `tests/` | New tests for accumulation, sliding-window scoring and the curve pairing. |
| `RESULTS.md` | One entry per completed analysis and run. |

## Implementation Approach

**Analysis 1: when does the gap open?** (existing logs, no GPU)

- **Data:** each Task B run logs validation bits per character on the first 1M validation characters.
  - Centralized runs log every 1,000 steps.
  - Simulated runs log after every merge: round r has used 500(r + 1) worker steps in total.
- **Pairing:** match centralized step s with simulated round r where s = 500(r + 1). This gives 20 points per seed and arm, at equal total compute.
- **Output:** the relative gap at each point, for the full-averaging, partial and sliced arms.
- **What it answers:** whether the gap opens early, grows steadily, or appears in the final 20% learning-rate decay, where the centralized model takes 4,000 decay steps and each worker takes 1,000.

**Analysis 2: sliding-window re-scoring** (short GPU use, no training)

- **Protocol:** each test character is scored once, with up to 255 characters of context.
  - The first window scores all its positions.
  - Each later window advances by a stride S and scores only its last S positions.
- **Stride:** S = 64, so every character after the first window sees 192 to 255 characters of context, at about 4× the cost of the current protocol. The current evaluation took 109 s per model, so this is about 7 to 8 minutes per model and about 1.5 hours for all 12.
- **What it answers:** how much our 256-character, context-reset scoring inflates bits per character in each arm, and whether the three gaps change under the fairer protocol. The report could only bound this from Al-Rfou et al.

**Code change 1: gradient accumulation.**
- **What:** with `grad_accum = k`, each optimizer step draws k micro-batches of `batch_size` sequences and back-propagates each loss divided by k. It then clips the summed gradient and steps once.
- **Default:** `grad_accum = 1` keeps the current code path exactly, so existing runs stay reproducible bit for bit.
- **Why it is needed:** batch 128 does not fit in 8 GB. The timing pilot measured 5,945 MiB at batch 64.

**Code change 2: per-step losses.** `OptimSection.log_step_losses` (default off) makes `train_steps` record each optimizer step's loss in `TrainStats.step_losses`, which the run logs already store with the rest of the statistics. It is a logging switch kept in the optimizer section because every training path receives that section. Future runs can then show whether loss jumps after each AdamW reset; the current per-round logs cannot.

**Code change 3: a shorter H during the decay (for B1-5).**

- **Setting:** `SimSection.decay_local_steps` (default 0, meaning off).
- **Round plan:** a new function `round_plan` lays out every round as (first worker step, number of steps). Rounds use `local_steps` until the worker trajectory reaches the decay start (step 4,000 of 5,000), then `decay_local_steps`. With 125 and 25 that is 32 + 40 = 72 rounds, at the same total compute.
- **Validation:** the plan raises an error if the decay start is not a multiple of `local_steps`, or the decay length not a multiple of `decay_local_steps`.
- **Worker:** `train_worker` gains an optional explicit start step, so the learning-rate schedule follows the trajectory exactly. Its default (round × H) keeps every existing run unchanged.
- **Logs:** round records add `start_step` and `local_steps`. The curve analysis uses them when present and the old formula otherwise.
- **Task A:** its script refuses a nonzero `decay_local_steps` rather than ignoring it.

**Code change 4: sliding-window scoring.**

- **API:** `evaluate_bpc(..., stride=None)` keeps the current protocol. A stride S that divides the context length L uses windows starting every S characters: the first scores all L positions, each later one only its last S.
- **Same characters:** this scores exactly the characters the current protocol scores, from the split's second character to n × L, where n is the current number of windows. So the two protocols differ only in context.
- **Expert counts:** not returned in this mode, because the forward pass also routes unscored positions.
- **Script:** `scripts/rescore_task_b.py` loads each saved model and its configuration and writes both scores.

**The four runs** (seed 7, after the laptop is serviced):

| Run | Arm | Settings | Answers |
|---|---|---|---|
| B1-1 | Centralized, batch 128, 5,000 steps | `optim.grad_accum=4`, `train.steps=5000` | The same-step data-parallel reference most papers use |
| B1-2 | Centralized, batch 32, 5,000 steps | `train.steps=5000` | The one-worker floor: a worker training alone on a quarter of the data |
| B1-3 | Full averaging, H = 125, Nesterov outer step | `sim.outer=nesterov`, `sim.outer_lr=0.7`, `sim.outer_momentum=0.9` | Whether DiLoCo's outer step recovers part of the 6.1% |
| B1-4 | Full averaging, H = 125, plain step larger than averaging | `sim.outer=nesterov`, `sim.outer_lr=1.6`, `sim.outer_momentum=0` | Whether a larger outer step without momentum helps |
| B1-5 | Full averaging, H = 125 until the decay, then H = 25 | `sim.decay_local_steps=25` | Whether the gap's widening during the decay (analysis 1) comes from how rarely workers synchronize there |

All four keep everything else from the Stage 0 Task B configurations: model, data, schedule shape, seed and evaluation.

- **Expected time.** Stage 0's Task B re-check under the laptop's power drop-outs ran at about 0.44 s per step of 32 sequences (`RESULTS.md`).
  - B1-1, B1-3 and B1-4 each process 20,000 such batches: about 2.5 to 3 hours each with evaluation.
  - B1-2 processes 5,000: under an hour.
- **Launch:** visibly, with keep-awake held, as in Stage 0.

## Mathematical / Statistical Details

- **Bits per character:** bpc = (total cross-entropy in nats) / (scored characters × ln 2), unchanged. Under the sliding-window protocol the set of scored characters is the same as before (every character after the first of the split); only the context each one sees changes.
- **Relative gap:** gap = bpc(arm) / bpc(centralized) − 1, per seed, as in the Stage 0 report.
- **Gradient accumulation:**
  - **Cross-entropy:** every micro-batch has the same number of scored targets (32 × 256). So the mean of the k micro-batch mean losses equals the mean loss over the whole 128-sequence batch, and its gradient is the sum of the k gradients each divided by k.
  - **Balance loss:** the one difference is the Switch load-balancing loss. It is a product of per-expert token fractions and mean router probabilities computed within each micro-batch, so averaging it over micro-batches is not identical to computing it once over 128 sequences. Its coefficient is 0.01, so the effect is expected to be small; it will be stated with the results.
- **Outer step** (`cassandra_chorus/coordinator/merge.py`, `NesterovOuter`), with Δ = average of the workers' parameters − current parameters:
  - v ← μv + Δ, then θ ← θ + η(Δ + μv).
  - With μ = 0 this is θ ← θ + ηΔ: plain averaging is η = 1, and B1-4 uses η = 1.6.

## Design Decisions

- **Why these four runs first.** They need no new training code apart from accumulation, and together they bound the two handicaps with the strongest published evidence: the baseline type (DiLoCo Table 2) and the outer optimizer (Khaled et al.; Horoi et al.).
- **Outer settings come from the literature, not from tuning.**
  - 0.7 and 0.9 are DiLoCo's values (150M, 8 workers, H = 500).
  - 1.6 is Horoi et al.'s tuned plain outer learning rate (178M, 8 workers, H = 30).
  - Neither was tuned for our setting. The report notes that Nesterov degraded at long local periods in FoMoE, and can be unstable at small scale. A failed run would be informative, not a bug.
- **The learning rate of B1-1 stays at 1e-3.** A larger batch often warrants a higher learning rate, so B1-1 may understate what data parallel can reach. Tuning it would need several runs. That is a stated limitation, not a decision to settle now.
- **Stride 64 for re-scoring.** Stride 1 would score every character with exactly 255 characters of context, at about 256× the current cost (about 8 hours per model). Stride 64 keeps 75% or more of the context for every character at 4× the cost.

## Verification

**Analysis 1, done 2026-10-13.**

- **Tests:** `tests/test_analyze_task_b_curves.py` (4 tests) checks:
  - the step count after each round (`n_workers × local_steps × (r + 1)`);
  - the pairing at equal compute, skipping step 0 and unmatched steps;
  - the mean, minimum and maximum over seeds, end to end through `main`.

  With the existing analysis tests, 10 passed (Python 3.13.14 on the reference laptop, CPU).
- **Run:** on the 12 Stage 0 Task B logs (`C:\Users\senso\chorus-runs`), the script paired all three seeds and 20 points per arm. The result and its reading are in `results/task_b_gap_curves.md` and the `RESULTS.md` entry of 2026-10-13.
- **Spot check:** the per-seed rows were checked by hand against the logs' `eval` and `round` records for seed 7 at 2,000, 16,000 and 20,000 worker steps.

**Still planned:**

- **Accumulation, `grad_accum = 1`:** a fixed seed reproduces an existing short run bit for bit (CPU and CUDA).
- **Accumulation, `grad_accum = 4`:**
  - with the balance loss off, the parameters after one step match a single batch of 4× the size within floating-point tolerance;
  - with it on, the difference is measured and reported.
- **Sliding window:** with stride equal to the context length, the score equals the current protocol exactly. With any stride, every character after the first is scored exactly once.
- **Curve pairing:** a test on a synthetic log checks that step s pairs with round s/500 − 1.
- **Full suite:** the 277 existing tests still pass.
- **Results:** each analysis and run goes into `RESULTS.md` with its commit, hardware, seed and wall time, stating what was not tested.

**Not tested in this batch:**
- other seeds;
- the H sweep;
- keeping AdamW state across rounds;
- learning-rate tuning for the baselines;
- the partial and sliced arms with an outer optimizer.

## Related Docs

- `docs/research/2026-10-11-stage0-literature-report.md`, §3.1 and §6 (gaps 1, 2, 13, 14 and 18)
- `docs/stage0-report.md` §3.3 and §5; `docs/stage0-closeout.md` §3.2
- `docs/implementations/2026-10-08-simulation-harness.md`, `2026-10-09-task-b-data-and-timing-pilot.md`, `2026-10-11-task-b-analysis.md`
