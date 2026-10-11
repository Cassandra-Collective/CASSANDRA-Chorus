# CASSANDRA Chorus · Stage 0: sliced local training of a mixture-of-experts model, a negative result

Technical report, 2026-10-11. Repository: github.com/mertefesensoy/CASSANDRA-Chorus (Apache-2.0). Every number below is taken from the committed record; sources are given in brackets.

## Summary

CASSANDRA Chorus asks whether a language model can be trained by a pool of volunteer computers when no computer ever holds the whole model. The method studied is **sliced local training** of a mixture-of-experts transformer:

- each worker receives the shared part of the model plus a subset of the experts;
- it trains them for many steps without network traffic;
- a coordinator averages the results.

Stage 0 simulates this on one laptop GPU, against a model of the same architecture trained normally, at equal compute. It has two decision gates.

- **Gate A, a synthetic routing task: passed, with a recorded limitation.**
  - Sliced training reached the centralized model's accuracy on every map and every seed, and its router still routed by map after merging.
  - Its experts became close to interchangeable: random routing cost it 4 to 5 points of accuracy where it cost the centralized model about 50.
  - Controlled comparison arms located the cause: restricting each worker's routing to the experts it holds.
- **Gate B, character-level language modelling on text8: not met.**
  - Sliced training ended +10.8% in test bits per character behind centralized (+10.3% to +11.3% over three seeds), against an allowance of +5%.
  - The gap splits exactly into three measured steps: local averaging itself +6.1%, updating only part of the experts +1.4%, and masked routing +3.2%.

The project owner judged the gap large (decision D28). By the plan, Stage 0 closes as a negative result, and the architecture is to be reconsidered before any networked stage. Reconsidering it is not part of this report.

## 1. Question and setting

The goal of the program is an open language model trained by many people's consumer GPUs, where no machine holds the whole model during training [SRS section 1]. The model is a mixture of experts:

- a **shared part:** embeddings, attention, normalization, the router and the output head;
- **experts:** several feed-forward blocks per layer, of which a learned router picks two per token.

Because each token uses only two experts, the experts can live on different machines.

**Sliced local training** proceeds in rounds [SRS section 2, S0-F-04 to S0-F-10]:

1. **Assign:** a coordinator gives each worker the shared part and a subset of the experts (its slice).
2. **Train locally:** each worker trains its slice for H steps, with routing masked to the experts it holds.
3. **Upload:** each worker returns its parameters.
4. **Merge:**
   - the shared part is averaged over all workers, weighted by examples;
   - each expert is averaged over the workers that held it;
   - each expert's router row is averaged over the same holders, since a worker gives no gradient to rows of experts it lacks (D11).

Stage 0 decides whether this method is viable before any networking is built. It simulates the workers one after another on a single GPU, with no faults or skewed data in the gated runs, and compares against centralized training of the same model at equal compute.

## 2. Method

**Equal compute (D17).** Every worker step uses the same batch as a centralized step, and the worker steps summed over workers and rounds equal the centralized steps: N × H × R = S.

**Arms.** Each comparison arm changes one thing from the main sliced arm [SRS S0-F-14, S0-F-26; D13, D20, D21]:

| Arm | A worker holds | Routes over | Updates | Router averaged over |
|---|---|---|---|---|
| Centralized | one machine, everything | all 8 | all 8 | no merge |
| Sliced (main) | shared part + 4 experts | its 4 | its 4 | each expert's holders |
| Sliced, rolling | as main, slice shifts each round | its 4 | its 4 | holders |
| Sliced, router over all | as main | its 4 | its 4 | all workers |
| Partial update | the full model | all 8 | its 4 | all workers |
| Full-model averaging | the full model | all 8 | all 8 | all workers |

- Partial update follows SPES, a published method in which nodes hold the full model but train only their own experts.
- The partial and full arms are equal to the sliced arms in steps and sequences, not in memory: their workers hold all 8 experts.

**Common settings.**

