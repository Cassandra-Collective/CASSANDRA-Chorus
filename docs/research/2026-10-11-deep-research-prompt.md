# Deep research prompt: why sliced local training of a mixture-of-experts model fell short in CASSANDRA Chorus Stage 0

Paste everything below the line into a new session. It is self-contained. If the session can read the CASSANDRA Chorus repository (github.com/Cassandra-Collective/CASSANDRA-Chorus), read `docs/stage0-report.md`, `docs/stage0-closeout.md` and `docs/prior-work.md` first.

---

## Your task

You are doing a literature investigation for a research project that has just produced a negative result. Find and read the published work that explains why our method lost quality, and what other researchers have already tried. The output is an annotated reading list and a synthesis that the project owner and I will read and discuss together. We want to understand the failure, not defend the method.

## The project in brief

CASSANDRA Chorus wants to train one language model on many volunteers' consumer GPUs, where **no machine ever holds the whole model**. The model is a mixture-of-experts (MoE) transformer:

- a shared part: embeddings, attention, norms, the router and the output head;
- 8 feed-forward experts per layer, with top-2 routing (a softmax over the 2 chosen).

The method is **sliced local training**, in rounds:

1. **Assign:** each of N workers receives the shared part plus a subset ("slice") of the experts.
2. **Train locally:** each worker trains its slice for H steps with **routing masked to the experts it holds**, using a fresh AdamW each round.
3. **Merge:** a coordinator averages:
   - the shared part over all workers;
   - each expert over the workers that held it;
   - each expert's router row over the same holders.

   Plain averaging, no outer optimizer.

Stage 0 simulated this on one laptop GPU (RTX 4070, 8 GB), always against centralized training of the same model at **equal compute** (same batch, same total steps), with seeds 7, 11 and 19.

**Arms compared** (each changes one thing):

| Arm | Worker holds | Routes over | Updates | Router averaged over |
|---|---|---|---|---|
| Centralized | everything | all 8 | all 8 | (no merge) |
| Sliced (the method) | shared + 4 of 8 experts | its 4 | its 4 | each expert's holders |
| Partial update (like SPES) | full model | all 8 | its 4 | all workers |
| Full-model averaging (local SGD / FedAvg-style) | full model | all 8 | all 8 | all workers |

Setting for every simulated arm: N = 4 workers, 4 of 8 experts per worker (coverage assignment), H = 125 local steps per round.

**Task A (synthetic):**

- 8 random lookup maps over 26 symbols; each sequence comes from one map.
- Model: 3.4M parameters, 4 layers, 10 rounds.
- Result:
  - sliced training matched centralized accuracy (every map 100%), and the router still separated maps;
  - but the experts became **interchangeable**: random routing kept 95% accuracy (centralized fell to about 48%), and removing any one expert cost at most 0.07 points (centralized: up to 18);
  - the comparison arms located the cause: letting workers route over all experts (partial update) restored most of the specialization. Assignment policy and router-merge rule barely mattered;
  - a probe found that, where a layer mattered, sliced experts were **generalists** that handled every map. Centralized experts were specialists.

**Task B (text8, character level):**

- Model: 46.05M parameters (6 layers, width 384, 8 experts of hidden size 768, k = 2, context 256).
- Budget: 20,000 steps of 32 × 256 characters per run; R = 40 rounds; Switch load-balancing loss 0.01 in every arm. Without it, routing collapsed onto 3 to 5 of 8 experts per layer.
- Test bits per character (lower is better), mean gap to centralized over three seeds:
  - full-model averaging **+6.1%**;
  - partial update **+7.6%**;
  - sliced **+10.8%**, against a pre-registered allowance of 5%.

  The seeds agree within 1 percentage point.
- The sliced gap splits exactly into three measured steps:
  - **local averaging** (full averaging vs centralized): **+6.1%**;
  - **partial updates** (partial vs full averaging): **+1.4%**;
  - **masked routing** (sliced vs partial update): **+3.2%**.

**Not tested in Stage 0:**

- other H, an outer optimizer (Nesterov outer momentum is implemented), other slice sizes or worker counts;
- larger models or budgets;
- router remedies (a central router fit after merging, a frozen shared anchor, z-loss).

## Questions to answer from the literature

For every claim, cite the paper and say whether you read the full text or only the abstract.

1. **The local-averaging cost (+6.1%).**
   - Is a gap of this size expected for local SGD, FedAvg or DiLoCo-style training at about 46M parameters, 4 workers, H = 125, 40 rounds, plain averaging and a fresh inner AdamW each round?
   - What does the literature report about how the gap depends on H, worker count, model size, the outer optimizer (Nesterov momentum, outer learning rate), learning-rate schedules and inner-optimizer state handling?
   - Which of our choices are known to hurt, and by how much? Look at DiLoCo, its scaling laws, Streaming and Decoupled DiLoCo, OpenDiLoCo, INTELLECT-1, Photon, and theory on local SGD and client drift (for example SCAFFOLD).
