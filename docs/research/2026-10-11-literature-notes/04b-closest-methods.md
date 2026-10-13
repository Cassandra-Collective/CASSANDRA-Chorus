# Question 4 (second half) and question 5: closest methods other than SPES

| | |
|---|---|
| Date | 2026-10-11 |
| Scope | MoE-DisCo, Branch-Train-MiX (BTX), Branch-Train-Merge (BTM), DiPaCo, SMALLTALK LM, DEPT, Learning@home, read in full; 2025-2026 follow-ups (FoMoE and KALAVAI read); OpenDiPaCo status; HeterMoE, Hexa-MoE and Lazarus classified |
| Not in scope | SPES and its citers, FlexOlmo, FedMoE, FedAlign-MoE, HARC, FLEX-MoE (covered by other researchers) |
| Method | Each paper fetched as PDF from arxiv.org with `curl`, converted with `pdftotext -layout`, and read from the raw text. One garbled table (FoMoE Table 6) was re-read from the arXiv HTML (v2) with a local table parser. Version histories from the arXiv abstract pages or the export API. Code status from the GitHub REST API. Search tools were used only to find papers. |
| Conversions | Where I convert perplexity ratios into ratios of log-loss (comparable in kind to our bits-per-character gaps, because bits = nats / ln 2 and the constant cancels in a ratio), the conversion is mine and is labelled "(my conversion)". Units still differ: tokens (BPE) in the papers, characters in ours. |

Our reference numbers (from the brief): full-model averaging +6.1%, partial update +7.6%, sliced +10.8% test bits per character against centralized at equal compute; steps of the decomposition: local averaging +6.1%, partial updates +1.4%, masked routing +3.2%. The sliced arm is about 4.4% worse than full-model averaging as a ratio (1.108 / 1.061, my arithmetic).

---

## Papers

### 1. MoE-DisCo: Low Economy Cost Training Mixture-of-Experts Models