- 4 workers, each holding 4 of the 8 experts in every layer (coverage assignment), so no worker ever holds more than half (D18).
- AdamW (learning rate 10⁻³, β = 0.9 and 0.95, no weight decay, gradient clipping at 1.0), 100 warm-up steps, and a linear decay to 10⁻⁴ over the last 20% of each worker's trajectory. The optimizer is reset each round (D19).
- Training is deterministic given configuration and seed. A resumed run was tested to end bitwise identical to an uninterrupted one.
- Seeds 7, 11 and 19; every criterion must hold on each seed separately (S0-A-06).

**Task A, synthetic lookup maps [SRS S0-F-15 to S0-F-18].**

- The task:
  - Eight secret maps over 26 letters; each sequence is 32 key-value pairs drawn from one map, and only a key's first appearance is scored.
  - In the marked variant a first token names the map (best possible accuracy 1.0). In the unmarked variant the map must be inferred from context (best possible 0.951).
  - The right routing is known, so a router's behaviour can be checked against it.
- The model: 3.42M parameters (4 layers, width 128, 8 experts per layer, k = 2), 5,000 steps of 64 sequences per run, 10 rounds of 125 local steps in the simulated arms.

**Task B, text8 [S0-F-19].**

- The data: character-level text8 with the conventional split. Bits per character are scored over the whole 5M-character test split in non-overlapping 256-character windows, the parent project's protocol.
- The model: 46.05M parameters (6 layers, width 384, 8 experts per layer, k = 2, context 256).
- The budget: 20,000 steps of 32 × 256 characters per run (163.8M characters); the simulated arms run 40 rounds of 125 local steps.
- The balance loss: a Switch load-balancing loss with coefficient 0.01 in every arm (D27). Without it, a 2,000-step centralized check sent almost all tokens to 3 to 5 of the 8 experts per layer.

**Measures, fixed before the runs (D10, D22).**

- Accuracy on every map.
- Router consistency: mutual information between map and chosen expert, divided by the map entropy.
- Routing necessity: accuracy with the trained router minus accuracy with random routing.
- Expert usage: an expert is negligible below 0.025 of tokens.
- Expert drift between the holders of an expert.
- Bits per character.

**Criteria, fixed before the runs [SRS section 4.4].**

| Criterion | Requirement |
|---|---|
| S0-A-01 | Task A marked: every map at least 99% accurate in the merged sliced model |
| S0-A-02 | Task A unmarked: within 2 points of centralized, same seed |
| S0-A-03 | No expert below 0.025 of tokens in any layer |
| S0-A-04 | Task B: merged sliced model within 5% (relative) bits per character of centralized |
| S0-A-05 | No worker holds more than half the experts |
| S0-A-06 | Each criterion on every seed |

Two readings were also registered before the data they concern:

- **D23:** if accuracy passes but the sliced experts are far more interchangeable than centralized ones, Gate A passes with a recorded finding, and Task B must show whether this costs capacity.
- **The probe's reading:** the thresholds for the inside-the-experts probe, committed before any probe number was computed (section 3.2).

## 3. Results

All runs ran on one laptop (RTX 4070 Laptop GPU, 8 GB; PyTorch 2.12.1, CUDA 12.6), fp32 with deterministic kernels.

### 3.1 Gate A: criteria met, experts interchangeable

All Gate A criteria were met on every seed [RESULTS.md, 2026-10-08 Gate A entry; `results/task_a_gate_a.md`]:

- every marked map at 1.000;
- unmarked accuracy 0.009 to 0.037 points below centralized;
- the least-used expert at 0.113 of tokens or more;
- 4 of 8 experts per worker.

The router still separated maps: consistency in the two middle layers was 0.27 to 0.46, against 0.12 to 0.37 for centralized (ceiling 2/3).

The registered limitation (D23) appeared on every seed and both variants:

| Task A | Centralized | Sliced |
|---|---|---|
| Accuracy with random routing (marked) | 0.46 to 0.49 | 0.95 to 0.96 |
| Routing necessity, relative to centralized | 1 | 0.06 to 0.10 |
| Worst single-expert removal (points) | 8.0 to 18.1 | at most 0.07 |