2. **The masked-routing cost (+3.2%) and interchangeable experts.**
   - What is known about how MoE experts come to specialize, and what destroys specialization? Cover router-expert co-adaptation, representation or routing collapse, load balancing as a driver of uniformity, and expert or routing dropout.
   - Is there evidence that training experts under a restricted or masked router (a subset of experts per worker or per step) produces generalist or redundant experts?
   - Look at FedAlign-MoE ("expert semantic blurring", "gating misalignment"), HARC (routing breakdown after merging), FLEX-MoE, DDOME/FedJETs, FedMoE, FlexOlmo, and any study of what MoE experts actually learn.
   - Also look at the results that random or hash routing can work almost as well (for example THOR, Hash Layers), which bear on whether specialization even matters at our scale.
3. **The partial-update cost (+1.4%).** What do sub-model and partial-training methods report about the cost of each worker updating only part of the model? Cover Federated Dropout, HeteroFL, FedRolex, IST and its theory, SDP, TwIST, FjORD and others. Is our 1.4% consistent with them?
4. **The closest prior methods, read in full.**
   - SPES (arXiv 2602.11543): its setting, its H, how its quality compares with centralized training, and what it does about routing. It is our partial-update arm at scale.
   - MoE-DisCo, Branch-Train-MiX, Branch-Train-Merge, DiPaCo, SMALLTALK LM, DEPT, Learning@home: what each found about training experts or modules apart, and the quality cost each reports.
   - Find papers that cite SPES or FlexOlmo and may be closer to our exact combination:
     - workers store only the shared part and their own experts;
     - routing masked to the held experts;
     - holder-only averaging;
     - per-worker slice sizes.
5. **Remedies with evidence.** Which interventions have measured effects on the three costs? Consider:
   - outer optimizers and synchronization frequency;
   - router-only or central router fine-tuning after merging;
   - a frozen shared trunk or anchor;
   - z-loss;
   - expert merging and alignment methods;
   - larger or overlapping slices;
   - routing a fraction of tokens to non-held experts;
   - knowledge distillation;
   - modular or path-based designs.

   Rank them by strength of evidence, without recommending a design.
6. **Sanity of our baselines.** Are about 1.44 bits per character for a 46M top-2 MoE after 164M characters of text8, and the 5% criterion, sensible against published character-level and MoE results? Note any reason our centralized baseline might be unusually strong or weak.

## Method and honesty rules

- **Primary sources only.** Verify that every paper exists: give its arXiv ID or DOI, a working link, authors, year and venue (or "preprint").
  - **Never invent a citation.** If you cannot verify a paper, list it under "unverified leads".
  - Prefer full text over abstracts. Mark each entry **full text**, **sections read** (say which) or **abstract only**.
  - Do not report a number from a paper you have not read in that part.
- **Recency.** Search through 2026. Several key papers are from 2025 and 2026. Note version dates when a preprint has several versions.
- **No novelty claims about our project.** Where our combination of choices looks unexplored, say "not found in this search" and describe what the search covered.
- **Every scale and setting.** Model sizes, data, number of workers, H, and whether the result is pretraining or fine-tuning. A finding at 7B with fine-tuning may not transfer to 46M pretraining; say so.
- **Quotes.** Keep quotations short (under about 15 words) and attributed; summarize in your own words.
- **Separate what a paper shows from your inference.** Label inferences as such.

## Deliverables

One Markdown report with these sections:

1. **Summary (one page):** the most likely explanations for each of our three costs, each with its strongest supporting papers, and how confident the literature allows us to be.
2. **Reading list for discussion:** 12 to 18 papers in the order we should read them together. For each:
   - full citation and link;
   - read status;
   - what it did (setting and scale);
   - its key findings;
   - which of our costs or questions it bears on;
   - how its setup differs from ours;
   - one question it raises for us.
3. **Findings by question (1 to 6 above):** what the literature says, where it disagrees, and what remains unknown.
4. **Remedies table:** intervention, which cost it targets, evidence (papers, scale, effect size as reported), and caveats.
5. **Closest prior work table:**
   - each method's choices on the axes in question 4;
   - its reported quality cost against centralized training;
   - its code availability and licence.
6. **Gaps:** questions no paper answers, which our project could answer with its existing harness. For example, the averaging cost as a function of H at small scale with and without an outer optimizer.
7. **Unverified leads:** anything you saw mentioned but could not verify.
8. **Search log:** queries, databases and sites searched, dates, and what was not covered.