- **Authors:** Xin Ye, Daning Cheng, Boyang Zhang, Yunquan Zhang (Institute of Computing Technology, CAS).
- **Year / venue:** 2026, preprint (no venue stated).
- **arXiv:** 2601.06857; v1 11 Jan 2026 (only version). Read: v1. https://arxiv.org/abs/2601.06857. DOI 10.48550/arXiv.2601.06857.
- **Code / licence:** Appendix B gives `https://anonymous.4open.science/r/MoE-DisCo-4835/`; a `curl` on 2026-10-11 returned HTTP 401 `not_connected`, so it was not opened. Two GitHub repositories named MoE-DisCo exist (`tomcheng0618/MoE-DisCo`, created 2026-01-05, description "Code of MoE-DisCo", size 0, no licence, no README; `yexin-9220/MoE-DisCo`, created 2026-01-06, 96 KB, no licence, no README). Neither is linked from the paper, so neither is confirmed as the authors' code. Licence: unknown.
- **Read status:** full text (all pages, appendices A to E).
- **Setting and scale:** Qwen1.5-MoE-2.7B and LLaMA-MoE-3.5B, each "set the number of experts to 4" (§4.1.1); C4, WikiText-2 and OpenWebText (§4.1.2). Whether the models start from random initialization or from released checkpoints is not stated. The reported losses (for example C4 loss 4.954, PPL 230.32 for the full-parameter Qwen run, Table 1) look like short from-scratch training (inference). Submodel phase: AdamW, lr 1e-4 constant, batch 16, sequence 1024 (Table 4); up to 4,200 to 5,922 steps per submodel (Table 6). Fine-tune and full-parameter baseline: AdamW, lr 3e-4, cosine, warmup 0.03, weight decay 0.01, batch 16 (Table 5). Pretraining-style language modelling (not fine-tuning of a released model, as far as stated).
- **Method:** data clustered with k-means on mean-pooled embeddings into E clusters; E dense submodels "shared backbone plus one expert" trained independently, "without any inter-device communication" (abstract); shared parameters averaged with weights ω_k (1/E when clusters are balanced, Eq. 2); experts concatenated; gate "initialized by tensor concatenation" (§3.1.3); then a short fine-tune of the whole MoE on the full data. Appendix E: during submodel training "the gating network is not utilized".
- **Key findings (with locators, v1):**
  - Table 1 (steps for the MoE-DisCo fine-tune to reach the full-parameter run's final loss): Qwen/C4 21,150 full-parameter steps vs 4,100 fine-tune steps (loss 4.954 vs 4.925; PPL 230.32 vs 165.86); Qwen/WikiText-2 12,500 vs 3,150; Qwen/OpenWebText 28,600 vs 6,650; Llama/C4 11,750 vs 4,150; Llama/WikiText-2 15,000 vs 5,300 (PPL 160.91 vs 163.27, MoE-DisCo worse); Llama/OpenWebText 21,000 vs 7,800.
  - **Baseline definition:** "full-parameter" training of the same MoE. The step comparison counts only the fine-tune phase; the submodel phase (Table 6: 4,200 to 5,922 steps per submodel, four submodels) is excluded and appears only in the dollar-cost table (Table 3). So it is neither equal compute nor equal tokens; it is "steps of expensive GPU to reach the same training loss".
  - PPL and loss are inconsistent within Table 1 (exp(4.954) ≈ 142, not 230), so PPL must be measured on a different set than the loss; the paper does not say which (could not verify).
  - Table 2 (Qwen, OpenWebText, downstream): ARC-e 27.9 vs 29.1, MMLU 23.0 vs 25.3, HellaSwag 27.45 vs 29.45, PIQA 52.25 vs 57.03 (full-parameter vs MoE-DisCo). All near chance (inference), so these do not separate the methods.
  - Table 3: total cost reduction 47.6% to 69.5%, using $0.35 per RTX 4090 hour and $2.28 per A100 hour.
  - §4.5.1, Fig. 6 (Qwen, C4): replacing k-means with random data assignment, "the final performance essentially regresses to that of full-parameter training". Figure only; no number.
  - §4.5.2, Fig. 7: 4 experts slightly better than 2 (figure only).
- **Remedy tags:**
  - [REMEDY | no router during independent training, gate fit in a short central fine-tune after concatenation | masked routing / router misalignment | 2.7B and 3.5B MoE, 4 experts | pretraining-style | reaches the full-parameter run's loss in 19% to 37% of its step count (my arithmetic from Table 1), counting fine-tune steps only | Table 1, §3.1.3, App. E]
  - [REMEDY | cluster-based (non-random) data assignment to experts | specialization | same | same | random assignment loses the advantage ("regresses to" full-parameter) | §4.5.1, Fig. 6]
- **Bears on:** Q4; Q5 (central router fit); Q2 (specialization needs differing data); cost "masked routing +3.2%".
- **How it differs from ours:** one-shot (never re-synchronized), one expert per worker, no routing at all during local training (we route top-2 over 4 held experts), non-IID clustered data (ours IID), billions of parameters, BPE tokens, unclear initialization, a central fine-tune on high-memory hardware (we have none).
- **Question it raises for us:** if we dropped local routing entirely (each worker trains its experts as fixed dense paths) and fit the router centrally after each merge, does the masked-routing share of our gap disappear, and what does the central step cost at 46M?
- **Axes:** worker stores shared backbone plus one expert; routing during local training: none (gate unused); averaged: shared parameters over all E submodels (weighted), experts not averaged (concatenated); slice: 1 of 4 experts; sync: one-shot, then central fine-tune.

### 2. Branch-Train-MiX: Mixing Expert LLMs into a Mixture-of-Experts LLM (BTX)

- **Authors:** Sainbayar Sukhbaatar, Olga Golovneva, Vasu Sharma, Hu Xu, Xi Victoria Lin, Baptiste Rozière, Jacob Kahn, Daniel Li, Wen-tau Yih, Jason Weston, Xian Li (FAIR at Meta).
- **Year / venue:** 2024; v1 states no venue, so recorded here as preprint (a later venue may exist; not verified).
- **arXiv:** 2403.07816; v1 12 Mar 2024 (only version). Read: v1. https://arxiv.org/abs/2403.07816. DOI 10.48550/arXiv.2403.07816.
- **Code / licence:** no official code found (paper gives none; GitHub search found only a third-party toy reimplementation, `empty-crayon/branch-train-mix-moe`, SmolLM-135M, no licence).
- **Read status:** full text including appendices A to C; references skipped. Table 2 is garbled by `pdftotext`; I mapped rows by checking the Llama-2 7B row against Table 1 (math 8.6 = mean of 14.7 and 2.5) and the BTX Top-2 row against Table 3 (27.4/34.0/41.0/63.5/52.5/47.9).
- **Setting and scale:** seed Llama-2 7B; three copies continue-pretrained on math (201B tokens, 48k steps), code (210B tokens, 50k steps) and Wikipedia (42B tokens); the seed itself is the fourth expert. MoE fine-tune 80B tokens (Sample Top-1: 160B), top-2, load balancing α = 0.01, AdamW wd 0.1, peak lr 1e-4, batch 4M tokens, sequence 4096 (§4.1). Continued pretraining at 7B, not from scratch.
- **Method:** feedforward layers of the N experts become N experts of an MoE layer; "self-attention layers ... simply averaging their weights", same for embeddings and the remaining parameters (§3.2); a new router W_l per layer; then MoE fine-tuning on all data.
- **Key findings (v1):**
  - Table 2 average score (all models trained on the same data and amount, except that BTM has no fine-tune stage): Llama-2 7B 40.7; Llama-2 13B 45.4; Dense (DM) 44.5; Sparse upcycling (DM) Top-2 46.3; BTM Top-1 43.1; BTM Top-2 43.4; BTX Sample Top-1 47.3; BTX Top-2 47.9.
  - **Baseline definitions:** "DM" = data-matching (same data, same order of stages, §4.1.2); "CM" = compute-matching in GPU-days (§4.1.2, Table 3).
  - Table 3 (compute-matched): BTX 23% of compute in MoE training, 7.8 days, 926.1 GPU-days, 533B tokens, average 47.9; sparse upcycling (CM) 100% MoE compute, 7.9 days, 1007.1 GPU-days, 252B tokens, average 47.3. So at roughly equal GPU-days, training experts apart then mixing slightly beats training the MoE jointly from the seed (+0.6 average points), because the parallel stage processes about twice the tokens.
  - BTM Top-2 (43.4) vs BTX Top-2 (47.9): the MoE fine-tune adds 4.5 average points; this conflates learned routing with the 80B extra fine-tune tokens (the Table 2 caption says BTM lacks the fine-tune stage).
  - Table 5 (10B fine-tune tokens): BTX 34.7; no load balancing 34.6; no load balancing and experts frozen 34.7; "blending experts" 22.2; split into 8 experts, top-2 28.0; top-4 34.5. §4.3.1: the fine-tune "mainly trains the other parameters such as averaged weights in the self-attention" and the router.
  - Table 4 (no load balancing, 10B tokens): Switch Top-1 24.7, Sample Top-1 33.0, Top-2 34.6, soft routing 35.8.
  - §4.3.2: without load balancing the Code expert becomes a dead expert; load balancing revives it.
- **Remedy tags:**
  - [REMEDY | central MoE fine-tune that learns a new router after averaging non-expert weights | masked routing / router misalignment and averaging damage to attention | 7B seed, 4 experts | continued pretraining | +4.5 average points over BTM Top-2, conflated with 80B extra tokens; freezing experts during the fine-tune changes nothing (34.7 vs 34.7) | Table 2, Table 5, §4.3.1]
  - [REMEDY | Switch-style load-balancing loss during router fit | dead experts | same | same | revives a dead expert; 34.7 vs 34.6 average | §4.3.2, Table 5]
- **Bears on:** Q4, Q5 (central router fit), Q2 (dead experts, load balancing), Q1 (one-shot averaging of attention is repaired by fine-tuning).
- **How it differs from ours:** one-shot, whole-model branches from a strong 7B checkpoint, domain-split data, router never trained locally, 80B-token central fine-tune; nothing about 46M from-scratch character models.
- **Question it raises for us:** how much of our sliced-arm gap would a short central fine-tune of router and shared part (after the final merge only) recover, compared with the same steps spent on more local training?
- **Axes:** worker stores the full dense seed copy; routing during local training: none; averaged: attention, embeddings and other non-FF parameters uniformly over the 4 branches; FF layers concatenated as experts; slice: one FF expert per layer per branch; sync: one-shot, then central fine-tune.

### 3. Branch-Train-Merge: Embarrassingly Parallel Training of Expert Language Models (BTM)

- **Authors:** Margaret Li, Suchin Gururangan, Tim Dettmers, Mike Lewis, Tim Althoff, Noah A. Smith, Luke Zettlemoyer (University of Washington, Allen Institute for AI, Meta AI).
- **Year / venue:** 2022; v1 states no venue: preprint.
- **arXiv:** 2208.03306; v1 5 Aug 2022 (only version). Read: v1. https://arxiv.org/abs/2208.03306. DOI 10.48550/arXiv.2208.03306.
- **Code / licence:** https://github.com/hadasah/btm (paper footnote 2). GitHub API on 2026-10-11: MIT, created 2022-08-02, last push 2024-04-29, 79 stars, not archived.
- **Read status:** sections read: §1 to §9 (all main text) and appendix Table 9, Table 13 and Figure 10; skipped: references and appendix Tables 10 to 12 (domain lists and de-identification regexes).
- **Setting and scale:** GPT-3-style LMs trained from scratch in fairseq at 125M, 350M, 750M and 1.3B parameters per expert LM (ELM); 8 training domains (73.8B training tokens, appendix Table 9) plus 8 evaluation domains; 16/32/64/128 GPUs; 80k/32k/24k/12k updates; lr 5e-4 (§4.1). Pretraining.
- **Method:** a seed LM is trained on all data; it is copied k times; each copy trains on one domain with no communication; ELMs are ensembled at inference using a domain posterior estimated from 100 development sequences ("cached prior", §2.3) or collapsed by parameter averaging.
- **Baseline definition:** compute-matched in number of updates (§4.1: "These models are compute-matched"); the ELMForest has 8× the parameters of the dense Transformer-LM. §6 (64 domains) is "intentionally not compute-matched" (§6.2).
- **Key findings (v1):**
  - Table 1 (average test PPL over all 16 domains): 125M Transformer-LM 22.5 ± 0.14, DEMix 20.8 ± 0.63, ELMForest 19.8 ± 0.05 (8 seeds); 350M 18.5 / 17.5 / 16.7; 750M 17.0 / 15.6 / 15.0; 1.3B 16.3 / 15.6 / 14.6.
  - **Random splits (the IID analogue):** Table 4, "Random Ensemble (seed init)", all-domain PPL 24.7 (125M), 21.5 (350M), 19.2 (750M), 18.9 (1.3B), against the compute-matched Transformer-LM 22.5, 18.5, 17.0, 16.3. The random-split ensemble is worse than the dense model at every scale: +9.8% to +16.2% perplexity, +3.0% to +5.3% in log-perplexity (my conversion). Abstract: "LM ensembles with random data splits do not perform well".
  - Table 3 (collapsing by parameter averaging): uniform average on training domains 47.4 (125M), 19.9, 19.0, 18.0 vs Transformer-LM 19.9, 16.3, 14.7, 14.2; posterior-weighted average 18.0, 15.1, 13.9, 13.4.
  - §5.2, Fig. 5: averaging ELMs trained from a shared random initialization with no seed phase gives "perplexities in the thousands"; a seed phase of about 40% to 60% of compute is best for ensembling (Fig. 4) and about 60% to 70% for averaging.
  - Table 2 caption: branched training gives a 33% speed-up in updates per second at 1.3B.
  - §6: 64 domains, 22.4B total parameters; "comparable" to a 1.3B Transformer-LM using about 40% of its GPU hours (Fig. 7; numbers in that figure are annotations I could not map with certainty, so not recorded).
- **Remedy tags:**
  - [REMEDY | shared seed (warm-up) phase before branching | averaging cost after independent training | 125M to 1.3B | pretraining | without it, parameter averaging gives PPL "in the thousands"; ensembles also worse | §5.2, Fig. 4, Fig. 5, Table 4]
  - [REMEDY | domain (provenance) data split instead of random split | specialization | same | same | random split: +3.0% to +5.3% log-PPL worse than dense; domain split: better than dense | Table 1, Table 4]
  - [REMEDY | sequence-level ensembling by domain posterior instead of parameter averaging | averaging cost | same | same | ensemble 17.2 vs uniform average 47.4 (125M, train domains) | Table 3]
- **Bears on:** Q4; Q2 (experts trained apart on IID data do not help); Q1 (averaging independently trained models fails without shared trajectory); modular-paths fallback.
- **How it differs from ours:** whole models, no shared part after the seed phase, no synchronization at all, sequence-level inference routing, domain-labelled data, 8× parameters at equal compute; ours averages every 125 steps and holds 4 of 8 experts.
- **Question it raises for us:** our workers see IID data; BTM's random-split result suggests experts trained on IID shards have nothing to specialize on. Does skewing our data per worker (supported by the harness) change the masked-routing cost?
- **Axes:** worker stores a full LM; routing during training: none (data pre-split by domain); averaged: nothing during training (optional posterior-weighted average at inference; new ELMs initialized from averages); slice: whole model; sync: none after the seed phase (4 BTM iterations in §6).

### 4. DiPaCo: Distributed Path Composition

- **Authors:** Arthur Douillard, Qixuan Feng, Andrei A. Rusu, Adhiguna Kuncoro, Yani Donchev, Rachita Chhaparia, Ionel Gog, Marc'Aurelio Ranzato, Jiajun Shen, Arthur Szlam (Google DeepMind).
- **Year / venue:** 2024, preprint.
- **arXiv:** 2403.10616; v1 15 Mar 2024 (only version). Read: v1. https://arxiv.org/abs/2403.10616. DOI 10.48550/arXiv.2403.10616.
- **Code / licence:** none from the authors. OpenDiPaCo (see block 10) is a third-party MIT reimplementation.
- **Read status:** full text including supplementary §7.1 to §7.3; references skipped. Hyperparameter Table 4 is garbled in the text layout; I rely on §4 and §7.1 for hyperparameters.
- **Setting and scale:** C4, SentencePiece 32k; each path 150M parameters (12 blocks, width 896, 16 heads); sequence 1,024, batch 512, cosine lr peak 4e-4; 88,000 weight-update steps; inner steps τ = 150 (§4.2; Table 5 uses 62); outer optimizer Nesterov, outer lr 0.7, momentum 0.9 (§7.1). DiPaCo runs start from a pretrained 150M model (Algorithm 1 requires one; Fig. 8: pretrained for 24k steps). Pretraining.
- **Method:** modules per level; a path picks one module per level (2×4, 8×8, 16×16 = 256 paths); routing once per document from the first 32 tokens, offline, so data are pre-sharded by path; k-means first, then one discriminative re-sharding round with a logistic-regression router (§2.4, §7.2.1); each worker trains one path; per-module DiLoCo: each module's outer gradient is averaged over the paths through it (Algorithm 1, line 13), weighted by shard size (Eq. 2 to 3) and with its norm "rescaled ... by the square root of the number of paths" (§2.7); path-specific modules still get the outer optimizer (footnote 1); optional top-2 overlapping shards and per-path early stopping.
- **Baseline definition:** §4: the comparison counts weight-update steps; "this comparison is not standard in the literature", because DiPaCo sees more tokens and FLOPs per step. Table 1 states compute and data multiples explicitly.
- **Key findings (v1):**
  - Table 1 (validation PPL; "Time" and "Compute and Data" multiples): Baseline 150M 1×/1× 16.23; DiLoCo P=8 1×/8× 15.02; DiLoCo P=64 1×/64× 14.96; Flat MoE P=8 (8 independent paths, 1.2B) 14.62; Flat MoE P=64 (9.6B) 12.76; DiPaCo 2×4 (0.5B) 14.86; DiPaCo 8×8 (1.2B) 13.37; DiPaCo 8×8 plus path-specific modules (5.3B) 12.70; **Baseline 8× steps (equal compute and data to the P=8 rows) 14.72.** At equal compute with 8 workers: DiLoCo 15.02 (+0.8% log-PPL vs 14.72, my conversion), DiPaCo 2×4 14.86 (+0.4%), flat MoE 14.62 (−0.3%).
  - §4.5: DiPaCo trained with DiLoCo vs fully synchronous per-step training of the same paths: DiLoCo better by 0.3 PPL (2×2) and 0.6 PPL (4×4); synchronous better by 0.1 PPL (8×8).
  - Table 2 (flat MoE after 10K steps): 8 paths 14.6, 16 paths 13.9, 256 paths 14.2 (over-fitting); 13.6 with overlapping shards and early stopping.
  - Table 3 (16×16, 256 paths; dense 1B = 11.41): routing once per sequence 12.39 (12.22 with early stopping); re-route every 128 tokens 11.48; 64: 11.38; 32: 11.31; 16: 11.26. The 1B-matching claim needs re-routing every 64 tokens at test time. (This corrects the earlier survey, which summarized DiPaCo as beating the 1B model with one path.)
  - Table 5 (8×8, 32 outer × 62 inner steps): k-means sharding 17.2, product k-means 16.8, discriminative 16.5.
  - Fig. 11 caption (16-path flat MoE): 14.0, 13.38, 13.36, 13.25 PPL after 0 to 3 alternating router phases.
  - §6: DiPaCo is "significantly less FLOP efficient per evaluation perplexity than a standard dense compute optimal model"; one path size, one dataset.
- **Remedy tags:**
  - [REMEDY | per-module outer Nesterov (lr 0.7, momentum 0.9) with outer-gradient norm rescaled by sqrt(paths through module) and shard-size weighting | local averaging cost with uneven holder counts | 150M paths, 8 to 256 paths | pretraining (from a pretrained 150M) | no isolated ablation of the rescaling or weighting reported; DiLoCo vs synchronous −0.3 / −0.6 / +0.1 PPL | §2.7, Eq. 2 to 3, §4.5]
  - [REMEDY | sequence-level offline routing with discriminative re-sharding | masked routing / router co-training | 8×8 | pretraining | 16.5 vs 17.2 (k-means) | Table 5]
  - [REMEDY | more frequent re-routing at evaluation | routing granularity | 16×16 | pretraining | 12.39 → 11.38 PPL (every 64 tokens) | Table 3]
  - [REMEDY | overlapping top-2 shards plus per-path early stopping | over-fitting of many independent paths | flat MoE 256 paths | pretraining | 14.2 → 13.6 PPL | Table 2]
- **Bears on:** Q1 (DiLoCo vs synchronous at 150M), Q4, Q5 (outer optimizer, per-module averaging, modular paths); our fallback.
- **How it differs from ours:** paths instead of experts within a layer; routing per document and offline, so no router is trained during local steps; data pre-sharded (non-IID across paths); Nesterov outer optimizer; initialized from a pretrained model; 150M paths; BPE tokens.
- **Question it raises for us:** at equal compute DiPaCo's own table shows a 150M dense model trained 8× longer slightly beating DiLoCo-8 and DiPaCo 2×4; would our modular-paths fallback at 46M beat our centralized MoE at equal compute, or only a dense model of path size?
- **Axes:** worker stores one path (one module per level); routing during local training: none (pre-sharded by a sequence-level router); averaged: each module over the paths that contain it, Nesterov outer step, norm rescaled by sqrt(path count), shard-size weights; module sizes: levels of several transformer blocks, path 150M; sync: every 150 inner steps (62 in Table 5).

### 5. No Need to Talk: Asynchronous Mixture of Language Models (SMALLTALK LM)

- **Authors:** Anastasiia Filippova, Angelos Katharopoulos, David Grangier, Ronan Collobert (EPFL; Apple).
- **Year / venue:** ICLR 2025 ("Published as a conference paper at ICLR 2025", page header).
- **arXiv:** 2410.03529; v1 4 Oct 2024; v2 15 Apr 2025. Read: v2. https://arxiv.org/abs/2410.03529. DOI 10.48550/arXiv.2410.03529.
- **Code / licence:** none linked in the paper; none found by GitHub search.
- **Read status:** full text including appendices A to C; references skipped. The per-subject MMLU tables (Tables 4 and 5) are garbled in the text layout; not used.
- **Setting and scale:** RedPajama-V2; experts 335M (24 layers, width 1024) with 4, 8, 16, 32 experts and 1.3B (24 layers, width 2048) with 4, 16, 32 experts; routers 4.4M parameters; sequence 1,024; routing prefix 256 tokens; AdamW β2 0.99, wd 0.1, lr 5e-4 cosine (§3.1, App. A.1). Pretraining from scratch.
- **Method:** E small router LMs are trained by EM on random then balanced assignments; each sequence goes to the expert whose router gives the prefix the highest likelihood; experts are trained as fully independent LMs on disjoint routed shards; at inference one expert per sequence.
- **Baseline definition:** a dense model of the size of one expert, trained on the same number of tokens (equal training FLOPs within 0.07% to 4.14%; equal inference FLOPs within 0.36% to 10.13%; App. Table 3). The mixture has E× the total parameters. Experts are trained at batch 128 vs dense batch 512 to 2048 (App. Table 2).
- **Key findings (v2, App. Table 3, test PPL dense → mixture):** 335M: 4 experts 11.78 → 10.78 (8.49%); 8 experts 11.25 → 10.20 (9.33%); 16 experts 10.80 → 9.64 (10.74%); 32 experts 10.5 → 9.07 (13.62%). 1.3B: 4 experts 9.10 → 8.75 (3.85%); 16 experts 8.48 → 7.42 (12.53%); 32 experts 8.20 → 6.76 (17.56%). §3.2: 32 × 335M experts reach 9.07 vs the 1.3B dense model's 9.11 at about the same training FLOPs and a third of the inference FLOPs.
  - Fig. 4a: router sizes 4.4M to 335M "perform practically identically"; Fig. 4c: TF-IDF plus balanced k-means routing does worse than the LM routers (figures only).
  - Fig. 5: every expert beats the dense baseline on its own routed segment (figure only).
- **Remedy tags:**
  - [REMEDY | fully independent experts with sequence-level prefix routing by small router LMs (no token-level router trained with the experts) | masked routing and local averaging (both removed) | 335M and 1.3B experts, E = 4 to 32 | pretraining | 3.85% to 17.56% lower PPL than an equal-FLOP dense model of expert size | App. Table 3]
- **Bears on:** Q4, Q5 (modular designs), fallback.
- **How it differs from ours:** no shared part, no averaging, no token-level MoE; data routed so each expert sees a different shard (not IID); E× parameters; compares with a dense model, not with a centrally trained MoE of equal total size.
- **Question it raises for us:** with only 4 workers, SMALLTALK's smallest gain (4 experts: 3.85% at 1.3B) is its weakest; would whole-model experts at our scale and worker count beat our centralized 46M MoE at all?
- **Axes:** worker stores one full expert LM (plus its small router); routing during training: sequence-level, fixed before expert training; averaged: nothing; slice: whole model; sync: experts never; routers exchange scores about every 45M tokens (about 94 times, App. A.4).

### 6. DEPT: Decoupled Embeddings for Pre-training Language Models

- **Authors:** Alex Iacob, Lorenzo Sani, Meghdad Kurmanji, William F. Shen, Xinchi Qiu, Dongqi Cai, Yan Gao, Nicholas D. Lane (University of Cambridge; Flower Labs; BUPT).
- **Year / venue:** ICLR 2025 (page header).
- **arXiv:** 2410.05021; v1 7 Oct 2024; v2 8 Oct 2024; v3 21 Oct 2024; v4 2 Apr 2025; v5 7 Apr 2025. Read: v5. https://arxiv.org/abs/2410.05021. DOI 10.48550/arXiv.2410.05021.
- **Code / licence:** no link in the paper (it names MosaicML Composer and Flower as the software base, App. A.1.1); none found by GitHub search.
- **Read status:** full text including appendices A to F; references skipped. Some appendix tables (Tables 15, 17, 21) are garbled; numbers below come only from tables that parsed cleanly.
- **Setting and scale:** decoder-only models with bodies of 86.4M (12 blocks) and 298.5M (24 blocks), sequence 2,048, batch 256 per source; a 1.2B multilingual run (App. B.1); The Pile (16 sources) and MC4 (8 languages); inner AdamW, outer "parameter averaging" (FedAvg); N_local = 500 local steps; 4 of 16 sources per round (multi-domain) or 3 of 8 (multilingual); T = 10 or 27 rounds (Tables 8 and 9). Pretraining.
- **Method:** GLOB (shared embeddings, plain local SGD), TRIM (embeddings trimmed to each source's vocabulary, re-projected for averaging), SPEC (embeddings private per source, never averaged); after pretraining, continued pretraining (15% to 19% more steps) with a new embedding matrix (§3.5).
- **Baseline definition:** standard synchronous training (STD) for "the same number of training steps" (App. A.1); the only hyperparameter changed is the learning rate, which was lowered for STD until it no longer diverged (App. A.1.2). Each DEPT round trains |S_t| sources in parallel at the same per-source batch, so DEPT processes about |S_t| times the tokens of STD per sequential step (inference from Table 8 and A.1; the paper does not state a token match).
- **Key findings (v5):**
  - Table 3 (24 blocks, The Pile, continued pretraining from random embeddings, average validation PPL): STD α=0 56, STD α=1 36.9, GLOB 31.6, TRIM 33.3, SPEC 32.7, SPEC-OPT 31.2.
  - Table 12 (12 blocks, same protocol): STD α=0 62.2, α=1 57.0, ACT 114.9, GLOB 42.9, TRIM 40.8, SPEC 43.2.
  - Table 5 (24 blocks, pretrained embeddings kept): STD α=0 22.3, α=1 22.8, GLOB 21.1, TRIM 23.7.
  - Table 13 (12 blocks, pretrained embeddings kept): STD α=0 31.2, α=1 31.9, GLOB 32.4, TRIM 31.1. At this smaller body, plain local SGD (GLOB) is 3.8% worse in PPL than STD α=0 (+1.1% log-PPL, my conversion). App. B.7: "the aggregation procedure may be overly harsh on the embedding parameters" at this scale.
  - App. B.3, Fig. 7 (IID random shards of C4): "DEPT performs similarly to standard pre-training" (figure only).
  - App. B.8, Table 14 (24 blocks, The Pile): DEPT averages 31.2 to 33.3 vs 33.9 to 226.9 for single-source models never averaged.
  - Table 2: 714× lower communication for the billion-scale multilingual SPEC-OPT run.
- **Remedy tags:**
  - [REMEDY | keep token embeddings local or trimmed (not averaged) while averaging the transformer body | averaging cost under vocabulary heterogeneity | 86M to 298M bodies | pretraining | TRIM/SPEC within about 1 to 2 PPL of GLOB with random-init embeddings (Table 3); TRIM worse than GLOB with pretrained embeddings (23.7 vs 21.1, Table 5) | Tables 3, 5, 12, 13]
- **Bears on:** Q1 (local averaging at H = 500 with plain averaging vs per-step training), Q5 (embedding decoupling).
- **How it differs from ours:** dense model (no MoE); non-IID sources; per-source vocabularies (our character vocabulary is tiny, so the vocabulary-dilution motivation does not apply, inference); baseline matched in sequential steps with a lowered learning rate rather than equal compute.
- **Question it raises for us:** DEPT finds averaging harsher at its smallest body (86M); is part of our +6.1% averaging cost a small-model effect that more local steps or a different outer step would change?
- **Axes:** worker stores full body plus embeddings (full, trimmed or private); routing: not applicable; averaged: body over the sources sampled that round (plain averaging), embeddings per variant; module sizes: embeddings vs body; sync: every 500 local steps.

### 7. Towards Crowdsourced Training of Large Neural Networks using Decentralized Mixture-of-Experts (Learning@home)

- **Authors:** Max Ryabinin, Anton Gusev (Yandex / HSE; independent).
- **Year / venue:** NeurIPS 2020 (journal reference on the arXiv page: Advances in Neural Information Processing Systems 33 (2020) 3659-3672).
- **arXiv:** 2002.04013; v1 10 Feb 2020; v2 14 Jun 2020; v3 21 Oct 2020. Read: v3. https://arxiv.org/abs/2002.04013. DOI 10.48550/arXiv.2002.04013.
- **Code / licence:** https://github.com/mryab/learning-at-home (footnote 3). GitHub API: no licence detected and no LICENSE file in the root (files: README.md, experiments, lib, requirements.txt, two images); created 2020-02-10, last push 2020-11-05. Its maintained successor library `learning-at-home/hivemind` is MIT, last push 2026-01-11.
- **Read status:** full text including broader impact and appendices A to E; references skipped.
- **Setting and scale:** Decentralized MoE (DMoE) layers whose experts live on volunteer "runtimes" found through a Kademlia DHT; trainers run a product-key gating function and call remote experts every step, asynchronously. Experiments: throughput with 224 feed-forward or Transformer blocks over 4 GTX 1080 (§4.1); MNIST convergence (§4.2); Transformer-XL on WikiText-2 with 256 experts over 16 layers, top-4, 32 trainers, 1,000 ms latency, 10% failure rate (§4.3).
- **Key findings (v3):**
  - Table 2 (3 cloud K80s across regions, samples/s): feed-forward model parallel 7.23 ± 0.06 vs Learning@home 300.8 ± 15.9; Transformer 0.01 ± 0.001 vs 0.68 ± 0.01.
  - DHT beam search for top-4 experts: 317 ± 58 ms (100 nodes), 528 ± 127 ms (1,000), 764 ± 106 ms (10,000) (§4.1).
  - Language-model quality: Fig. 6 only, no table; I could not extract a number. Text: "the 10% failure rate has a positive effect on the DMoE performance" (§4.3), attributed to a dropout-like effect on a small dataset.
  - §3.2: failed experts are excluded and the gate weights renormalized; trained this way the mixture learns overlapping specializations.
- **Remedy tags:** [REMEDY | exclude unavailable experts and renormalize gate weights during training | worker dropout / fault tolerance | small Transformer-XL, WikiText-2 | pretraining | qualitative (figure only) | §3.2, §4.3, Fig. 6]
- **Bears on:** Q4 only marginally (it is not local training on a slice); the renormalization over available experts is the same operation as our masked top-2 softmax over held experts.
- **How it differs from ours:** synchronous per-step remote expert calls (no local steps, no averaging), every expert has one owner, no quality comparison with centralized training in numbers.
- **Question it raises for us:** Learning@home renormalizes over reachable experts and claims it builds redundancy; is "overlapping specialization" the same phenomenon as the interchangeable experts in our Task A?
- **Axes:** a runtime stores some experts; routing: trainer's gating over the experts it can reach, renormalized over responders; averaged: nothing (experts are updated in place by the gradients sent to them); slice: per runtime capacity; sync: every step (asynchronous remote calls).

### 8. FoMoE: Breaking the Full-Replica Barrier with a Federation of MoEs (follow-up, read)

- **Authors:** Lorenzo Sani, Zeyu Cao, Meghdad Kurmanji, Alex Iacob, Andrej Jovanović, Yan Gao, Wanru Zhao, Nicholas D. Lane (Cambridge ML Systems Lab; Flower Labs). Same lab as DEPT and Photon.
- **Year / venue:** 2026, "Preprint." (page 2 footer).
- **arXiv:** 2606.19025; v1 17 Jun 2026; v2 20 Jun 2026 (arXiv API published/updated dates). Read: v2 (PDF and, for Table 6, the HTML of v2). https://arxiv.org/abs/2606.19025. DOI 10.48550/arXiv.2606.19025.
- **Code / licence:** none linked; none found by GitHub search (2026-10-11).
- **Read status:** full text including appendices A to G; references skipped.
- **Why it is here:** found as a 2026 citer of DiPaCo in Semantic Scholar's citation list. Note for the report writer: it may also be found by the researcher chasing SPES citers.
- **Setting and scale:** trained proxy only: "Small Proxy (54M)", d_model 256, 4 layers, 8 experts of hidden size 128, 2 active (Table 1); GPT-oss tokenizer with vocabulary 200,019, tied embeddings, sequence 2,048 (Table 7). With these figures the embedding matrix alone is about 51M of the 54M parameters (my arithmetic: 200,019 × 256), so the experts are a tiny part of the model, unlike ours. Data: SmolLM corpus (fineweb-edu-dedup and python-edu, 90/10), i.i.d. partitions; evaluation on C4 validation (a different distribution). Global batch 1,024 sequences split over M workers; 640 optimizer batches, 160 warmup, about 1.34B tokens (Table 7), so K = 32/64/128 means 20/10/5 rounds (my arithmetic). AdamW lr ≈ 0.01, wd 0; σ-MoE sigmoid routing; Peri-LN; local optimizer state kept across rounds (§3.4). Outer: DiLoCo/Nesterov (0.7, 0.9) or LocalAdamW (averages optimizer moments too). 3 seeds. Larger configurations (150M to 100B) are cost-model projections only (§6.4, §7). Pretraining.
- **Method:** each worker holds the dense part plus O_e·N_e/M experts per layer; O_e is the number of workers holding each expert. "For most of our work, we partition each router, along with the experts," so that tokens are "not routed to experts that are unavailable to the local worker" (§3.3.3). The dense part is averaged over all workers; experts are averaged within their replica group (Algorithm 2). A "skip-token" variant keeps the full router and skips tokens sent to non-resident ("ghost") experts. Placement fixed or randomly reshuffled.
- **Baseline definition:** iso-token and iso-parameter (§5, §6.1); "full replica" = O_e = M; "centralized" is a single-site reference shown only in Fig. 5, with no number in the text or tables.
- **Key findings (v2):**
  - Table 6 (LocalAdamW, fixed placement, validation PPL, mean ± std), M = 4: K = 32: O_e=1 121.42, O_e=2 112.00, O_e=4 (full replica) 103.91. K = 64: 130.79, 119.53, 104.47. K = 128: 143.72, 123.50, 111.89. So O_e = 2 of 4 costs +7.8% / +14.4% / +10.4% PPL vs full replica, +1.6% / +2.9% / +2.1% in log-PPL (my conversion); O_e = 1 costs +3.4% / +4.8% / +5.3% log-PPL.
  - Same table, LocalAdamW, M = 8, K = 128: fixed placement O_e = 1/2/4/8 gives 181.07 / 156.84 / 138.88 / 159.71, and random placement O_e = 4 gives 131.86. Here partial replication (O_e = 2 or 4) beats full replication. The full-replica M = 8, K = 128 run (159.71) is also much worse than M = 4 (111.89), a worker-count effect within the same table.
  - Same table, DiLoCo outer, fixed, M = 4: K = 32: O_e=2 130.58 vs O_e=4 137.27 (partial better); K = 64: 142.25 vs 124.17; K = 128: 383.65 vs 420.49 (both very poor).
  - Tables 4 and 5 (captioned only "across different configurations of workers M and synchronization frequencies K"; their values equal the O_e = M entries of Table 6, so I read them as full replica, inference): LocalAdamW 103.91 to 111.89 at M = 4 over K = 32 to 128; DiLoCo 137.27, 124.17, 420.49. §6.1 and Fig. 5 name LocalAdamW the stronger full-replica baseline.
  - §6.2: "Smaller values of Oe achieve higher perplexity under an iso-token training budget"; O_e ≥ 4 best balances quality and cost; random reshuffling does not help in the i.i.d. sweep.
  - §6.3, Fig. 7: skip-token adds configurations with lower PPL at comparable FLOPs (figure only).
  - Fig. 11: up to 1.4× measured throughput from skip-token (150M MoE, 8 B200).
  - The "±" values (about ±14 on PPL near 105) are described as the spread across the dataset in §5 but as the spread across seeds in Table 7; this inconsistency is unresolved. Claims of "high routing entropy" and no expert collapse (§1) are not backed by a table or figure I could find.
- **Remedy tags:**
  - [REMEDY | sigmoid (σ-MoE) gating so that a missing expert "must not skew the probability distribution of the remaining available experts" | masked routing (softmax renormalization over held experts) | 54M proxy | pretraining | no ablation against softmax reported | App. B.3.2]
  - [REMEDY | more holders per expert (higher O_e) | masked routing plus partial updates | 54M proxy, M = 2 to 8, K = 32 to 128 | pretraining | M = 4, K = 128: O_e 1 → 2 → 4 gives 143.72 → 123.50 → 111.89 PPL | Table 6]
  - [REMEDY | LocalAdamW (average optimizer moments too) instead of DiLoCo outer Nesterov; keep local optimizer state | local averaging cost | 54M proxy | pretraining | full replica M = 4, K = 128: 111.89 vs 420.49 | Tables 4, 5]
  - [REMEDY | skip-token: route over all experts, skip non-resident | masked routing | 54M proxy | pretraining | lower PPL at comparable FLOPs (figure only) | §6.3, Fig. 7]
- **Bears on:** Q4 (closest match found in this strand), Q2, Q3, Q5; costs: masked routing +3.2% and partial updates +1.4% together (its O_e sweep changes both at once).
- **How it differs from ours:** synchronized optimizer moments (LocalAdamW) or Nesterov outer (ours: plain averaging, fresh AdamW each round); sigmoid router (ours: softmax top-2); embeddings dominate parameters; 5 to 20 rounds (ours 40); BPE with a 200k vocabulary (ours characters); evaluation off-distribution; no centralized number. Mapping our sliced arm to "M = 4, O_e = 2, fixed placement" is my inference.
- **Question it raises for us:** FoMoE's partial-replica cost at M = 4, O_e = 2, K = 128 is about +2.1% in log-PPL vs full replica, against our +4.4% (sliced vs full averaging); is the difference due to its sigmoid router, its persistent optimizer state, or its tiny expert share?
- **Axes:** worker stores dense part (embeddings, attention, norms, shared experts) plus O_e/M of experts with their router rows; routing during local training: masked to resident experts (default) or skip-token; averaged: dense over all workers, experts and router rows within replica groups, outer DiLoCo or LocalAdamW; slice: O_e/M of experts (1/M to 1); sync: every K = 32/64/128 steps.

### 9. KALAVAI: Predicting When Independent Specialist Fusion Works (follow-up, read)

- **Authors:** Ramchand Kumaresan (Murai Labs). Single author.
- **Year / venue:** 2026, "Preprint."
- **arXiv:** 2603.22755; v1 24 Mar 2026; v2 27 Mar 2026 (arXiv API). Read: v2. https://arxiv.org/abs/2603.22755. DOI 10.48550/arXiv.2603.22755.
- **Code / licence:** footnote 2 gives github.com/mechramc/Kalavai, which redirects to `Murai-Labs/Kalavai`; GitHub API: no licence detected, created 2026-03-09, last push 2026-08-04.
- **Read status:** sections read: §1 to §7 (all main text). Appendices A to S not read (including the evaluation-correction appendix S and the results-integrity audit P).
- **Why it is here:** a 2026 citer of BTX that measures when training apart pays off and whether routing must be learned.
- **Setting and scale:** Pythia-410M, 1B, 6.9B from the step-10000 checkpoint (7% of pretraining); 3 domain specialists (code, science, fiction), 2,000 steps each, batch 8, sequence 512, lr 2e-5; 500 router steps; first K layers optionally frozen (§4.1). Fine-tuning (continued training of a partly trained checkpoint), domain-split data. The fused model runs all N specialists and mixes their logits (§3), so inference costs about N×.
- **Key findings (v2):**
  - Table 1 (410M, equal-weight loss): base 2.651, best specialist 2.404, weight averaging 2.486, monolithic 2.229, MoE fusion 2.218.
  - Table 4 (equal compute: monolithic 6,000 steps vs 3 × 2,000): 410M MoE +0.47% over monolithic; 1B 2.090 vs 2.097 (+0.34%). With 3× parameters and 3× inference.
  - §4.5: uniform routing −1.19% vs best specialist; trained linear router +7.70%; MLP +7.72%. "Routing must be learned" (§4.5 heading).
  - Weight averaging is −3.4% vs best specialist (Table 1); against the equal-compute monolithic model it is 11.5% worse in loss (2.486 vs 2.229, my arithmetic).
  - §4.10, Table 12: fusion gain ≈ 0.82 × divergence − 2.72 (R² = 0.856, n = 6); near-zero gain below about 3.3% specialist divergence.
  - §4.4, Table 5: freezing early layers helps only beyond about 10,000 specialist steps.
- **Remedy tags:**
  - [REMEDY | learned router fit after independent training (500 steps) | router misalignment | 410M to 6.9B | fine-tuning | uniform −1.19% vs learned +7.70% relative to best specialist | §4.5]
  - [REMEDY | frozen early layers as a shared anchor | drift between independently trained copies | 410M | fine-tuning | +2.4 pp at 20,000 steps; none below 10,000 | §4.4, Table 5]
- **Bears on:** Q5 (router fit), Q2 (benefit scales with how much specialists diverge; IID data give little divergence, inference), Q1 (one-shot weight averaging cost).
- **How it differs from ours:** fine-tuning, whole-model experts all executed at inference, one-shot, domain-split; single-author study with a six-point regression.
- **Question it raises for us:** can we measure "divergence" between holders of the same expert or between workers in our runs, and does it predict the masked-routing cost?
- **Axes:** worker stores a full model copy (optionally frozen first layers); routing during training: none; averaged: nothing (weight averaging only as a baseline); slice: whole model; sync: one-shot, then central router fit.

### 10. OpenDiPaCo (code status, not a paper)

- https://github.com/MasonFlint44/OpenDiPaCo. GitHub API on 2026-10-11: MIT, created 2026-06-11, last push 2026-06-21, 63 commits (all between 2026-06-11 and 2026-06-21), 0 stars, not archived; no stated affiliation with the DiPaCo authors.
- README (read raw; untrusted, self-reported): implements paths, k-means and discriminative routing, per-module DiLoCo with shard-size weighting and sqrt rescaling, async scheduler and sharded parameter servers; claims a routed path beats a matched dense model on C4 on a 16 GB GPU with margins "+150 → +267 ppl" from 4 to 36 paths; "What's open is paper-scale validation (256 paths × 150M ...)". Margins of hundreds of perplexity points suggest a very small-data regime (inference). Unverified; no change since the earlier survey.

### 11. Leads classified at abstract level (arXiv API abstracts only; no numbers taken from them)

| Lead | arXiv (versions) | What it is | Relevance |
|---|---|---|---|
| BTS: Branch-Train-Stitch (Zhang et al., Meta) | 2502.00075, v1 31 Jan 2025 | frozen domain experts joined to the seed by trained "stitch layers" | follow-up to BTX/BTM; continued pretraining; read later if router-fit alternatives matter |
| Nexus (Gritsch et al., Cohere) | 2408.15901, v1 28 Aug 2024 | upcycling dense experts into an MoE with routing from domain embeddings | router initialization from expert identity; fine-tuning-style |
| HDEE (Ersoy et al., Gensyn) | 2502.19385, v1 26 Feb 2025; code github.com/gensyn-ai/hdee | BTM-style ensembles with experts of different sizes and steps, same compute budget | modular design at small scale; possibly useful for heterogeneous volunteers |
| c-BTM (Gururangan et al.) | 2303.14177, v1 24 Mar 2023 | BTM with unsupervised clustering; abstract says specializing to meaningful clusters "is key" | supports the BTM random-split finding |
| BAR: Train Separately, Merge Together (Morrison et al., AI2) | 2604.18473, v1 20 Apr 2026 | independent post-training of experts, MoE composition with router training, 7B | post-training only |
| EMO (Wang, Bhagia, Min) | 2605.06663, v1 7 May 2026; v2 10 May 2026 | MoE pretraining that restricts each document to a pool of experts so modules emerge | relevant to Q2 (document-level expert pools); not a training-apart method |
| Optimal Splitting (Seto et al., Apple) | 2603.19149, v1 19 Mar 2026 | scaling laws for pretraining then splitting into domain models | cites SMALLTALK; compute allocation, not a cost of training apart |
| BlockTrain (Toth, Oprisa) | 2606.24722, v1 23 Jun 2026; v2 3 Jul 2026 | blocks trained on local objectives; abstract reports CE within about 0.04 of end-to-end on byte-level WikiText | different mechanism (local losses); character/byte-level, so possibly worth a later look |
| SpecDrop (Wang, Lei) | 2608.04084, v1 4 Aug 2026; v2 27 Sep 2026; NeurIPS 2026 per comment | fixed category-conditioned routing; abstract says on fuzzy LM partitions routing reduces to no-routing controls | bears on Q2 (whether specialization matters without label structure) |
| HeterMoE (Wu et al.) | 2504.03871, v1 4 Apr 2025 | systems: disaggregates attention and experts across GPU generations | not relevant to quality cost |
| Hexa-MoE (Luo et al.) | 2411.01288, v1 2 Nov 2024 to v4 2 Apr 2025 | systems: expert-specific operators for heterogeneous devices (Swin-MoE) | not relevant to quality cost |
| Lazarus (Wu et al.) | 2407.04656, v1 5 Jul 2024; v2 24 Oct 2025 | systems: fault-tolerant elastic MoE training with replica placement | not relevant to quality cost; its replica-placement algorithm is a systems analogue of holder assignment |

---

## Synthesis for question 4 (closest methods other than SPES)

**What the papers show.**

1. **The methods that beat a dense model after training parts apart did so with differing data and with more total parameters than that dense model:**
   - The different data came from domain labels (BTM, BTX), clustering (MoE-DisCo, c-BTM), learned sequence routing (SMALLTALK, DiPaCo) or domain splits (KALAVAI).
   - The dense baseline was the size of one expert or path, at equal compute or tokens (BTM Table 1, SMALLTALK App. Table 3, DiPaCo Table 1).
   - Comparisons that hold the model fixed are fewer:
     - BTX vs dense and sparse upcycling, data-matched (Table 2) and GPU-day-matched (Table 3: 47.9 vs 47.3 average score), 7B continued pretraining.
     - FoMoE partial vs full replica at equal tokens (Table 6).
     - DiPaCo with DiLoCo vs the same paths trained synchronously (§4.5).
     - MoE-DisCo vs the same MoE trained jointly, counting fine-tune steps only (Table 1).
2. **With random (IID) splits the evidence is negative or null:**
   - BTM: random-split ensembles are worse than the compute-matched dense model at all four scales, by +3.0% to +5.3% in log-PPL (Table 4, my conversion).
   - MoE-DisCo: random assignment makes its advantage disappear (Fig. 6, no number).
   - KALAVAI: gain shrinks to near zero below about 3.3% specialist divergence (fine-tuning).
   - DEPT: on IID C4 shards, a dense model trained apart performs "similarly" (App. B.3, figure only).
   - (Inference) Our Stage 0 data are IID across workers. Nothing in this strand predicts that experts trained apart on IID shards will specialize, which is consistent with the generalist, interchangeable experts of our Task A. None of these papers measures a masked-routing cost on IID data, so they do not predict its size.
3. **Masked routing with holder-only averaging has one direct precedent here, FoMoE (2026).** Its router is partitioned with the experts, and experts and router rows are averaged within replica groups, as in our sliced arm.
   - At M = 4 with 2 holders per expert and LocalAdamW, partial replication cost +1.6% to +2.9% in log-PPL against full replication over K = 32 to 128 (Table 6, my conversion). Our sliced arm costs about +4.4% against full averaging.
   - FoMoE differs in ways that could each explain part of the difference (inference): synchronized and persistent optimizer state; a sigmoid router chosen so that missing experts do not distort the remaining gate probabilities; embeddings making up about 51M of 54M parameters; 5 to 20 rounds instead of 40; and no centralized number.
   - Its O_e sweep changes the slice and the routing mask together, so it cannot separate our partial-update cost (+1.4%) from our masked-routing cost (+3.2%). The skip-token variant would be needed for that, and it is reported only in a figure.
4. **Central router fitting after independent training is consistently reported as necessary, but only one-shot, at billions of parameters or in fine-tuning:**
   - BTX: router fit plus 80B tokens gives +4.5 points over BTM, and freezing the experts during the fit costs nothing (Table 5).
   - KALAVAI: uniform mixing −1.19% vs a learned router +7.70%, relative to the best specialist.
   - MoE-DisCo: gate learned only in a short fine-tune; its step comparison excludes the submodel phase.
   - No paper fits a router centrally after each round of iterative local training, and none does so at small-scale from-scratch pretraining. Whether it would help at 46M is not known.
5. **Outer optimizer and per-module averaging:**
   - DiPaCo applies Nesterov (0.7, 0.9) per module, with sqrt(path count) norm rescaling and shard-size weights. It reports DiLoCo within ±0.6 PPL of fully synchronous training of the same paths (§4.5), but does not ablate the rescaling.
   - FoMoE: LocalAdamW beats DiLoCo outer at every K tested, and DiLoCo breaks down at K = 128 (Tables 4, 5).
   - DEPT: plain parameter averaging at 500 local steps beats per-step training, but that baseline was matched only in steps and had its learning rate lowered. At its smallest body DEPT is slightly worse than the baseline (Table 13).
   - For our +6.1%, the best like-for-like number in this strand is DiPaCo Table 1: at equal compute and data, DiLoCo with 8 workers (15.02) is +0.8% log-PPL behind a 150M model trained 8× longer (14.72), at τ = 150 with Nesterov, starting from a pretrained model.
6. **Modular or path-based designs** (DiPaCo, SMALLTALK, BTM, c-BTM) avoid training a token-level router on a slice at all:
   - Their wins come with E× parameters, and DiPaCo's 1B-matching result needs re-routing every 64 tokens at test time (Table 3).
   - DiPaCo states it is less FLOP-efficient than a compute-optimal dense model (§6).
   - At equal compute with 8 paths, DiPaCo 2×4 (14.86) was slightly behind a 150M dense model trained 8× longer (14.72), and a flat mixture (14.62) slightly ahead (Table 1).

**Where they disagree.**

- **Does local averaging cost quality?**
  - DEPT and DiPaCo §4.5 find local updates match or beat synchronous training.
  - FoMoE (Table 3), DiPaCo Table 1 (DiLoCo-8 vs 8× baseline) and our Stage 0 find a cost.
  - The baseline definitions differ: equal sequential steps with a lowered baseline learning rate (DEPT), equal steps from a pretrained start (DiPaCo §4.5), equal compute (ours).
- **Is partial replication always worse?** Within FoMoE's Table 6 the direction varies with the outer optimizer, K and M:
  - worse at M = 4 with LocalAdamW;
  - better at M = 8, K = 128 with LocalAdamW (O_e = 4: 138.88 vs full replica 159.71). This setting has K close to our H;
  - better with DiLoCo at M = 4, K = 32 (130.58 vs 137.27).

  (Inference) Partial replication may act as a regularizer when full-replica local averaging degrades, so its cost cannot be read off one configuration.
- **How much routing machinery is needed?**
  - BTX and KALAVAI: routing must be learned.
  - SMALLTALK: router size does not matter, for sequence-level routing.
  - DiPaCo: discriminative re-sharding helps (Table 5).

**What is unknown (not found in this search).**

- No paper in this strand trains at our scale and resolution: about 46M parameters, character-level, from scratch, 4 workers, H = 125, plain averaging, fresh AdamW each round, IID data. FoMoE (54M, BPE, i.i.d.) is the nearest.
- No paper separates the partial-update cost from the masked-routing cost.
- Our exact combination, as a whole, was not found in this search:
  - workers store only the shared part and their experts;
  - routing is masked to held experts with a softmax;
  - experts and router rows are averaged among holders;
  - plain averaging with fresh optimizers;
  - variable slice sizes.

  FoMoE matches the first and third items (with the router partitioned) but uses sigmoid gating, persistent or synchronized optimizer state and uniform slices. The search covered: the seven named papers in full; Semantic Scholar citation lists of BTX, BTM, DiPaCo and SMALLTALK (2025 to 2026 titles filtered by keyword); three web searches; GitHub repository search. It did not cover citers of DEPT, MoE-DisCo or Learning@home, nor SPES or FlexOlmo citers (another strand).

---

## Candidates for the joint reading list

1. **FoMoE (2606.19025)**, specific, but read early: the only paper in this strand with masked (partitioned) routing and holder-only expert averaging, at 54M, with an O_e × K × M table directly comparable to our arms.
2. **DiPaCo (2403.10616)**, foundational (read early): per-module DiLoCo with holder-count rescaling, sequence-level routing, and honest equal-compute rows (Table 1). This is our fallback design.
3. **BTM (2208.03306)**, foundational (read early): random-split ensembles lose to dense at every scale (Table 4), and averaging needs a shared seed phase. The clearest evidence on training apart with IID data.
4. **BTX (2403.07816)**, specific (read later): central router fit after averaging the non-expert parameters, with data-matched and compute-matched baselines, and the ablation showing the fit mainly trains router and attention.
5. **SMALLTALK LM (2410.03529)**, specific (read later): the cleanest equal-FLOP evidence for fully independent experts with sequence-level routing. Shows what the modular fallback buys and that it needs E× parameters.

---

## Gaps (questions no paper answers that our harness could answer)

1. **Holder count × H.** The sliced-minus-full-averaging gap at 46M characters as a function of holders per expert (1, 2, 4 of 4 workers) and H (for example 32, 64, 125, 250), with plain averaging and fresh AdamW. This replicates FoMoE's O_e × K sweep in our optimizer regime. FoMoE only tested LocalAdamW and DiLoCo with persistent state.
2. **Outer momentum per expert.** Nesterov outer momentum applied per expert over its holders: does it shrink the masked-routing share as well as the averaging share? DiPaCo uses per-module Nesterov but reports no ablation.
3. **Skewed data.** Do skewed (non-IID) worker data change the sign of the masked-routing cost? BTM, MoE-DisCo and KALAVAI all say training apart pays off only when data diverge; no one has measured this for masked routing inside a token-level MoE.
4. **Worker count.** N = 2, 4, 8 at a fixed slice fraction. FoMoE reports M effects only for its own optimizer; our plain-averaging regime is untested.
5. **Assignment policy.** Fixed vs rotating with fresh optimizers. FoMoE found random reshuffling no help under i.i.d. data, but it re-initializes optimizer state only for moved experts.
6. **Worker dropout as a regularizer.** Learning@home claims a dropout-like benefit on WikiText-2 from figures only.

Not answerable without new code (listed for completeness): a central router fit after each merge or after the last merge (BTX, MoE-DisCo, KALAVAI); sigmoid instead of softmax gating under masking (FoMoE); persistent or averaged optimizer moments (FoMoE LocalAdamW); sequence-level routing or paths (DiPaCo, SMALLTALK).

---

## Could not verify

- **MoE-DisCo code.**
  - The anonymous link `anonymous.4open.science/r/MoE-DisCo-4835/` returned HTTP 401 `not_connected` (curl, 2026-10-11).
  - The GitHub repositories `tomcheng0618/MoE-DisCo` and `yexin-9220/MoE-DisCo` have no README or licence, and nothing ties them to the authors.
  - Licence unknown.
- **MoE-DisCo initialization** (random or released checkpoints): not stated in the paper.
- **MoE-DisCo PPL/loss mismatch:** which evaluation set its PPL column uses is not stated.
- **Venues of BTX, BTM and DiPaCo:** no venue in the arXiv versions read. OpenAlex lists only arXiv locations. A later venue for BTX may exist; not checked at source.
- **Official code for BTX, SMALLTALK LM, DEPT and FoMoE:** none found (paper text and GitHub repository search). `empty-crayon/branch-train-mix-moe` is a third-party toy.
- **Learning@home code licence:** the GitHub API reports no licence and the repository root has no LICENSE file.
- **FoMoE details:**
  - the meaning of its "±" values (§5 and Table 7 disagree);
  - a numeric centralized reference (Fig. 5 only);
  - its routing-entropy and no-collapse claims (no table or figure found).
- **BTM Fig. 7 end-point perplexities:** annotations extracted from the figure could not be mapped to curves with confidence.
- **OpenDiPaCo:** the README's validation results are self-reported and were not reproduced.
- **DEPT token count vs its STD baseline:** inferred (about |S_t|× tokens for DEPT), not stated by the paper.
- **KALAVAI appendices:** A to S not read, including its evaluation-correction and integrity appendices, which may qualify the main-text numbers.
- **Abstract-only leads:** BTS, Nexus, HDEE, c-BTM, BAR, EMO, Optimal Splitting, BlockTrain and SpecDrop were not opened beyond the arXiv API abstract, so none of their quality costs is verified.

---

## Query log

All times are local (TST) on 2026-10-11, from the `date` command.

| Time | Tool / source | Query or request |
|---|---|---|
| 10:28:47 | local | read brief, prior-work.md, stage0-report §7 |
| 10:29:11 to 10:29:41 | arxiv.org/pdf (curl, 3 s apart) | 2601.06857, 2403.07816, 2208.03306, 2403.10616, 2410.03529, 2410.05021, 2002.04013 |
| 10:29:52 to 10:30:15 | arxiv.org/abs (curl, 3 s apart) | the same seven IDs, for version histories and comments |
| 10:33:40 | GitHub API `repos` | hadasah/btm, mryab/learning-at-home, MasonFlint44/OpenDiPaCo, learning-at-home/hivemind |
| 10:34:30 | GitHub API | OpenDiPaCo README and commits; learning-at-home repository contents |
| 10:34:47 | GitHub API `search/repositories` | "branch-train-mix", "smalltalk language models", "decoupled embeddings pre-training", "MoE-DisCo", "DiPaCo", "branch train mix moe" |
| about 10:35 | GitHub API; curl | tomcheng0618/MoE-DisCo, yexin-9220/MoE-DisCo, empty-crayon/branch-train-mix-moe (metadata and README); searches "asynchronous mixture of language models", "DEPT pretraining federated", "vocabulary-agnostic federated", "SmallTalk LM mixture"; anonymous.4open.science MoE-DisCo link (401) |
| 10:36:52 | OpenAlex `works/doi:` | BTX, BTM, DiPaCo, SMALLTALK, MoE-DisCo (citation counts unusable; arXiv-only locations) |
| 10:37:10 | Semantic Scholar `paper/arXiv:{id}/citations` | BTX, DiPaCo, SMALLTALK, BTM citers (all HTTP 200); filtered to 2025 to 2026 titles by keyword |
| 10:38:07 | export.arxiv.org API | abstracts for triage: 2606.19025, 2603.22755, 2502.00075, 2603.19149, 2604.18473, 2605.06663, 2606.24722, 2608.04084, 2502.19385, 2408.15901, 2609.36770 |
| 10:38:35, 10:38:40 | arxiv.org/pdf | 2606.19025 (FoMoE), 2603.22755 (KALAVAI) |
| 10:39:16 | arxiv.org/html | 2606.19025v2 (for Table 6) |
| 10:40:36 | GitHub API; export.arxiv.org | mechramc/Kalavai (redirect to Murai-Labs/Kalavai); search "FoMoE"; arXiv title search HeterMoE OR Hexa-MoE OR Lazarus |
| about 10:41 | WebSearch (discovery only) | "decentralized pretraining mixture of experts workers hold subset of experts quality gap 2026 arXiv"; "DiPaCo follow-up path-based modular decentralized training language model 2025"; "independently trained expert language models random data split worse than dense equal compute 2025" |
| 10:41:25 | export.arxiv.org | 2602.08019 (an MoE survey; not relevant) |
| 10:45:48 | export.arxiv.org | 2303.14177 (c-BTM metadata) |

**Not covered:**

- citers of DEPT, MoE-DisCo and Learning@home;
- BTS, Nexus, HDEE, c-BTM, BAR, EMO, Optimal Splitting, BlockTrain and SpecDrop beyond the abstract;
- KALAVAI appendices;
- Google Scholar and non-arXiv venues;
- Chinese-language venues;
- GitHub code search inside repositories (the GitHub MCP connector failed; only the unauthenticated REST API was used);
- the anonymous MoE-DisCo repository;
- SPES, FlexOlmo and the federated MoE papers (other researchers).
