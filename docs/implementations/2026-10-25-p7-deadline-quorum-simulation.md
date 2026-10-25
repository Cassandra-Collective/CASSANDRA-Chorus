# 2026-10-25: P7 deadline-quorum rounds in the simulation harness

| | |
|---|---|
| PLAN step | Stage 0 simulation extension; system study P7; #79 |
| Branch | `exp/79-p7-deadline-quorum` |
| SRS requirements | D39, D11, D12, D17, D19; S0-F-04 to S0-F-12, S0-N-04, S0-N-05 |
| Status | Planned before code. Reading registered before any P7 run. |

Copied from `_TEMPLATE.md`. This document is committed alone before code.

## Problem / Motivation

Stage 0 does not test deadline-quorum averaging with three to five peers,
mid-round departures or loss of one or both holders. P7 supplies evidence
for AD-5 (#36) and Gate N1b's definition, AD-12 (#43). This task supplies
the plan, tested code and an unrun GPU queue. Runs and results come later.

Base: origin/main a30dd6a, fresh worktree outside OneDrive. The task's
explicit instructions override CONTRIBUTING section 3 on issue comments,
owner questions and closing keywords: no issue comments, labels or assignments;
one draft PR with `Refs #79`; unsettled choices remain open for the owner.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-p7-deadline-quorum-simulation.md` | Plan and registered reading. |
| `cassandra_chorus/sim/harness.py` | Opt-in settings, validation and optional checkpoint metadata. |
| `cassandra_chorus/sim/deadline.py` | Pure replayable churn, holder interventions, timing and counted sets. |
| `cassandra_chorus/sim/p7.py` | Round execution, centralized continuation and holder quality diagnostics. |
| `scripts/train_task_b_sliced.py` | Select P7, log counters and resume its state; retain the legacy arithmetic. |
| `tests/test_p7.py` | CPU protocol, accounting, configuration and features-off regression tests. |
| `tests/test_p7_scripts.py` | Tiny CPU pipeline and resume checks. |
| `configs/task_b/p7.toml` | Task B experimental settings for review. |
| `configs/task_b/p7-churn.toml` | Hash-pinned common churn and intervention tape. |
| `configs/queues/p7_deadline_quorum.toml` | Later GPU work for seeds 7, 11 and 19, not launched here. |

## Implementation Approach

### Opt-in boundary and contracts

`SimSection.round_mode` defaults to `legacy`. Existing configurations retain
their training, data streams, worker order, merge and learning-rate path.
New defaults are inert, but adding resolved fields changes **every config
hash containing SimSection**, including configurations with features off.
Old checkpoints fail the existing hash check. There is no hash workaround.

Pure timing functions take settings, a validated tape, seed and round, and
return membership, executed steps and posted/counted sets. They do not train,
sleep, mutate model/optimizer state or use the process RNG. Tape loading reads
TOML and validates identities, transitions, offsets and SHA-256. Runs keep a
copy; resume verifies that copy instead of following a changed source file.

The P7 executor takes global state, assignments, timing and a batch callback,
executes even partial or late steps, and merges only complete counted updates
through the existing merge. It returns state, reports, worker records and
counters. A subquorum round merges an empty list, preserving global values
and outer velocity. Optional checkpoint metadata stores counters, synthetic
elapsed time, synchronous retry position and centralized AdamW state. Legacy
checkpoint calls retain their defaults. Resume must reproduce all of these.

### Time model

Synthetic units set the reference worker to one optimizer step per unit.
A dedicated derived RNG for `(seed, worker, tape round)` draws training speed
uniformly in `[speed_min, speed_max]` steps/unit and upload duration uniformly
in `[upload_min, upload_max]`. The proposal uses `[0.75,1.25]`, `[1,8]`,
H=100, D=110, L=160, g=10, and synchronous timeout 200. These are synthetic
distributions, not measurements of homes. All timings and lateness are logged.

Full training finishes at H/speed and posts at H/speed+upload. Exactly at D
is on time. A departure during training or upload loses the update. No partial
update is merged. In deadline mode, training is cancelled at L-g; late work
never enters a later round. Grace reserves publication time and never extends
D. Only completed optimizer steps count. This cancellation model is open for
the owner; publication and network transfers themselves are not simulated.

Deadline rounds advance by L. Synchronous mode waits for every assigned ready
worker until timeout; incomplete attempts abort with an empty counted set.
The next tape slot retries the assignment and local LR position. Its duration
is at least L, or close+g when longer. Timeout 200 is a proposal, not AD-6.

### Replayable churn and holder drops

TOML `[[event]]` records have zero-based `round`, round-relative `at`, `worker`
and `action` (`depart` or `arrive`). All workers start online. Changes persist;
offset-zero events change readiness immediately. Mid-round arrivals work only
next round. A mid-round departure loses the current update, even if that peer
returns later in the round. Impossible or duplicate transitions are rejected.
The identical slot-indexed tape is applied to every arm. It does not assert
identical absolute UTC times across arms with different slot durations.

`[[holder_drop]]` records have round, offset, layer, expert and `remaining`
(1 or 0). Resolve against the full-roster reference rolling assignment for
that tape slot, independently of the arm; the target must have two holders.
Remove the first one or both in worker order for that slot only. Apply the
same resolved worker failures to all arms, including centralized. Record
nominal counts, counts after interventions and actual counted holders
separately. Churn, lateness or quorum failure can reduce counts further.
A synchronous retry can have an older assignment, so its actual target counts
must be read from logs, not inferred from the reference intervention label.

Use eight experts, total capacity sixteen: `(6,5,5)`, `(4,4,4,4)` and
`(4,3,3,3,3)` for three, four and five workers. Rolling windows give exactly
two nominal holders everywhere. Fixed-roster assignments do not rebalance
away a fault. This holder-loss stress assignment is open for the owner, not
a full dynamic ready-set allocation. At zero counted holders, the expert,
holder-only router row and their outer state retain their existing values.

### Arms and diagnostics

Queue deadline Q_min=1, deadline Q_min=2, synchronous and centralized for each
peer count and seed. The Q_min set is a proposal for AD-5. Propose plain outer
averaging for the distributed arms; AD-12 remains open. Nesterov remains
supported and is tested for empty-quorum and absent-holder preservation.

Centralized is one full model and one persistent AdamW optimizer, with no
averaging. It consumes the same seeded worker batch streams in worker order
and the same available step counts. Partial work is retained immediately;
there is no update upload to lose. Its synthetic time charges serial training
and idle slots. This availability comparator and time interpretation are open
for the owner, not a measured networked centralized service. Centralized LR
uses actual executed steps over the offered total; distributed LR uses the
original local trajectory, repeated after synchronous aborts. State this
optimizer/schedule difference with comparisons.

Use the Stage 0 Task B model (46,050,432 parameters), text8 checksum/splits,
batch 32, context 256, balance coefficient 0.01 and seeds 7, 11, 19. Offer
24,000 steps per arm: H=100 with 80, 60 or 48 slots for 3, 4 or 5 peers.
Record actual steps run and merged, both token equivalents, simulated elapsed
time and host execution seconds. Offered compute is not actual spent compute.
Equal steps are Stage 0's proxy, not equal FLOPs for full versus sliced models.

Holder quality is conditional validation BPC on positions routed to each expert
with zero or one counted holder, with scored counts and ordinary routing usage.
Hooks observe existing MoE selections, never change routing, and are removed
even on errors. This is the current full model on each expert's routed
population, not that expert's isolated causal quality. Changing populations
are a limitation. Use the same validation prefix in every arm. Final test BPC
is descriptive and never selects Q_min.

## Mathematical / Statistical Details

Let v_i be speed, u_i upload time, a_i the earliest departure/intervention,
C the cancellation boundary. Executed steps are
`h_i = min(H, floor(v_i * min(a_i,C)))`, or zero if not ready. A full post
requires h_i=H and `H/v_i+u_i < a_i` (departure wins a tie). Deadline candidates
also require post<=D. S_t is that set when its size>=Q_min, else empty.
Synchronous S_t contains all assigned ready workers only when every one posts
by timeout, else empty. Results enter merge in worker ID order. Existing
example-weighted float64 averaging is unchanged.

Steps run sum all h_i. Steps merged sum H over S_t. Aborted/late/partial work
costs compute but contributes no merged steps. Centralized retained steps equal
steps run. Tokens multiply steps by batch_size*grad_accum*context_length.
Lateness is signed post-D; missing posts carry a reason. Synthetic time never
uses measured host step time.

### Pre-registered reading, before any run

1. **Primary proposal:** validation BPC at 8,000 actual steps run, equivalently
   65,536,000 spent characters. Report deadline minus synchronous and deadline
   minus centralized BPC for each seed, peer count and Q_min, all three paired
   differences, mean and range. No small-sample significance claim.
2. Report the same comparisons at 8,000 actual steps merged/retained, waste
   fraction, empty-quorum and abort rates, lateness, realized holders and time
   to the common budget. Plot BPC against both compute axes and simulated
   wall time. Equal spent tokens is primary, equal wall time secondary. Host
   seconds measure the sequential simulator, not distributed speedup.
3. Evaluation is at round boundaries. At a common coordinate linearly
   interpolate the two bracketing validation observations, report both raw
   points and bracket width. Use the last observation at a repeated coordinate.
   Never extrapolate. No bracket means unavailable, not a win. This curve
   estimate is not an exact-budget trained checkpoint. Interpolation versus
   exact-budget continuation is open for the owner before queue launch.
4. For each holder intervention report before/at/after BPC, conditional BPC
   and its scored count, realized holders and the next two rounds' recovery.
   Separate nominal intervention counts from counted-set counts. Missing
   observations never become zero loss.
5. If Q_min=1 improves availability but worsens primary BPC/recovery consistently
   across seeds, review Q_min=2. If Q_min=2 wastes more work without consistent
   quality benefit, review Q_min=1. Mixed signs or unavailable budgets leave
   AD-5 unresolved. A reversal between spent/merged axes exposes discarded
   work; a reversal at equal wall time exposes a throughput tradeoff. Neither
   settles AD-12 without an owner-set allowance.
6. Better BPC only supports a candidate gate definition. Worse BPC identifies
   a failure to explain. No outcome establishes live-network guarantees,
   post-SFT quality, a gate tolerance or a final optimizer. These stay open.

**Inference:** the supplied calibration is about two hours per 20,000-step
Task B run on the RTX 4070 Laptop (2026-10-10 run folders; also RESULTS.md's
Task B entries). Scaling gives 2.4 hours per 24,000-step run, 36 queued runs
(3 seeds x 3 peer counts x 4 arms), about 86.4 GPU hours before extra
validation/checkpoint/availability effects. Reserve roughly 90 to 140 GPU hours
(four to six days). This is not measured runtime.

## Design Decisions

- Engineering boundary: simulation and Task B script only; no coordinator,
  merge, SRS, ROADMAP or ARCHITECTURE edits. Supporting tests/configs are in scope.
- Engineering defaults: separate opt-in path, derived RNGs, bounded work with
  no cross-round leftovers, pinned tape, replayable checkpoints.
- **Open for the owner:** AD-5 Q_min ({1,2}); AD-12 outer optimizer (plain),
  primary spent-token axis, 8,000-step coordinate, interpolation or exact-budget
  continuation, quality allowance and final Gate N1b definition.
- **Open for the owner:** timing distributions, cancellation/grace model,
  synchronous timeout, fixed-roster stress assignment, reference-tape injections
  during retries, centralized availability/time comparator and conditional-BPC
  diagnostic. These proposals do not establish new protocol rules.
- No P7 run here. Owner review of this reading precedes later GPU work.

## Verification

Baseline `python -m pytest` on untouched a30dd6a: **339 passed**, no skips or
failures, 2 expected warning-capture warnings, 371.34 seconds. Environment: Windows 11, Python
3.13.14, PyTorch 2.12.1+cu126, NumPy 2.4.4, pytest 9.0.2; RTX 4070 Laptop GPU
available. The baseline passed before implementation.

Planned: complete suite; bit-for-bit tiny CPU comparison with the original
round loop (including Nesterov velocity); seed/file replay, invalid tapes,
exact deadline/departure boundaries, late exclusion, nonempty subquorum state
invariance, holder/intervention/counted counts; tiny CPU pipelines/resume;
queue parse without launch; layering and scope checks; git diff --check;
scan every touched file for U+2013/U+2014. Fill final observed counts here.

No P7 run was made, so nothing about deadline-quorum quality is known yet.
CPU smoke uses tiny models, synthetic text and only a few steps. Existing
suite GPU tests are tests, not P7 experiments. No new corpus is downloaded.

**Not tested:** P7 GPU training/quality comparisons, real transport/publication,
home timing, dynamic ready-set allocation, post-SFT behaviour or AD-5/AD-12.
GPU runs, results and the RESULTS.md entry come later.

Stop if the untouched baseline fails, features-off equality cannot be achieved,
or a coordinator/merge change is needed. Record the finding here and in the PR.

## Related Docs

- [#79](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/79),
  [AD-5 #36](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/36),
  [AD-12 #43](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/43).
- [CONTRIBUTING](../../CONTRIBUTING.md), sections 3, 4, 5, 7, 8.
- [Architecture](../ARCHITECTURE.md), sections 6, 7, 8, 14.
- [System study](../research/2026-10-13-system-study-report.md), sections 5, 6 (P7).
- [Harness](2026-10-08-simulation-harness.md),
  [Task B runs](2026-10-09-task-b-runs.md), [results](../../RESULTS.md).