The comparison arms located the cause [`results/task_a_gate_a.md`]. Routing necessity, relative to centralized, was:

- **sliced arms:** 0.05 to 0.18 (main, rolling, router over all);
- **partial update:** 0.56 to 0.70;
- **full-model averaging:** 0.64 to 0.80.

Partial update and the sliced arm with the router averaged over all workers differ in training only in whether a worker may route tokens to experts it does not update. That single change moved necessity from 0.05 to 0.07 up to 0.56 to 0.70. Neither the assignment policy nor the router merge rule did comparably.

### 3.2 Inside the experts

A probe of the 36 saved Gate A models had its reading registered in a commit before any probe number was computed [RESULTS.md, step 9a; `results/task_a_redundancy_probe.md`]. Its two measurements:

- zeroing one mixture layer at a time;
- forcing every pair of experts in each layer.

The registered reading came out **mixed**:

- **Unmarked variant.** Layer 0 is needed in every arm (44 to 88 points lost without it). There, 63% to 71% of the main sliced model's (expert pair, map) combinations kept 99% of trained accuracy, against none in the centralized, partial and full models. Where a mixture layer is needed, the sliced experts are generalists.
- **Marked variant.** No single mixture layer of the sliced model was needed (at most 0.4 points). A post hoc check, approved by the owner and labelled as such, zeroed all four layers at once; every model then collapsed. The sliced layers stand in for one another.

### 3.3 Task B: the gap on text

All 12 runs completed with a clean working tree [`results/task_b_gate_b.md`; RESULTS.md, Task B entries].

| Test bits per character | Seed 7 | Seed 11 | Seed 19 | Gap to centralized, mean (range) |
|---|---|---|---|---|
| Centralized | 1.4388 | 1.4386 | 1.4353 | reference |
| Full-model averaging | 1.5300 | 1.5242 | 1.5219 | +6.1% (+5.9 to +6.3) |
| Partial update | 1.5504 | 1.5474 | 1.5408 | +7.6% (+7.3 to +7.8) |
| Sliced (Chorus) | 1.6020 | 1.5867 | 1.5887 | +10.8% (+10.3 to +11.3) |

- **S0-A-04 fails on every seed.**
- The seeds agree closely: the centralized result varies by 0.0035 bits per character, and each arm's gap by at most 1.0 percentage point.
- The order of the arms is the same on all three seeds.

Because each step adds one restriction, the sliced arm's gap splits exactly:

| Step | Arms compared | Mean (range), % of centralized |
|---|---|---|
| Local averaging | full-model averaging vs centralized | +6.1 (+5.9 to +6.3) |
| Partial updates | partial update vs full-model averaging | +1.4 (+1.3 to +1.6) |
| Masked routing | sliced vs partial update | +3.2 (+2.7 to +3.6) |

Under the balance loss, expert usage held in every run but one. In the sliced run on seed 11, one expert of layer 0 received 0.011 of tokens.

## 4. Discussion

**Two gates, one consistent picture.**

- **Task A:** routing restricted to a worker's slice made the merged experts interchangeable without costing accuracy. A thousand bits of lookup maps fit in any expert.
- **Task B:** the same restriction costs about 3 points of bits per character on top of everything else. That is the capacity cost D23 asked Task B to show.

Updating only part of the experts costs a further 1.4 points. Both costs are specific to slicing.

**The largest single cost is not slicing.** Ordinary local averaging of the whole model already costs about 6% at this setting: 125 local steps, 40 rounds, plain averaging with no outer optimizer. Every simulated arm pays it. On its own it would be just outside the 5% allowance.

This matters for reading the result. Under these settings the method fails by about twice its allowance. Slicing's own share, 4.6 points, is close to the allowance by itself. The sweeps that would bound the averaging share were planned (PLAN step 11) but not run:

- fewer local steps;
- the outer optimizer that is implemented;
- other slice sizes and worker counts.

**Relation to prior work.** A bounded survey [`docs/prior-work.md`, SRS section 10] found close relatives:

- **SPES** pretrains mixture-of-experts language models with each node training its own subset of experts, but its nodes hold the full model and route over all experts. That is the partial-update arm here, which also missed the allowance (+7.6%).
- **FedMoE** uses the holder-averaging merge rule for fine-tuning.
- **Sub-model training of dense transformers:** HeteroFL, FedRolex, TwIST and SDP.

The survey did not find open code combining all of Chorus's specific choices. That is not proof that none exists. Only the key abstracts and the SPES code were checked against their sources; claims from inside the papers were not re-checked. **No novelty is claimed.** The contribution of Stage 0 is the controlled measurement above, a negative result at this scale.

## 5. Limits and what was not tested (S0-N-07)

**Scale and setting.**

- One machine: an RTX 4070 Laptop GPU with 8 GB, with workers simulated in sequence and no real network.
- Two model sizes: 3.42M (Task A) and 46.05M (Task B).
- Two datasets: synthetic lookup maps and text8.
- One budget per task.
- One simulated configuration: 4 workers, 4 of 8 experts each, coverage assignment, H = 125, plain averaging.
- Three seeds per cell. The per-seed values are given; no significance test is claimed.

**Not tested.**

- Other numbers of local steps, outer optimizers, slice sizes, worker counts, worker dropout and skewed data (implemented, not run in the gated experiments).
- Larger models and budgets.
- The registered Gate A remedies for routing:
  - a central router fit after merging;
  - a frozen shared anchor;
  - z-loss.
- What layer-0 experts specialize in, if not the map.
- Sliding-window evaluation (non-overlapping windows were used, as in the parent project).
- Reproduction on another machine.

**Unequal resources.** The partial-update and full-averaging arms hold twice the expert parameters per worker, and in Task A (dense dispatch) did about twice the expert computation per step. They are equal to the sliced arms in steps and sequences only.

**Operations.**

- The laptop's mains supply dropped out frequently, and two outages ran the battery low. Runs froze for 1.9 h and 7.0 h and then continued; one run was resumed from its checkpoint.
- Training is deterministic, so these events changed wall-clock time only. Each is recorded in its run's log.

## 6. Reproducing the results

- **Code and configurations:** the repository at the commit of each run (recorded in its log and in `RESULTS.md`).
- **Task A runs:**
  - centralized: `scripts/train_task_a_centralized.py`;
  - simulated arms: `scripts/train_task_a_sliced.py`;
  - configurations: `configs/task_a/`;
  - queues: `configs/queues/gate_a_main.toml` and `configs/queues/gate_a_comparison.toml`.
- **Task B runs:** `scripts/train_task_b_centralized.py` and `scripts/train_task_b_sliced.py`, configurations in `configs/task_b/`, queue `configs/queues/task_b_matrix.toml`.
- **Analyses:** `scripts/analyze_task_a.py`, `scripts/probe_task_a.py`, `scripts/analyze_task_b.py`. They read run logs only.
- **Data:** text8, SHA-256 `6e890197040d37d85beb962ae1f041ff1d9a9ca8d20c7d99c85027eebf51dca7`, checked on load.
- **Not in the repository:** raw run logs and saved models (up to about 370 MB per Task B run). They are kept locally and available on request.

## 7. What comes next

By decision D28, the architecture is to be reconsidered before any networked stage. The measurements suggest where to look, without deciding anything:

- **The averaging share (+6.1%),** which every variant pays.
- **The masked-routing share (+3.2%),** which is the cost of keeping each worker's model small.
- **The fallback the plan already names:** modular paths, where each worker trains one complete route through a grid of modules.

That study, and any change to the method, will be planned and reported separately.

## Sources

- `RESULTS.md` (dated entries for every run and check)
- `results/task_a_gate_a.md`, `results/task_a_redundancy_probe.md`, `results/task_a_probe_all_layers_posthoc.md`, `results/task_b_gate_b.md`
- `docs/SRS.md` (sections 1, 2, 4.4, 10; decisions D10 to D28), `docs/PLAN.md` (section 5)
- `docs/prior-work.md`
- `docs/implementations/` (one document per change, with its verification)
