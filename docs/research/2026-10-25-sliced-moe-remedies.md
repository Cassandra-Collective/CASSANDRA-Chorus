# Candidate remedies for the partial-update and masked-routing costs

Date: 2026-10-25. Proposal for [#104](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/104), not an experiment result. Base: `a30dd6a`. [Plan](../implementations/2026-10-25-sliced-moe-remedies.md).

The practical first pool is a paired slice-size study, followed by assignment policy. Both use existing options. Consistent routing, balance scope, sigmoid gates and expert-merging warm-up need separate implementation work. Published gains motivate tests; they do not predict a recovery of Stage 0's costs.

## Comparison contract

Use `configs/task_b/sliced.toml` and `configs/task_b/centralized.toml`. Unless a row says otherwise: text8, 46,050,432 parameters, top-2 of 8, batch 32, context 256, seeds **7, 11, 19**, four workers, `sim.local_steps=125`, `sim.rounds=40`, `sim.equal_compute_steps=20000`, `sim.policy=coverage`, `sim.capacity=4`, plain averaging and fresh AdamW each round. Keep the optimizer, data split and evaluation protocol fixed. These are the Stage 0 configurations, not a claim of equal FLOPs between modes.

Arm abbreviations: C is centralized, `train.steps=20000`; F is `sim.mode=full, sim.router_rule=all`; P is `partial, all`; S is `sliced, holders`. All other overrides below are relative to these. Set `run.seed` and a distinct `run.name` for every configuration. No real runs were made for this note.

The [Stage 0 report](../stage0-report.md), section 3.3, reports a +10.8% sliced gap, decomposed as +6.1% averaging, +1.4 percentage points partial updates and +3.2 percentage points masking, relative to centralized bpc. Rounding means the displayed components need not sum exactly. For new comparisons use per-seed `dP = bpc(P) - bpc(F)` and `dM = bpc(S) - bpc(P)`. A change in S alone cannot identify which cost moved. Report raw bpc and ratios with their denominators named.

Pre-register these screening rules in each pool's own plan before running: if the target difference falls in every paired seed without raising the preceding arm's bpc, conclude that the intervention is a candidate remedy in this setting; if not, conclude that this screen gives no consistent support, and retain mixed or adverse seeds. No significance, equivalence or deployment decision follows from three seeds. Missing or failed runs make a comparison incomplete. Open for the owner: a practical-effect threshold, total budget and adoption gate.

## Checked evidence and candidate runs

### R1. Larger slices and more holders

**Target:** partial updates; paired P/S runs also measure the masking cost as visibility changes.

**Primary evidence:** Filippova et al., [Partial Parameter Updates, v1](https://arxiv.org/html/2509.22418v1#S3.T1), section 3.1 and Table 1: 1.3B dense LM, RedPajama-V2, 32 nodes, H=100, Nesterov outer step. Full training has perplexity 12.75 at 26B tokens; MLP fractions 1/16, 1/8, 1/4 and 1/2 give 14.21, 13.59, 12.72 and 12.24. The response is not a monotonic penalty relative to full training. FoMoE, [v2, Table 6](https://arxiv.org/html/2606.19025v2#A5.T6), uses a 54M proxy, web/code pretraining and C4 validation. At four workers, LocalAdamW, fixed placement and K=128, one, two and four holders give 143.72, 123.50 and 111.89 perplexity. At eight workers its four-holder result 138.88 beats full replication 159.71. Larger replication is not uniformly better. FoMoE changes masking and partial updates together and uses different gates and state handling.

**Feasibility and runs:** existing `sim.capacity`, `sim.mode`, `sim.router_rule`. Run P and S at capacity 2, 4 and 6, plus F and C. Capacity 8 is the full-visibility endpoint; do not budget duplicate P/S endpoints as independent evidence. At fixed worker count, slice fraction and mean holder count move together; this pool does not separate them. Report memory as well as bpc. Larger P slices need more optimizer state; P already stores the full forward model.

**Inference:** 8 configurations x 3 seeds = **24 runs** if no controls can be reused. Reading: if dP falls as capacity increases in each seed, support a size-dependent partial-update cost; otherwise reject that directional screen. Separately apply the same reading to dM. This connects to gaps 5 and 7 of the literature report.

### R2. Change assignment while preserving mean capacity

**Target:** partial-update variance and masked-routing consistency.

**Primary evidence:** FoMoE v2, Table 6, same setting as R1: at four workers and two holders, fixed versus random placement gives 112.00 versus 113.65 at K=32, but 119.53 versus 114.88 at K=64. The sign reverses. The table supports an assignment comparison, not a claim that fixed placement wins. Its random placement timing is not sufficiently specified to treat our policy as a reproduction.

**Feasibility and runs:** existing `sim.policy=coverage`, `random`, and `rolling`. Use rolling with `sim.rolling_shift=1` for rotating, exactly two holders; use rolling with `rolling_shift=0` for a pinned assignment. The latter is expressible today: `_rolling` in `coordinator/assignment.py` adds round index times shift to a fixed worker offset. Pinned residency does not make a token's contextual routing fixed. Random assignment can leave an expert without a holder; coverage cannot. Compare all four policies in P and S at capacity 4, with C and F anchors. Record realized holders and missed updates, not just nominal capacity.

**Inference:** 10 configurations x 3 = **30 runs**, or **18 additional runs** after reusing R1's identical C, F, P4 and S4 controls. If rolling or pinned residency reduces dP or dM in every seed, support that policy for that cost; if not, do not infer that lower holder variance or greater persistence is sufficient. Do not attribute a random-policy failure solely to variance when experts went untrained.

### R3. Extra training for partial updates

**Target:** partial-update sample efficiency, with a distinct resource question.

**Primary evidence:** Filippova v1, Table 1: at 1/8 MLP fraction, 37B rather than 26B tokens changes perplexity from 13.59 to 12.68; full training at 26B is 12.75. This compares different token budgets in a dense 1.3B model. It does not establish a free improvement at our budget.

**Feasibility and runs:** existing configuration can double worker trajectories: P and F at 20,000 and 40,000 total worker steps (`sim.rounds=40` or `80`, with matching `equal_compute_steps`), plus C at `train.steps=20000` and `40000`. Keep schedule fractions fixed over each new trajectory. This is a dose test, not a FLOP-matched test: skipping expert gradients does not halve all training work. Gap 20 needs profiling before choosing a genuine compute-matched budget.

**Inference:** 6 configurations x 3 = **18 runs**, or **9 additional runs** after reusing R1's C, F and P4 at the original budget. If longer P reaches original-budget F in every seed, conclude that additional training can recover that target, at a stated extra token budget; if not, it did not at this dose. Compare longer F and C to expose the opportunity cost. Hardware-specific time and FLOPs must be measured, not assumed from trainable parameter counts.

### R4. Make routing more consistent

**Target:** masked routing, as a hypothesis about disrupted input-to-expert associations.

**Primary evidence:** [StableMoE v1](https://arxiv.org/html/2204.08396v1#S4.T5), sections 3, 4.1, 4.2 and Table 5: centralized LM on RoBERTa corpora plus English CC100, 124M shared and 454M expert parameters. Freezing a distilled router after 6K of 60K steps changes BASE-layer validation perplexity 20.04 to 19.41, and StableMoE stage-1-only 19.48 to 19.28. [MaskMoE v4, Table 5](https://arxiv.org/html/2407.09816v4#S5.T5) tests fixed token-type masks on the Pile, at 468M active parameters: four visible experts out of 64 give 6.551 versus 6.618 with all visible. Neither is a worker-residency experiment. With only 27 character IDs, a token-type restriction is a substantial change in inductive bias.

**Feasibility and runs:** new code in `model/moe.py`, `model/transformer.py`, `sim/worker.py` and `scripts/train_task_b_sliced.py`: a distilled routing module with saved state, a freeze boundary, and an explicit top-2 fallback over resident experts. Merely freezing the current linear router does not freeze routes because trunk representations keep changing. Before implementation, specify a separate, context-independent routing feature path, distillation targets, and what happens when a preferred expert is absent.

Proposed first comparison is learned versus distilled-and-frozen selection in F/P/S, with the same residency policy, and C as an anchor. Freeze after the first 10% of the worker trajectory (500 local steps, four rounds), an **Inference:** screening choice inspired by StableMoE's fraction, not a validated transfer. Charge the teacher/distillation cost. Keep inference restrictions identical across treatment and its matched control; any full-visibility evaluation is an explicitly separate metric. A fixed token mask is a later separate ablation, not bundled into this screen.

**Inference:** 7 configurations x 3 = **21 runs** before shared-control reuse, **9 additional** if R1's four controls match. If dM falls with frozen selection without degrading P, support this routing intervention; if not, do not conclude that consistent residency alone or a frozen linear weight matrix is the explanation.

### R5. Balance coefficient, then balance scope

**Target:** the Task B masking cost; balance is also a collapse safeguard.

**Primary evidence:** [Demons in the Detail v2](https://arxiv.org/html/2501.11873v2#S4.T1), section 4.1, Tables 1 and 4: centralized multilingual/general/math pretraining, 3.4B total and 0.6B active, 120B tokens. Moving balance batch size from 4 to 512 changes perplexity 8.167 to 8.038. At batch size 4, weights 0.008 and 0.004 give 8.167 and 8.154. These are different interventions, with different effects; neither is evidence for a particular coefficient on text8.

**Feasibility and runs:** `model.balance_coef` already exists. Run F/P/S at 0, 0.001 and 0.01, plus C at the same three coefficients. Use all coefficients in every arm, rather than tuning S alone. **Inference:** 12 configurations x 3 = **36 runs**, or **24 additional** with R1's coefficient-0.01 controls reused. If dM falls at a lower coefficient without higher P bpc or more unused experts, support it; if not, weaker balance is not supported by this screen.

Global or cross-worker balance needs new code in `switch_balance_loss` in `model/moe.py`, the training loop and worker orchestration. Sequential local workers do not expose contemporaneous global statistics. A trailing statistics buffer must be called buffered balance, not exact global balance. At a coefficient fixed before this second phase, compare current versus buffered scope in F/P/S, plus C: **Inference:** 7 x 3 = **21 fresh runs**, 9 additional if controls match. If the scope change reduces dM while keeping P and expert coverage, support that scope; if not, the published global-batch mechanism did not transfer under this approximation.

### R6. Sigmoid gates without selected-expert renormalization

**Target:** masked routing and the change in gate normalization between local and merged models.

**Primary evidence:** [sigma-MoE v3, Table 4](https://arxiv.org/html/2310.10837v3#S6.T4): centralized LM, 47M parameters on WikiText-103, sigmoid gives perplexity 11.59 versus 11.89 for softmax with renormalization. At 41M on character-level enwik8, the corresponding bpc values are 1.08 and 1.09. This is close in total size, but not a sliced or local-averaging test. FoMoE v2, appendix B.3.2, motivates independent sigmoid scores under partial replication but supplies no isolated sigmoid-versus-softmax ablation.

**Feasibility and runs:** new selection/gate mode in `model/moe.py`, configuration in `model/transformer.py`, and tests of masked forward passes and gate gradients. Keep selected indices, top-k and initialization controlled. Specify whether balancing still uses softmax probabilities and retain that choice in both gate treatments; changing balance simultaneously would confound the gate comparison. Compare softmax versus independent sigmoid output gates in C/F/P/S, with no second sigmoid normalization.

**Inference:** 8 configurations x 3 = **24 runs**, or **12 additional** with R1 controls reused. If dM falls under sigmoid without a worse P arm, support a gate-related remedy; if not, FoMoE's motivation is insufficient for our setting. Inspect output norms so scale changes are visible.

### R7. Expert-merging warm-up

**Target:** partial updates, by sharing early information across experts.

**Primary evidence:** [SPES v3, Table 4](https://arxiv.org/html/2602.11543v3#S4.T4), sections 3.3 and 4: 1B-class MoE, 1.1B total/0.3B active configuration, SlimPajama, 50B tokens. With expert merging the eight-task average is 50.95 versus 48.99 without. **Inference:** +1.96 score points. This is not a loss or bpc result. The paper gives warm-up 12,500 steps, interval 300, initial strength 0.1 and four similar peers; the literature report records different released-code defaults. Those code defaults were not independently re-audited here.

**Feasibility and runs:** new expert-similarity and mixing operation in `coordinator/merge.py`, scheduling/state in `sim/harness.py`, and invocation in `scripts/train_task_b_sliced.py`. Mixing expert parameters is different from averaging copies of the same expert. Specify the similarity metric, peer tie-breaking, strength decay and optimizer-state handling before implementation. Conservative proposed screen: at each of the first four round boundaries, move each expert toward the mean of its four closest other experts using flattened-weight cosine and a linearly decreasing strength starting at 0.1; stop afterward. **Inference:** these are test settings, not a reproduction of SPES.

Run warm-up on/off in F/P/S, plus C. **Inference:** 7 configurations x 3 = **21 runs**, or **9 additional** with R1 controls reused. If dP falls without increasing F bpc, support early mixing for partial updates; if not, this adaptation is unsupported. Run interchangeability diagnostics separately: a gain in loss alone does not show improved specialization.

## Verification and limits

The seven versioned arXiv HTML documents linked above were fetched as primary text on 2026-10-25. Their relevant methods, setup paragraphs and tables were read directly, including opposite-sign FoMoE cells. Raw effect values are reproduced as evidence; all new run budgets and transferred settings are labelled Inference. The code audit checked `SimSection`, `round_slices`, `_rolling`, `train_worker`, `ModelSection`, `switch_balance_loss`, the Task B configs and both entry points at the stated base.

No remedy efficacy, significance or network performance was verified. Figure-only numbers, SPES code-versus-paper provenance, and FoMoE random-placement timing remain unverified. Existing Stage 0 controls require the owner's local logs and models plus matching configurations and evaluation; otherwise rerun them. Actual new-code designs require their own implementation plans and tests. Test-suite and document-check results are recorded in the implementation plan.

Other report candidates, including post-merge router fitting, z-loss, alignment, shared experts, distillation and remote expert calls, are not promoted by this shortlist. This does not claim they fail. The gap proposals in #105 keep the report's explicit new-code questions visible. Averaging-only remedies remain with [#87](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/87) and [#88](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/88).

## Proposed split into research pools

1. **Visibility and holder budget:** R1. Existing options; keep paired P/S arms and memory reporting together.
2. **Assignment and persistence:** R2. Existing options, after the R1 controls are fixed.
3. **Additional training:** R3, with gap 20 supplying a later measured FLOP-matched extension. Keep the extra-token result distinct.
4. **Consistent selection:** R4, after a separate routing and residency contract is approved.
5. **Balance:** R5 coefficient screen first, then a separately planned scope comparison.
6. **Gate normalization:** R6, independent of balance changes.
7. **Early expert mixing:** R7, independent of optimizer-state changes.

Each pool needs its own committed plan and reading before runs. The counts above are standalone screening estimates, not an instruction to launch all pools; shared controls are reusable only when their full configuration matches. Open for the owner: priority, resource limits, practical thresholds and which implementations to commission.
