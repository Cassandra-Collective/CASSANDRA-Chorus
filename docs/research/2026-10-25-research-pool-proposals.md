# Research-pool proposals from the literature gaps

Date: 2026-10-25. Proposal for [#105](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/105). Base: `a30dd6a`. [Implementation plan](../implementations/2026-10-25-research-pool-proposals.md).

This inventory covers every numbered item in [the literature report](2026-10-11-stage0-literature-report.md), section 6, plus each item in its final new-code list and the appended centralized-sensitivity question. G01-G20 preserve the report's numbering. N01-N14 cover the additional list. They are proposals for separate committed plans, not authorization to train or owner decisions. The remedy evidence and candidate designs are in [#104, draft PR #128](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/pull/128).

## Common run and reading contract

Unless stated otherwise, use `configs/task_b/sliced.toml` and `configs/task_b/centralized.toml`: text8, 46,050,432 parameters, top-2 of 8, batch 32, context 256, seeds **7, 11, 19**. Simulated defaults: four workers, capacity 4, coverage assignment, H=125, 40 rounds, `sim.equal_compute_steps=20000`, plain averaging, fresh AdamW, zero dropout and skew. Preserve the remaining configuration, data hashes and evaluation. Set `run.seed` and a unique `run.name` for each run. Record actual hardware and parameter counts with eventual results; no hardware throughput is assumed here.

C means centralized with `train.steps=20000`. F means `sim.mode=full, sim.router_rule=all`; P means `partial, all`; S means `sliced, holders`. Use `dP=bpc(P)-bpc(F)`, `dM=bpc(S)-bpc(P)` and each arm's gap to C per seed. State denominators for relative gaps. Equal worker steps or characters are not equal FLOPs. When worker count changes, also report steps per worker, holders, data volume, communication and realized compute.

**Inference:** every numeric grid, proposed setting and run count below is a planning choice, not a published result or a power calculation. Counts include the named controls but exclude C anchors unless explicitly counted. Reuse a control only if configuration, initialization, budget and scoring match. Do not sum rows as independent budgets: several intentionally share runs. All new training screens use seeds 7, 11 and 19. Historical analyses use the same three Stage 0 seeds. The exception is existing #87, whose approved first batch is seed 7 only; any extension needs the owner's decision.

Each **Reading** below is to be fixed in that pool's own committed plan before any run or analysis. A directional training condition means it holds in all three paired seeds. Mixed directions mean no consistent support; missing or failed runs mean incomplete evidence. These screens do not establish significance, equivalence, causation from correlations, or adoption. Open for the owner: practical-effect thresholds and adoption gates. Hardware or numerical failures are retained and reported, not silently replaced with a new seed.

## Harness audit that changes the classification

- [SimSection](../../cassandra_chorus/sim/harness.py) supplies the H, worker, capacity, assignment, outer-step, dropout and decay options below. `make_outer` and `NesterovOuter` accept an outer lr above 1. `sim.capacities` is the per-worker tuple; full and partial modes require `router_rule=all`.
- [Assignment](../../cassandra_chorus/coordinator/assignment.py) with `policy=rolling, rolling_shift=0` pins residency. Shift 1 rotates it. Four workers of capacity 2 give disjoint complete coverage under rolling. A same-subset-for-every-worker policy is not supplied.
- [Task B check](../../scripts/train_task_b_sliced.py) rejects nonzero `sim.skew`: it is defined over Task A's maps. Text8 heterogeneity therefore needs code and a data plan. This is not an existing text8 experiment switch.
- [ModelSection](../../cassandra_chorus/model/transformer.py) already has `balance_coef`, `dropout` and `context_length`; [OptimSection](../../cassandra_chorus/train/loop.py) has `weight_decay`, `grad_accum` and `log_step_losses`. Changing a coefficient does not change balance scope. `dispatch=dense` still computes an MoE; it is not a dense baseline.
- [Worker training](../../cassandra_chorus/sim/worker.py) constructs a fresh optimizer every round. No keep-state or moment-averaging option exists. Round checkpoints retain the latest merged state, not a complete history of local workers.
- Task B's `sim.decay_local_steps` accepts larger as well as smaller H if both phases divide exactly. Thus N11 is now possible without new code. [evaluate_bpc](../../cassandra_chorus/metrics/task_b.py) and [rescore_task_b](../../scripts/rescore_task_b.py) already implement strided scoring. Per-position losses and Task B versions of the Task A routing probes still need analysis code.

## Summary table

Dependencies: **network** means scheduling future distributed pool runs, after #78; it is not proof that the present simulation harness is already a network runner. **Local data** means the owner's laptop artifacts in [closeout section 4](../stage0-closeout.md). **Code** means a separate implementation plan and tests before research runs.

| Gap | Question | Runs or analyses | Dependency | Overlapping issue |
|---|---|---|---|---|
| G01 | H with/without outer momentum? | F, 5 H values x 2 outer modes x 3 seeds | network; G11 for keep-state extension | #88; #87 first |
| G02 | Outer lr at H=125? | F, 8 lr/momentum settings + plain control, 27 runs | network; #87 | #87 B1-3/B1-4 |
| G03 | Momentum changes which cost? | F/P/S x plain/Nesterov, 18 runs | network; G02 | #87; #104 PR #128 |
| G04 | Worker count at fixed total steps? | F/P/S x 2/4/8 workers, 27 runs | network | #104 PR #128 |
| G05 | Holder/fraction effects and masking dose? | Paired P/S worker/capacity grid, 54 runs | network; G04; matched F/C anchors | #104 PR #128 R1 |
| G06 | Assignment variance and persistence? | P/S x four policies, 24 runs | network; G15/G16 diagnostics | #104 PR #128 R2 |
| G07 | Disjoint or overlapping ownership? | P at capacity 2/4 plus F, 9 runs | network; G05 | #104 PR #128 R1 |
| G08 | Data skew versus structural skew? | Task A F/P/S x three skews, 27 runs | network; text8 needs code/data plan | none |
| G09 | Unequal worker capacities? | P/S x uniform/heterogeneous, 12 runs | network | none |
| G10 | Dropout and lost coverage? | F/P/S x three dropout rates, 27 runs | network; realized-compute accounting | none |
| G11 | Keep/reset/average AdamW state? | F x three state rules, then P/S, up to 27 runs | code; network; #87 | #88; N01 |
| G12 | Spikes around resets/merges? | 12 historical logs; optional 9 traced reruns | Local data; absent traces cannot be recovered | none |
| G13 | Evaluation protocol penalty? | 12 models at original/stride 64; optional strides | Local data; position-loss analysis code | #103 |
| G14 | Central steps equivalent to each arm? | 12 logs, 9 paired curve crossings | Local data; G19 for out-of-range targets | #87 curve analysis |
| G15 | Expert interchangeability on text8? | 12 models, routing/removal probes | Local data; Task B probe code | #104 diagnostics |
| G16 | Exposure, usage and quality? | 9 simulated logs plus model probes | Local data; missing train counts need logging | G05/G06 |
| G17 | Routing and update diagnostics? | Historical subset; optional 9 instrumented runs | Local data; intermediate-state/logging code | G11/G15; #104 |
| G18 | Same-step and one-worker baselines? | B1-1/B1-2 in existing queue | network; #78 | #87 |
| G19 | Longer centralized data curve? | C at 20k/40k/80k steps, 9 runs | network; G14 | none |
| G20 | Partial updates at equal FLOPs? | Profile, then matched P and F, 6 full runs | code for accounting; network | #104 PR #128 R3 |
| N01 | Average optimizer moments? | G11 third state arm, no duplicate pool budget | code; G11 | #88 |
| N02 | Iso-C aggregation? | F/P/S x mean/Iso-C, 18 runs | code; network; G02 | none |
| N03 | Does an MoE beat dense here? | C MoE and two dense sizes, 9 runs | dense model code; network | none |
| N04 | Balance coefficient and scope? | 36 coefficient runs, then 21 scope runs | coefficient exists; scope needs code | #104 PR #128 R5 |
| N05 | z-loss under restricted routing? | C/F/P/S x three weights, 36 runs | code; network | none |
| N06 | Frozen initial router weights? | C/F/P/S x learned/frozen, 24 runs | training freeze option; network | none |
| N07 | Character-hash routing? | C/F/P/S x learned/hash, 24 runs | token-aware routing code; network | none |
| N08 | Router fitting after merges? | F/P/S x five fit schedules, 45 runs | code; full-model fitting site; network | #104 deferred candidate |
| N09 | Sigmoid under masking? | C/F/P/S x two gates, 24 runs | code; network | #104 PR #128 R6 |
| N10 | Expert-merging warm-up? | F/P/S x warm-up on/off, 18 runs | code; network | #104 PR #128 R7 |
| N11 | Larger H in final decay? | F/P/S x constant/smaller/larger H, 27 runs | existing Task B option; network | #87 B1-5 |
| N12 | Mix partial and sliced rounds? | P, S, P-then-S, S-then-P plus F, 15 runs | mode-schedule code; network | none |
| N13 | Sequence routing or paths? | C/F/P/S x token/sequence routing, 24 runs | architecture code; network; owner contract | none |
| N14 | Centralized hyperparameter slack? | 8 single-factor configurations, 24 runs | existing options; network | N04 coefficient controls |

## A. New runs, preserving numbered gaps

### G01. Averaging cost as a function of H

**Question:** How does F's bpc respond to H under plain averaging and outer momentum? **Runs:** H=25,50,125,250,500 with `sim.rounds=200,100,40,20,10`, `equal_compute_steps=20000`; plain versus `outer=nesterov, outer_lr=0.7, outer_momentum=0.9`: 30 runs. Use matching C anchors. Existing options; H=1 with fresh AdamW is not the same optimizer as data parallel. **Dependency:** network, #87 completion and #88's pool plan. A kept-state factorial extension depends on G11 code. This proposal is a specification for #88, not a competing run request. **Reading:** if smaller H reduces the F-C gap consistently under a given outer rule, then conclude that more frequent synchronization helps under that state rule; if not, no consistent H benefit is shown. Do not separate H from round count at fixed steps.

### G02. Outer learning rate at H=125

**Question:** Does the outer step need a different lr, including values above 1? **Runs:** F with `outer=nesterov`, lr in 0.4,0.7,1.0,1.6 and momentum in 0,0.9, plus plain F: 27 runs. Existing options; `make_outer` does not cap lr at 1. **Dependency:** network and #87 B1-3/B1-4; reuse their seed-7 results only when settings match. **Reading:** if a pre-specified setting beats plain F in all seeds, then conclude it is a candidate outer setting; if not, no consistent gain is shown. Rank settings on validation only and confirm a selected setting on held-out test without choosing a winner from test scores.

### G03. Outer momentum across all arms

**Question:** Does the same outer rule alter dP or dM as well as averaging? **Runs:** F/P/S under plain versus Nesterov, lr 0.7 and momentum 0.9, H=125: 18 runs. If G02 supplies another setting, freeze that substitution in this plan before running G03. Holder-restricted expert and router-row updates already use the outer step in `coordinator/merge.py`. **Dependency:** network, G02 or its fixed default, #87; compare #104 PR #128. **Reading:** if momentum reduces dP or dM without worsening its preceding arm, then support a remedy for that component; if not, improvement in S alone is not evidence that either component shrank.

### G04. Worker count at fixed total steps

**Question:** What happens to loss and both incremental costs as worker count changes? **Runs:** F/P/S, `n_workers=2,4,8`, capacity 4, H=125, `rounds=80,40,20`, `equal_compute_steps=20000`: 27 runs plus C if unavailable. Existing options. **Dependency:** network and G03 if adopting a changed outer rule; otherwise keep plain. **Reading:** if the gap to C rises consistently with worker count, then conclude that the full fixed-step worker-count package is harmful here; if not, no monotonic package penalty is shown. Holder counts, worker trajectory length and synchronization count also change; this is not a holder-only causal estimate.

### G05. Holders, fraction and masking dose

**Question:** How do partial cost and masking cost vary with visibility, and can their dependence on holders be distinguished from fraction? **Runs:** P/S at workers 4 and 8 crossed with capacities 2,4,6, then P/S at workers 4 with capacities 3,5,7. This is 18 configurations, 54 runs. H=125; use 40 rounds for four workers, 20 for eight. Add F controls for each worker count and C as needed. Existing options; top-k stays 2. Report actual per-round holders, trainable parameters and memory. **Dependency:** network, G04 and #104 R1. **Reading:** if dM increases as capacity shrinks in all seeds, then support a masking dose response; if not, no monotonic response is shown. For P, compare same-capacity/different-worker and same-mean-holder/different-capacity cells separately. If their patterns disagree, conclude that holder count alone is insufficient; if not, call the pattern compatible with a holder explanation, not isolated proof, because fixed global steps also change worker trajectories. A pure holder intervention would require a separately specified update-allocation experiment.

### G06. Assignment policy

**Question:** Does controlling holder variance or residency persistence reduce dP or dM? **Runs:** P/S at capacity 4 under coverage, random, rolling shift 1 and rolling shift 0: 24 runs, with shared F/C anchors. Existing options; pinned assignment is rolling shift 0. An all-workers-same-subset contrast needs a new assignment policy and explicit treatment of unheld experts, so it is not included in these runs. **Dependency:** network; G15/G16 for diagnostics; #104 R2. **Reading:** if rolling or pinned assignment lowers a component in every seed without worse preceding-arm bpc, then support that policy; if not, persistence or variance control is not sufficient in this screen. Random-policy results must report unheld experts, so missing coverage is not mislabelled as only variance.

### G07. Disjoint versus overlapping partial ownership

**Question:** Does SPES-like disjoint ownership have a different partial-update cost? **Runs:** P at capacity 2 versus 4 with rolling shift 1, plus F: 9 runs. Four workers with capacity 2 produce one holder per expert; capacity 4 produces two. Same total worker steps. Existing options. **Dependency:** network, G05; reuse matching cells. **Reading:** if disjoint P has larger dP in all seeds, then conclude the disjoint package is worse here; if not, overlap has no consistent advantage. Fraction and holder count change together, so do not assign the difference to overlap alone.

### G08. Skewed versus IID data

**Question:** Does data heterogeneity interact with structural heterogeneity? **Runs:** first use `configs/task_a/sliced.toml`, keeping that Task A model and budget, with F/P/S and `sim.skew=0,0.5,1`: 27 runs. Existing map-skew options, with Task A accuracy costs and its interchangeability probes, not text8 bpc. **Dependency:** network; text8 conclusions require new sharding/sampling code in `data/text8.py` and `scripts/train_task_b_sliced.py`, with owner-approved corpus labels or a clearly described position-based surrogate. A future text8 extension repeats F/P/S over the same three skew levels with equal aggregate training distribution and matched C. **Reading:** if skew changes the S-P accuracy penalty consistently while the pooled data distribution stays fixed, then support a data-by-structure interaction on Task A; if not, none is shown there. Neither outcome answers the text8 question without that extension.

### G09. Heterogeneous capacities

**Question:** Does unequal per-worker memory capacity matter at the same total expert slots? **Runs:** P/S with uniform capacity 4 versus `sim.capacities=[2,4,4,6]`, rolling shift 1 in both, H=125: 12 runs. Existing per-worker option; clear the tuple for uniform controls. Both assignments have the same total slots and two holders per expert under this rolling construction. **Dependency:** network; G06 controls if identical. **Reading:** if heterogeneity increases dP or dM in all seeds, then conclude that unequal allocation has a cost under this assignment; if not, no consistent cost is shown. This does not simulate slower hardware or different per-worker step budgets.

### G10. Worker dropout

**Question:** How does losing worker updates affect loss and expert coverage? **Runs:** F/P/S with `sim.drop_prob=0,0.1,0.25`: 27 runs, using the existing deterministic dropout stream. Log surviving workers and realized sequences. **Dependency:** network; no new training option, but a compute-matched regularization test would need replacement-work scheduling. **Reading:** if higher dropout increases bpc and unheld-expert rounds consistently, then conclude loss of updates harms this fixed-nominal-budget package; if not, no consistent harm is shown. An improvement is only a dropout association, not evidence of regularization at equal compute: the script skips dropped workers, so realized work is lower.

### G11. AdamW state across rounds

**Question:** Do keeping or averaging moments change the three costs? **Runs:** first F under reset, keep and holder-aware averaged moments at H=125: 9 runs; then the same three state rules in P/S: 18 more. Keep trajectory schedule and all AdamW hyperparameters fixed. **Dependency:** code in `sim/worker.py`, `sim/harness.py`, checkpointing and Task B orchestration; network; #87 then #88. For experts that move workers, specify whether state follows the global expert or worker, how absent experts are treated, and how optimizer step counters align. No such state rule exists today. **Reading:** if keeping or averaging state reduces F-C consistently, then support that rule for averaging; if not, no consistent benefit is shown. Apply dP/dM separately to P/S. This belongs to #88; N01 details its third arm, not another budget.

## B. Analyses of historical artifacts

Every entry here **needs the owner's local data**. The closeout records logs and saved models under `C:\Users\senso\chorus-runs` and text8 under `C:\Users\senso\chorus-data`; these proposals do not claim those artifacts were inspected. Inventory availability before analysis. No value absent from a log can be inferred merely because a newer logging option exists.

### G12. Loss traces around merges and resets

**Question:** Are boundary-adjacent loss spikes visible? **Runs/data:** audit all 12 C/F/P/S logs over the three seeds; read per-round worker mean CE and merged validation bpc. No new training if per-step traces exist. If they do not, mark within-round reset spikes unanswerable historically; a future F/P/S rerun with `optim.log_step_losses=true` needs 9 runs. Compare the first 5 versus last 5 steps of each round under a pre-fixed schedule-phase stratification; a causal reset contrast additionally needs G11 keep-state controls. **Dependency:** needs the owner's local data; existing logging option for reruns; network if rerun. **Reading:** if boundary excess is positive in each seed and diminishes under matched kept-state controls, then support reset-associated spikes; if not, no consistent reset-associated pattern is shown. With round means alone, conclude only that fine-grained evidence is missing, not that spikes are absent.

### G13. Strided re-scoring and position losses

**Question:** Does context-reset scoring change the relative gaps? **Runs/data:** the 12 final models, original scoring versus stride 64 using `scripts/rescore_task_b.py`; seed set remains 7/11/19. This is existing #103, with its original-score tolerance 1e-6 and equal scored-character check. Do not replace its approved stride silently. Optional stride 32 and 1 analyses must be registered separately and stored separately from the resumable stride-64 results. Add per-position CE aggregation in `metrics/task_b.py` or an analysis script; no retraining. The first window has short-prefix positions even at stride 1. **Dependency:** needs the owner's local data and #103's owner laptop session; position analysis needs code. **Reading:** if the paired relative gap changes consistently after re-scoring, then conclude protocol sensitivity of that gap; if not, no consistent change is shown. If only absolute bpc improves, do not claim a distributed-training remedy.

### G14. Equivalent centralized compute

**Question:** How many centralized steps reach each arm's final validation bpc? **Runs/data:** 12 logs; pair nine F/P/S final validation targets with the three C curves. Extend `scripts/analyze_task_b_curves.py` to find the earliest adjacent validation checkpoints bracketing each target and linearly interpolate between those two steps. Also report the bracket, not just the interpolation. No extrapolation; use validation against validation, never final test bpc as a curve target. **Dependency:** needs the owner's local data; existing #87 equal-compute curve analysis, plus new crossing analysis; G19 for targets outside the observed range. **Reading:** if a target is bracketed, then conclude an observed-range estimate of its centralized step equivalent; if not, report a one-sided bound or unavailable crossing. A noisy first crossing does not establish a precise compute multiplier.

### G15. Task B interchangeability probes

**Question:** Do sliced experts remain more interchangeable when measured on characters? **Runs/data:** 12 saved models, fixed validation characters and paired diagnostic RNG. Evaluate trained routing, all-layer random routing, one randomized layer at a time, single-expert removal and dynamic suppression of the top m choices for m=0,1,2,4,6 with top-k kept at 2. Keep at least two available experts. Record bpc damage and per-layer usage; evaluate test only after freezing the probe design. **Dependency:** needs the owner's local data; `metrics/task_a.py` and `scripts/probe_task_a.py` provide concepts, but `evaluate_bpc` needs select/mask support or a new Task B probe wrapper. No new training. **Reading:** if S has consistently smaller randomization and removal damage than C/F/P, then support greater interchangeability on these probes; if not, the Task A pattern does not transfer consistently. Smaller damage alone does not establish why it arose.

### G16. Per-expert exposure, usage and quality

**Question:** Do less-trained experts have lower usage or greater ablation damage? **Runs/data:** nine simulated-arm logs and their final models; reconstruct actual successful holder-steps from round `held`, `dropped` and `local_steps`, and pair with final evaluation usage and G15 ablations. Compute within-layer rank associations per seed; do not treat experts from one model as independent seed replicates. Exact cumulative training token counts require actual training-routing logs, which current Task B worker statistics do not contain. Add counts to training statistics for future runs, not merged-evaluation counts as a substitute. **Dependency:** needs the owner's local data; G15; logging code for unavailable token exposure. **Reading:** if lower exposure aligns with worse usage/quality in every seed, then report an association compatible with under-training; if not, exposure alone is not supported as an explanation. Missing train-token counts remain missing.

### G17. Router and update diagnostics

**Question:** Which observable changes accompany the costs? **Runs/data:** inventory the 12 historical models/logs, then compute available final row cosines and gate saturation on fixed validation windows. Longitudinal diagnostics require before/after merged states and worker states that may not have been retained; do not reconstruct them from the final checkpoint. A separately planned F/P/S instrumentation run would be 9 runs, with diagnostics fixed before launch. **Dependency:** needs the owner's local data; new hooks in `model/moe.py`, `sim/worker.py`, the training loop and Task B orchestration; G11/G15 and network for reruns.

Register these metrics together: gate entropy/maximum probability; top-1 expert changes on the same characters between rounds; cosine of same-index expert deltas across successful holders; Jensen-Shannon divergence over an eight-expert support (zero for absent choices, with residency differences reported); fraction of local top-2 choices surviving merged full top-2; cosine between router rows; and routing under crossed pre/post trunk and pre/post router parameters, holding expert parameters fixed. Score fixed-layer inputs as well as end-to-end route changes when separating input from parameter effects. Save sufficient intermediate data using an explicit storage budget.

**Reading:** if route instability or update disagreement increases alongside dM across the pre-specified contrasts, then report an association worth testing with an intervention; if not, those diagnostics do not consistently track the cost. If trunk-only crossing reproduces more changes than router-only crossing, conclude input shifts dominate this diagnostic; if not, they do not. Neither route agreement nor its restoration is a quality metric by itself.

## C. Baselines, preserving numbered gaps

### G18. Same-step baseline and single-worker floor

**Question:** How much of F-C is associated with fewer sequential steps? **Runs:** use #87 B1-1, C with `optim.grad_accum=4, train.steps=5000`, and B1-2, C with `grad_accum=1, train.steps=5000`, compared with existing C20k and F. Existing options and `configs/queues/sweeps_batch1.toml`; first batch is seed 7 only. Additional seeds 11 and 19 are an owner question, not silently appended here. **Dependency:** network, #78 and #87. **Reading:** if F is closer to the batch-128 same-step reference than to C20k, then conclude that baseline choice explains part of the displayed gap in this seed; if not, that explanation is unsupported by this comparison. Batch accumulation averages micro-batch balance losses, so it is an analogue, not exactly synchronized global-batch balancing. One seed cannot establish robustness.

### G19. Longer centralized runs

**Question:** What is the local data-versus-bpc slope? **Runs:** C with `train.steps=20000,40000,80000`, all three seeds: 9 runs, with C20k reusable. Keep schedule shape fixed, evaluate at pre-specified data fractions and score the same characters. Existing options. Compute the Stage 0 5% allowance from each baseline rather than importing an unverified rounded literature value. **Dependency:** network; G14 reading; no local historical artifact dependency if all are rerun. **Reading:** if the longer trajectory brackets a lower-loss target, then give the observed-range character/step equivalent using the registered crossing method; if not, report only a bound. Longer budgets also change decay timing, so the curve is not a pure data scaling law.

### G20. Compute-matched partial training

**Question:** Can partial training use saved backward compute to recover its gap under a measured FLOP budget? **Runs:** first profile fixed batches for F and P at capacity 4, with identical token shapes and dispatch. Register the accounting method before viewing outcomes: include forward, backward, optimizer work and separately report communication and wall time. Let measured per-step costs be f and p. For an F budget of 20,000 worker steps, set P total steps to `4 * floor(20000*f/(4*p))`; create whole rounds with a final shorter round if needed. This needs partial-round orchestration if the target is not divisible by four-worker H=125. Compare F20k and matched P over three seeds: 6 full runs plus profiling. Existing rounds alone cannot guarantee FLOP equality. **Dependency:** accounting/instrumentation code, network and #104 R3. **Reading:** if measured-budget P reaches or beats F in all seeds, then conclude a FLOP-budget recovery in this setting; if not, it does not. If profiling or the final schedule exceeds the fixed budget, the comparison is invalid, not an equal-compute success.

## D. Every additional item in the report's new-code list

### N01. LocalAdamW-style moment averaging

**Question:** Does synchronizing moments help beyond keeping them locally? **Runs:** the averaged-state third arm of G11 in F/P/S, not nine additional duplicate runs. **Code:** moment state return/merge/checkpointing in `sim/worker.py`, `coordinator/merge.py` and `sim/harness.py`; use successful holders for expert moments and the same router-row policy as parameters. Define aligned Adam step counters, absent-holder state and reassignment before implementation; arithmetic averaging of moments alone is not a complete LocalAdamW specification. **Dependency:** G11, #88 and network. **Reading:** if averaged moments improve the target difference over both reset and kept state consistently, then support synchronized state; if not, no consistent extra benefit is shown. Include added memory and transmitted bytes in the conclusion.

### N02. Iso-C or other merge-based aggregation

**Question:** Can a non-arithmetic merge lower the costs? **Runs:** F/P/S under plain mean versus a fixed Iso-C implementation, H=125: 18 runs. Keep outer momentum off to isolate the merge first; add a later G02-matched outer comparison only under a separate plan. **Code:** matrix-aware aggregation in `coordinator/merge.py`, config and checkpoint metadata in `sim/harness.py`. A prerequisite plan must specify matrix orientation, singular-value treatment, normalization and fallback for vectors or unsupported tensors, and test holder-only merging. **Dependency:** network, code and #104's averaging context. **Reading:** if the merge lowers bpc consistently under the same work budget, then support it for this screen; if not, do not infer a gain from unrelated model-merging results. Report decomposition changes separately.

### N03. Dense baselines matching active and total size

**Question:** Is the centralized MoE useful at this budget? **Runs:** C MoE versus dense SwiGLU transformers with approximately 14M and 46M parameters, three seeds: 9 runs. Keep six layers, width 384 and attention fixed; choose dense hidden widths near 1536 and 6144, then record exact counts before launch. All receive the original character budget; additionally report FLOPs rather than calling total-size matching compute matching. **Code:** a true dense feed-forward block/model option in `model/layers.py` and `model/transformer.py`, then centralized script schema support. `n_experts=1, top_k=1` is rejected today, and dense dispatch is not this baseline. **Dependency:** code, network and owner budget. **Reading:** if MoE beats the active-size dense reference consistently, then support a quality advantage at that parameter-activation comparison; if not, no such advantage is shown. The total-size comparison answers a distinct storage question.

### N04. Balance coefficient and scope per arm

**Question:** Is the masking cost sensitive to balance strength or scope? **Runs:** C/F/P/S x `model.balance_coef=0,0.001,0.01`: 36 runs; then current versus a pre-fixed buffered scope in F/P/S plus C, 21 standalone runs, with matching controls reused. This is #104 R5, not a duplicate allocation. **Code:** coefficient already exists; scope needs changes in `switch_balance_loss`, training statistics and sequential-worker orchestration. Define buffer horizon and resident-expert normalization before running; a lagged buffer is not exact simultaneous global balance. **Dependency:** network and scope implementation; R5. **Reading:** if lower coefficient or changed scope reduces dM without worse P loss or expert coverage, then support that intervention; if not, it is not supported by the screen. Keep coefficient and scope as separate phases.

### N05. Router z-loss

**Question:** Does logit regularization improve quality or numerical stability under masking? **Runs:** C/F/P/S x coefficients 0,0.001,0.01: 36 runs, keeping Stage 0 fp32. **Code:** `model/moe.py` and `model/transformer.py` add a separately logged `coefficient * mean(logsumexp(available_logits)^2)` term; exclude unavailable entries from the available set and test finite gradients and empty-set rejection. Keep balance unchanged. **Dependency:** code and network. **Reading:** if nonzero z-loss lowers dM or avoids failures under matched conditions in all seeds without worse P, then support that measured benefit; if not, no consistent benefit is shown. If no control fails, report that this screen did not measure a stability advantage; do not claim proof of one from lower logit magnitude.

### N06. Router frozen at initialization

**Question:** Are learned router weights necessary in this setting? **Runs:** C/F/P/S with learned versus frozen initial linear-router weights: 24 runs. Freeze all router rows from the start with the same initialized weights as paired controls; trunk and experts still train. **Code:** explicit training freeze configuration in `model/transformer.py`, centralized entry point and `sim/worker.py`, including optimizer exclusion and checkpoint metadata. **Dependency:** code and network. **Reading:** if frozen weights match or beat learned bpc consistently, then conclude no quality advantage for learned weights in this screen; if not, learned weights help. This is distinct from #104 R4: fixed weights do not fix routes while the trunk changes, and no equivalence margin is inferred from mixed seeds.

### N07. Character-hash router

**Question:** How much contextual routing is needed with 27 character IDs? **Runs:** learned versus deterministic character-hash preference order in C/F/P/S: 24 runs. Choose a seeded permutation of eight experts per character and layer, taking the first two resident experts in S; fix seed and fallback before runs. Record that this fallback changes selected pairs with residency. **Code:** pass token IDs or an immutable token-aware routing context through `model/transformer.py` and `model/moe.py`, and exclude the unused learned selection weights from optimization while fixing a separately specified gate-weight rule, proposed equal weights over the selected pair. **Dependency:** code and network. **Reading:** if the hash package loses bpc consistently, then support the value of the learned contextual package over this baseline; if not, it is not consistently better. Selection and weighting differ, so do not attribute the result to context alone without a later gate-matched control.

### N08. Central router fitting after merging

**Question:** Does a centralized calibration phase repair the masked-training gap? **Runs:** in each of F/P/S compare no fit, router-only 1,000 final steps, router-only 25 steps after each of 40 merges, all-parameter 1,000 final steps, and all-parameter 25 steps after each merge: 45 runs. Fit on fixed training-only windows; keep validation/test out of gradients. Controls charge the extra centralized data and compute. **Code:** freezing, calibration optimizer, round-boundary invocation, schedule and resume state in `sim/worker.py` and Task B orchestration, plus a calibration configuration. **Dependency:** full-model fitting site, network, code and the #104 deferred candidate. **Reading:** if router fitting reduces dM and beats its timing-matched all-parameter control at the reported resource budget consistently, then support a router-specific repair; if not, recovery cannot be credited specifically to router fitting. It also introduces a central resource requirement.

### N09. Sigmoid gates under masking

**Question:** Is selected-expert softmax renormalization part of dM? **Runs:** C/F/P/S x selected softmax versus independent sigmoid gates, 24 runs as #104 R6. Same top-k indices, initialization and balance treatment. **Code:** `model/moe.py` gate mode, `ModelSection`, gradients and masking tests. No renormalization after sigmoid; record output norms. **Dependency:** code, network and R6; shared controls only if identical. **Reading:** if sigmoid lowers dM without worse P bpc in all seeds, then support a gate-related remedy; if not, the gate hypothesis lacks consistent support here. This does not reproduce the rest of sigma-MoE or FoMoE.

### N10. SPES-style expert-merging warm-up

**Question:** Can early cross-expert mixing reduce partial-update cost? **Runs:** F/P/S x warm-up on/off, 18 runs plus C anchors, sharing #104 R7's controls. Proposed adaptation: first four merge boundaries, each expert mixed toward its four closest other experts by flattened-weight cosine, starting strength 0.1 and linear decay to zero. **Code:** similarity/mixing in `coordinator/merge.py`, scheduler and checkpoint state in `sim/harness.py`, script invocation. Fix peer tie-breaking and optimizer-state treatment first. **Dependency:** code, network and R7. **Reading:** if warm-up lowers dP without worse F bpc consistently, then support this adaptation; if not, it is unsupported. Changes in interchangeability must be measured separately through G15, not inferred from loss. It is not a numerical reproduction of the SPES schedule.

### N11. H growing during decay

**Question:** Is more or less synchronization useful in the final decay? **Runs:** F/P/S with constant H=125, `sim.decay_local_steps=25`, and `decay_local_steps=250`, keeping nominal `local_steps=125, rounds=40, equal_compute_steps=20000`: 27 runs. Existing `round_plan` yields 40, 72 and 36 actual rounds respectively, with the same 5,000-step worker trajectory. The decay begins at worker step 4,000. **Dependency:** network, #87 B1-5's seed-7 full-arm result and matching controls; no new Task B code needed. **Reading:** if increasing final H lowers the gap consistently, then support less final synchronization under fresh AdamW; if not, that direction lacks support. If smaller H wins instead, record that opposite result without rewriting the registered question. Changing final H also changes reset frequency.

### N12. Mixing partial and sliced rounds

**Question:** Can occasional full forward visibility reduce dM while retaining some sliced operation? **Runs:** P throughout, S throughout, P for 20 rounds then S for 20, S then P in the reverse order, plus F: 15 runs plus C anchors. Same H and total worker steps. Record memory peaks and per-mode compute; partial rounds need the full forward model. **Code:** immutable per-round mode schedule and corresponding router rule in `SimSection`, Task B orchestration and resume hashing; use the existing worker builders for each mode. **Dependency:** code, network and owner memory budget. **Reading:** if a mixed schedule beats S consistently at its reported extra resource cost, then support a visibility-schedule benefit; if not, none is shown. Comparing the two orders tests timing, not a mechanism by itself.

### N13. Sequence routing and paths

**Question:** Does less frequent routing avoid part of the masked-training cost? **Runs:** token routing versus a causal sequence-constant expert-pair path in C/F/P/S: 24 runs. Conservative first implementation: each layer selects its top-2 resident experts from that sequence's first-token representation and keeps that pair for the sequence. The first token sees no future tokens. Keep the eight-expert inventory and two active experts, and measure FLOPs and memory. **Code:** persistent per-sequence route state in `model/moe.py`, `model/transformer.py`, worker construction and evaluation; tests for causality, masking and resume. **Dependency:** architecture contract from the owner, code and network; G08 if later content-domain paths are proposed. **Reading:** if the sequence-routing package lowers dM without worse P bpc consistently, then support this package; if not, it does not help in this screen. This small comparison does not validate a separate DiPaCo-style distributed path architecture or require such an architecture decision.

### N14. Centralized sensitivity checks

**Question:** How much centralized baseline slack exists in the report's suggested factors? **Runs:** single-factor changes around C: balance 0.001/0.01/0.1, dropout 0/0.1/0.2, weight decay 0/0.01/0.1 and context 256/512. This gives eight unique configurations including the common default, 24 runs. All are existing options: `model.balance_coef`, `model.dropout`, `optim.weight_decay`; context requires both `model.context_length` and `text8.context_length`. For context 512 use batch 16 to preserve characters per optimizer step and total character budget; report the changed sequence count. Score both context-trained models at context 256 for the training ablation, with context-512 scoring a separate result. **Dependency:** network, N04 shared coefficient controls; no new training feature. **Reading:** if a pre-registered setting improves validation consistently, then carry it to a separately budgeted confirmation before changing distributed controls; if not, no consistent slack is shown by this grid. Never choose a new baseline on test and retroactively change Stage 0's gate.

## Dependencies and owner questions

Start by inventorying G12-G17 artifacts and reusing existing issues, rather than creating duplicate experiments. #87 already owns B1-1 through B1-5; G02, G18 and N11 reference those runs, and G14 extends its curve analysis. #88 owns G01/G11/N01 after #87. #103 owns G13. [PR #128](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/pull/128) owns the remedy shortlist and its primary evidence; G05/G06/G20 and N04/N09/N10 are the gap-side specifications for those candidates.

Open for the owner: pool order and budgets; whether to extend #87 to seeds 11 and 19; practical-effect thresholds; local artifact access and missing-history policy; Task A surrogate versus a text8 heterogeneity design; which algorithm implementations and central resources to commission; and the precise FLOP accounting, memory ceilings and network readiness gates. These questions do not change SRS, ROADMAP, ARCHITECTURE or the literature report. Each eventual pool plan must fix its operational details and readings before running, then publish hardware, scale, dataset, seeds, failures and limits with results.

## Verification and limits

This note maps questions rather than adding literature results. The empirical evidence is in PR #128, checked directly in seven primary arXiv HTML papers: Filippova v1, FoMoE v2, StableMoE v1, MaskMoE v4, Demons in the Detail v2, sigma-MoE v3 and SPES v3. No additional empirical paper number is imported here. Source limitations remain SPES code-versus-paper provenance, FoMoE random-placement timing and figure-only effects.

The implementation plan records the completeness, link, configuration, arithmetic and test checks. No real training, saved-model scoring, local-data completeness audit or live network experiment was performed. New-code proposals remain designs, and the three-seed directional readings have no claimed statistical power or equivalence margin.
