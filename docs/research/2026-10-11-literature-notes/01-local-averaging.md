# Q1: the local-averaging cost (+6.1%) · literature notes
> Correction (2026-10-11, coordinator): our experts are SwiGLU with three matrices, so expert parameters are 42.47M of 46.05M (92%), about 14.2M are active per token, and a partial-arm worker trains about 54%. Figures in this file based on two-matrix experts (about 10M active, about 28M expert parameters, about 61% or 70%) are wrong; see the report's header.

Researcher notes for question 1 of `docs/research/2026-10-11-deep-research-prompt.md`, plus remedy evidence on outer optimizers, synchronization frequency, inner-optimizer state, schedules and merge rules. Written 2026-10-11.

How these notes were made. Every number and quotation below was read in raw paper text: PDFs fetched from arxiv.org with `curl` and converted with `pdftotext -layout`, one new directory per paper. For one paper (2509.10439) the arXiv HTML was also fetched, because the PDF table layout was garbled. Text was read with Read, `sed` or `grep`. Search tools were used only to discover papers. Version histories come from the arXiv abs pages, and venues from the arXiv record or OpenAlex. Code licences come from the GitHub REST API.

Caveat on extraction. `pdftotext` scrambles some multi-column tables. Where a value was read from a garbled table, the entry says so and explains how the row mapping was checked. Values readable only in figure images are not recorded; such entries say "figure only".

Our numbers, for reference (from `docs/stage0-report.md` section 3.3):

- Mean test bpc: centralized 1.4376; full-model averaging 1.5254.
- Relative gap +6.1%.
- Absolute gap 0.0878 bits per character = 0.0609 nats per character (×ln 2).
- Setup: M = 4 workers, H = 125, R = 40 rounds; plain averaging (outer SGD, learning rate 1, no momentum); fresh AdamW every round (β = 0.9, 0.95; no weight decay; clip 1.0).
- Schedule: warm-up 100 steps (round 0 only), constant 1e-3, then linear decay to 1e-4 over the last 20%.
- Each worker runs 5,000 steps at batch 32×256 characters. The centralized run is 20,000 steps at batch 32.
- Task B MoE model: 46.05M total parameters, about 10M active; character-level text8, IID shards; 163.8M training characters.

## Papers

Blocks are grouped into four groups:

- A. DiLoCo family, the core quantitative evidence.
- B. Remedies, meaning outer optimizers, merge rules and optimizer state.
- C. Theory and classic local SGD.
- D. Critical batch size, plus minor or low-relevance items.

Cost names used throughout: "averaging cost" = +6.1% (Q1); "partial-update cost" = +1.4%; "masked-routing cost" = +3.2%.

### A1. DiLoCo: Distributed Low-Communication Training of Language Models

- **Authors:** Douillard, Feng, Rusu, Chhaparia, Donchev, Kuncoro, Ranzato, Szlam, Shen (Google DeepMind). 2023. Preprint; no venue stated on the arXiv record or found in OpenAlex.
- **arXiv:** 2311.08105. Versions: v1 14 Nov 2023, v2 2 Dec 2023, v3 23 Sep 2024. **Read v3.** https://arxiv.org/abs/2311.08105 (DOI 10.48550/arXiv.2311.08105).
- **Code:** none found in the paper.
- **Read status:** full text (main body and appendix; figures not readable).
- **Setting:**
  - Chinchilla-style transformers of 60M, 150M and 400M on C4; sequence length 1,024; batch 512.
  - 88,000 total steps. By default DiLoCo starts from a model pretrained for 24,000 steps, then runs 8 workers with H = 500 (64,000 steps).
  - Non-IID shards by default (k-means clustering); IID also tested.
  - Inner AdamW (lr 4e-4, 1,000 warm-up steps, weight decay 0.1); outer Nesterov with lr 0.7 and momentum 0.9 (Table 5, §3.1).
- **Key findings:**
  - **Table 2 (150M, 8 workers, H = 500, non-IID), perplexity:**

    | Arm | Perplexity |
    |---|---|
    | single-worker baseline (1× compute) | 16.23 |
    | DP with 8× batch | 15.30 |
    | 8× batch by microbatching | 15.30 |
    | 8× updates (8× more sequential steps at the same batch) | 14.72 |
    | DiLoCo | 15.02 |

    The text says the 8×-updates baseline "improves perplexity over our method, but at the cost of being 8× slower" (§3).
    - (inference) In loss terms, DiLoCo is +0.75% vs 8× updates and −0.68% vs 8× batch DP. 8× batch DP is itself +1.44% vs 8× updates.
  - **Limitations (§5):** the distributed computation "reduces the FLOP and data efficiency of the model", because outer updates "have effectively too large a batch size".
  - **H (Fig. 4, 150M, non-IID, H from 50 to 2000):** more frequent communication helps, with diminishing returns below H = 500. At H = 1000, perplexity rises "by only 2.9% relative to H = 50" (§3.1). Curves are figure only.
  - **Replicas (Table 3), fixed inner steps per replica, so more replicas means more compute.** Perplexity IID / non-IID:

    | Replicas | IID | non-IID |
    |---|---|---|
    | 1 | 16.23 | 16.23 |
    | 4 | 15.23 | 15.18 |
    | 8 | 15.08 | 15.02 |
    | 16 | 15.02 | 14.91 |
    | 64 | 14.95 | 14.96 |

    Diminishing returns beyond 8 workers.
  - **Model size (Table 4):** improvement of DiLoCo (8 workers) over a single worker is 4.33% at 60M, 7.45% at 150M and 7.49% at 400M. The reference is a single worker, not an equal-compute centralized run.
  - **Outer optimizer (Fig. 6, figure only):** outer SGD (= FedAvg) and outer Adam "performed poorly"; Nesterov lr 0.7, momentum 0.9 "is very robust" (§3.1).
  - **Outer lr schedule:** a cosine decay of the outer lr "resulted in similar performance"; inner-lr decay already shrinks the outer-gradient norm (§3.1).
  - **From scratch (Fig. 3):** starting DiLoCo from random initialization gives "minimal (-0.1 PPL) degradation".
  - **Inner optimizer state (Supplementary §6.1):** each replica keeps its own Adam state. Synchronizing inner optimizer states "did not lead to significant improvements" while tripling communication.
  - **Pseudo-gradient statistics (§6.2):** IID outer gradients are highly correlated. In the non-IID setting, the averaged outer gradient's norm is "inversely proportional to the square root of the number of replicas".
- **Tags:**
  - [REMEDY | Nesterov outer optimizer (lr 0.7, μ 0.9) instead of outer SGD = FedAvg | averaging cost | 150M | pretraining (from a 24k-step checkpoint) | FedAvg "performed poorly"; no numbers in text | Fig. 6, §3.1, v3]
  - [REMEDY | sync inner Adam states | averaging cost | 150M | pretraining | "did not lead to significant improvements" | Supp. §6.1, v3]
  - [REMEDY | lower H (more frequent sync) | averaging cost | 150M | pretraining | H 1000 vs 50: +2.9% perplexity | Fig. 4, §3.1, v3]
- **Bears on:** Q1 (averaging cost); Q5 (remedies).
- **Differences from ours:**
  - BPE tokens on C4; dense model, 3.3× to 40× larger.
  - Starts from a pretrained checkpoint by default.
  - Keeps Adam state; uses Nesterov outer optimizer; 8 workers; H = 500; non-IID shards.
- **Question for us:** Table 2's "8× updates" row is the published analogue of our centralized arm. How much of our +6.1% would remain against a DP run at batch 128 (the analogue of "8× batch")?

### A2. Communication-Efficient Language Model Training Scales Reliably and Robustly: Scaling Laws for DiLoCo

- **Authors:** Charles, Teston, Dery, Rush, Fallen, Garrett, Szlam, Douillard (Google). 2025.
- **Venue:** NeurIPS 2025, per OpenAlex (DOI 10.52202/085713-3559); the arXiv record gives none.
- **arXiv:** 2503.09799. Versions: v1 12 Mar 2025 only. **Read v1.** https://arxiv.org/abs/2503.09799
- **Code:** none found.
- **Read status:** sections read: abstract, §1 to §4 (all four findings, Tables 3 to 5, Fig. 7), §5.1 (synchronization cadence), §5.2, §6.1 to §6.4 (Tables 7 to 12).
- **Setting:**
  - From scratch on C4 at Chinchilla tokens (D = 20N); 9 model sizes from 35M to 2.4B, plus 4B and 10B with predicted hyperparameters.
  - AdamW inner (β 0.9, 0.99; 1,000 warm-up steps; cosine decay to 5%); Nesterov outer (μ 0.9, constant outer lr swept over {0.2, …, 1.0}); H = 30 by default; M ∈ {1, 2, 4, 8}.
  - "replicas maintain their inner optimizer state across rounds" (§2.1).
  - Baseline is data-parallel at the same N and token budget D. DiLoCo's global batch B is split B/M per replica. Batch size and lr are tuned separately for each algorithm (§2.2, §3.1).
- **Key findings:**
  - **Table 4, eval loss and % vs DP at H = 30:**

    | N | M = 1 | M = 2 | M = 4 | M = 8 |
    |---|---|---|---|---|
    | 35M (DP 3.485) | 3.482 (−0.1%) | 3.508 (+0.7%) | 3.554 (+2.0%) | 3.621 (+3.9%) |
    | 90M | −0.1% | +0.5% | +1.5% | +3.1% |
    | 2.4B | −0.4% | −0.1% | +0.3% | +1.1% |

    The text says "DiLoCo with M = 4 goes from attaining 2% higher evaluation loss for N = 35M parameters to only a 0.26% higher evaluation loss at N = 2.4B". The table shows +0.3%.
  - **Finding 2:** DiLoCo with M = 1 beats DP at every size. This is an outer-optimizer (Lookahead-like) effect, not a distribution effect.
  - **Finding 3:** DiLoCo increases the optimal batch size, and the optimal global batch grows with M. DP "degrades quickly as batch size increases".
  - **Finding 4 and §5.1:** the best outer lr is roughly independent of N and grows with M and H.
    - Fig. 7 (read from the figure's text layer; treat with care): best outer lr at 35M is 0.6 for M = 4 and 1.0 for M = 8.
    - Fig. 8: "The optimal outer learning rate increases with H."
  - **§5.1, Fig. 9 (figure only):** H ∈ {1, 5, 10, 30, 100, 300}. H = 1 is worst. Otherwise "evaluation loss increases as H increases". The increase is "less pronounced for M = 1 and larger models".
- **Tags:**
  - [REMEDY | Nesterov outer with tuned outer lr, keep Adam state, H = 30 | averaging cost | 35M to 2.4B | pretraining | M = 4 gap vs same-global-batch DP: +2.0% (35M) down to +0.3% (2.4B) | Table 4, v1]
  - [REMEDY | lower H | averaging cost | 35M to 550M | pretraining | loss rises with H beyond H = 1; less so for larger N | Fig. 9, §5.1, v1]
- **Bears on:** Q1 (size, M, H, outer lr dependence); Q6 (whether a small-scale gap is normal).
- **Differences from ours:**
  - DP baseline at the same global batch and steps, so there is no "more sequential steps" handicap.
  - Nesterov outer, kept Adam state, H = 30, BPE C4, dense model.
- **Question for us:** Is our +6.1% consistent with the 35M M = 4 point (+2.0%) once the extra handicaps are accounted for: H = 125, plain averaging, Adam reset, a more-steps baseline?

### A3. Streaming DiLoCo with overlapping communication: Towards a Distributed Free Lunch

- **Authors:** Douillard, Donchev, Rush, Kale, Charles, Garrett, Teston, Lacey et al. (14). 2025. Preprint per the arXiv record. A conference venue appears only in another paper's citation, which was not verified.
- **arXiv:** 2501.18512. Versions: v1 30 Jan 2025 only. **Read v1.** https://arxiv.org/abs/2501.18512
- **Read status:** sections read: §3.1 (simulation, partial), §3.2 (scaling setup), Supplementary (Tables 2, 5, 6, 7; inner-steps and replicas paragraphs).
- **Setting:**
  - Chinchilla architecture with QKNorm and z-loss; C4; Chinchilla tokens; 35M to 4B; from scratch.
  - Outer lr 0.4, tuned at small scale and kept fixed; 2 replicas in main runs.
  - Table 6 varies M ∈ {2, 4} and H ∈ {30, 100}, using the full method (Streaming DiLoCo with overlapped FP4 communication).
- **Key findings:**
  - **Table 5 (M = 2), eval loss at 35M:** DP 3.51; DiLoCo H = 30 3.54; Streaming H = 30 3.53; Streaming H = 100 3.56. At 1B: DP 2.49, DiLoCo 2.49.
  - **Table 6 (35M, full method):** M = 2 / H = 30: 3.53; M = 4 / H = 30: 3.60; M = 2 / H = 100: 3.56; M = 4 / H = 100: 3.64.
    - (inference) vs DP 3.51: +0.6%, +2.6%, +1.4%, +3.7%.
    - At 1B, M = 4 / H = 100 gives 2.53 vs DP 2.49.
    - The table layout is garbled, but each row has an explicit "M H" prefix.
  - **Table 7 (1B, Dolma) caption:** "With twice more replicas, the global batch size is doubled, and twice less steps are done … slightly worse performance". M = 4 eval loss: 2.73 / 2.54 / 2.47 at 25B / 100B / 250B tokens, vs DP 2.67 / 2.52 / 2.45.
  - **Number of inner steps (Supplement):** "a too small H produce noisy small-normed outer gradients and a too high H will see replicas drifting apart".
  - **Cosine similarity:** outer gradients between replicas start slightly correlated (≈ 0.1), become nearly orthogonal, and end slightly anti-correlated (≈ −0.1). Larger models show lower similarity.
- **Tags:** [REMEDY | lower H (30 vs 100) | averaging cost | 35M | pretraining | M = 4: loss 3.60 vs 3.64 (DP 3.51) | Table 6, v1]
- **Bears on:** Q1 (smallest-scale M = 4 numbers with H ≈ 100).
- **Differences from ours:**
  - Fragment-wise streaming sync with FP4 quantization; Nesterov outer; BPE.
  - Table 6's batch convention (global batch fixed or growing with M) is not stated in the text read. Table 7's caption implies the global batch grows with M.
- **Question for us:** Does our gap scale with H the way 35M M = 4 does (+2.6% at H = 30 → +3.7% at H = 100)?

### A4. OpenDiLoCo: An Open-Source Framework for Globally Distributed Low-Communication Training

- **Authors:** Jaghouar, Ong, Hagemann (Prime Intellect). 2024. Preprint.
- **arXiv:** 2407.07852. Versions: v1 10 Jul 2024 only. **Read v1.** https://arxiv.org/abs/2407.07852
- **Code:** https://github.com/PrimeIntellect-ai/OpenDiloco, Apache-2.0, pushed 2026-07-17 (GitHub API).
- **Read status:** full text of the main body (§1 to §4); appendix not read.
- **Setting:**
  - 150M Llama replication of DiLoCo from scratch: C4, 88,000 steps, batch 512, sequence length 1,024, inner lr 4e-4, Nesterov 0.7/0.9.
  - 1.1B TinyLlama configuration: batch 2,048, 44,000 steps, 4 workers, outer lr 0.7.
- **Key findings:**
  - **Table 1 (150M):** DP with 8× batch 13.68; DiLoCo with 8 replicas, H = 500: 13.73; single worker 16.17.
  - **Table 2 (1.1B), perplexity:**

    | Arm | Perplexity |
    |---|---|
    | DP with 4× batch | 10.52 |
    | DiLoCo, 4 workers, H = 125 | 10.76 |
    | DiLoCo, 4 workers, H = 500 | 11.14 |
    | single worker | 11.85 |

    (inference) Loss gaps: +0.96% at H = 125 and +2.43% at H = 500.
  - **Figs. 4 to 5 (H = 50):** "DiLoCo with more than one worker is initially not as compute efficient as the same number of global steps on a single machine or when using Distributed Data Parallel training."
  - **Practical usage:** training for only 44,000 steps with 8 workers "results in a significantly worse performing model than DDP".
- **Tags:** [REMEDY | H 125 vs 500 | averaging cost | 1.1B | pretraining | perplexity 10.76 vs 11.14 (DP 10.52) | Table 2, v1]
- **Bears on:** Q1. M = 4 and H = 125 match ours exactly, at 24× the parameters.
- **Differences from ours:** Nesterov outer; Adam state presumably kept (follows DiLoCo; not stated in the text read); the DP baseline uses 4× batch at the same steps; BPE; dense.
- **Question for us:** Their 4-worker, H = 125 gap is under 1% in loss at 1.1B. How much of our gap is scale and how much is our choices?

### A5. INTELLECT-1 Technical Report

- **Authors:** Jaghouar, Ong, Basra, Obeid, Straube, Keiblinger, Bakouch, Atkins et al. (12). 2024. Preprint.
- **arXiv:** 2412.01152. Versions: v1 2 Dec 2024 only. **Read v1.** https://arxiv.org/abs/2412.01152
- **Code:** framework https://github.com/PrimeIntellect-ai/prime, MIT, pushed 2026-10-11.
- **Read status:** sections read: abstract, §2 (DiLoCo description), §3.1, §3.4, Appendix A hyperparameter table (garbled layout; label-to-value mapping done by order).
- **Setting:**
  - 10B Llama-3-style model; 1T tokens; up to 14 nodes.
  - H = 100 inner steps; int8 pseudo-gradients.
  - WSD inner lr schedule (7.5e-5) with a cool-down in the final 20%.
  - Outer Nesterov lr 0.7, momentum 0.9 (Appendix A table, garbled; mapped by order of labels).
- **Key findings:** no controlled centralized baseline. The model is compared with other open models trained centrally on similar token counts (§3.6). The schedule shape (WSD with a final-20% decay) resembles ours.
- **Bears on:** Q1 (schedule precedent only).
- **Differences from ours:** scale; there is no equal-compute baseline, so the paper gives no gap measurement.
- **Question for us:** none beyond showing that a WSD-shaped inner schedule has been used with DiLoCo at scale.

### A6. Photon: Federated LLM Pre-Training

- **Authors:** Sani, Iacob, Cao, Lee, Marino, Gao, Cai, Li et al. (11). 2024.
- **Venue:** MLSys 2025 (arXiv journal reference "Proceedings of Machine Learning and Systems 7 (MLSys 2025)").
- **arXiv:** 2411.02908. Versions: v1 5 Nov 2024, v2 14 Jun 2026 (v2 adds MFU corrections, Appendix F). **Read v2.** https://arxiv.org/abs/2411.02908
- **Read status:** sections read: abstract, §3 (incl. "Exploiting Small Batches and High Learning Rates"), §5.1 to §5.3, Tables 2 to 4, Appendix A Table 6, Appendix B.1 (stateless clients), C.1, C.2.
- **Setting:**
  - MPT decoder models of 125M to 7B; C4 split IID into 64 shards (and The Pile for heterogeneity).
  - AdamW clients with cosine lr; 62/128/512 local steps.
  - Default server optimizer "FedAvg with server learning rate 1.0 and server momentum 0.0" (Appendix B.1), i.e. plain averaging.
  - For billion-scale runs: "we employ a stateless local optimization procedure, and resetting optimizer states each round" (Appendix B.1).
  - 125M setting: N = 4 clients, local batch 32, global batch 128. This is structurally the closest published configuration to ours.
- **Key findings:**
  - **Table 2:** federated perplexity beats centralized: 1.3B 20.1 vs 23.2; 3B 15.7 vs 18.2; 7B 13.8 vs 16.6. "perplexity gains grow with model size" (§5.2).
  - **§5.3 and Fig. 6:** at 125M with N = 4 and global batch 128, DiLoCo's Nesterov outer lr was tuned over {0.1, 0.3, 0.5, 0.7}. Higher values "hindered achieving the desired perplexity due to early divergent activations", so 0.1 was chosen.
  - **Table 4:** Photon reaches target perplexity in about 0.5× DiLoCo's wall time.
  - **Appendix C.1:** the averaging step "will limit the impact of any individual update". Client updates are "near-orthogonal". A cosine lr period scaled to the client batch is proposed.
  - **Baseline-definition caveat:**
    - Table 6 lists, for 1.3B and 3B, a centralized batch equal to the client batch (512) and the same schedule length T.
    - Table 3 shows federated compute time 1.6× to 2.8× the centralized compute time.
    - The caption defines "same computational resources" as equal numbers of clients and DP workers.
    - (inference) Photon's "better than centralized" result is therefore not an equal-compute comparison in our D17 sense. I could not resolve exactly how many tokens each centralized run saw.
- **Tags:** [REMEDY | plain averaging (server lr 1, μ 0) with small client batch and high lr | averaging cost | 125M to 7B | pretraining | "2× faster" than DiLoCo (s = 0.1) at 125M; lower perplexity than "centralized" at ≥ 1.3B (baseline not equal-compute) | Tables 2, 4, Fig. 6, v2]
- **Bears on:** Q1 (plain averaging and optimizer reset at scale); a disagreement with DiLoCo Fig. 6.
- **Differences from ours:** model size; baseline definition; outer lr for DiLoCo constrained by divergence; IID C4.
- **Question for us:** Photon resets optimizer state and uses plain averaging, yet reports good results. Is the reset harmless at their larger scale, or are its costs hidden by the baseline choice?

### A7. The Future of Large Language Model Pre-training is Federated

- **Authors:** Sani, Iacob, Cao, Marino, Gao, Paulik, Zhao, Shen et al. (11). 2024. Preprint.
- **arXiv:** 2405.10853. Versions: v1 17 May 2024, v2 19 Jul 2024, v3 14 Oct 2024. **Read v3.** https://arxiv.org/abs/2405.10853
- **Read status:** sections read: §6.5, §7.1 (partial), Table 3, Fig. 3 caption.
- **Setting:** IID C4; 500 local steps; AdamW clients; FedMom server (lr 0.1 to 0.7, μ 0.9); models 75M to 7B.
- **Key findings:** the centralized model "outperforms the 75M federated model while performing near-identically for the 1.3B models" (Fig. 3 caption). Aggregation causes early client-perplexity spikes that subside faster for larger models. Figure only; no numbers in the text.
- **Bears on:** Q1 (model-size dependence of the gap at small scale).
- **Differences from ours:** outer momentum; BPE; dense.
- **Question for us:** Does our 46M model sit in the regime where federated training "loses" (like their 75M)?

### A8. Decoupled DiLoCo for Resilient Distributed Pre-training

- **Authors:** Douillard, Rush, Donchev, Charles, Fallen, Dubey, Gog, Dean et al. (17). 2026. Preprint.
- **arXiv:** 2604.21428. Versions: v1 23 Apr 2026 only. **Read v1.** https://arxiv.org/abs/2604.21428
- **Read status:** sections read: abstract, §1, §2 to §3.2, §5.1, §5.4 to §6, Appendix D.2 (radial-directional averaging), Table 14.
- **Setting:**
  - Asynchronous learners with a central synchronizer.
  - 24 fragments, each synchronized every H = 24 steps.
  - Dense Gemma models of 2B to 9B; MoE with 2.8B/3.8B active parameters on 170B/233B tokens.
- **Key findings:**
  - Restates DiLoCo: Nesterov outer "greatly improves model quality compared to weight averaging (which corresponds to an outer optimizer of SGD with learning rate 1)" (§2; a citation of DiLoCo, not a new measurement).
  - Per-learner outer gradients are "almost pairwise orthogonal". Their average therefore has norm about 1/√M, so "we generally need to re-tune the outer optimizer when we merge via averaging" (Appendix D.2).
  - Radial-Directional Averaging (RDA) averages norms and directions separately. TIES, Iso-C and sparsity-aware merges were tried, but "direct averaging and RDA outperformed such methods in our setting".
  - **MoE:** learners "can only optimize [the load-balancing] loss locally", yet "with sufficient scale" performance is comparable to DP (§5.5). Downstream accuracies only; no loss gap numbers.
- **Tags:** [REMEDY | RDA merge instead of averaging | averaging cost | 2B to 9B dense, 2.8B-active MoE | pretraining | "greater hyperparameter stability" and better scaling in learners; no small-scale numbers | §5.1, App. D.2, v1]
- **Bears on:** Q1 (the only MoE + local-averaging evidence found, at 2.8B active and H = 24).
- **Differences from ours:** asynchronous; fragmented sync; far larger.
- **Question for us:** Does local-only load balancing interact with averaging at our 10M-active scale?

### A9. Factored Gossip DiLoCo: Reducing Blocking Communication in DiLoCo

- **Authors:** Hewa Koneputugodage, Ajanthan, Ramasinghe, Dolatabadi, Siriwardhana, Avraham, Shevchenko, Pajak et al. (10). 2026.
- **Venue:** "Accepted at ICML 2026" (arXiv comment; not checked further).
- **arXiv:** 2606.22768. Versions: v1 22 Jun 2026 only. **Read v1.** https://arxiv.org/abs/2606.22768
- **Read status:** sections read: §4.1 setup, §5 main results text, §6 (scaling and H paragraphs), Appendix inner/outer optimizers. Table 1 layout is garbled; DiLoCo numbers are taken from the text.
- **Setting:** 1.5B Llama 3 on FineWeb; 10B tokens (and 30B); 8 workers; global batch 512 × 1,024 tokens (64 per worker); AdamW 3e-4 with linear decay to zero; outer Nesterov 0.7/0.9 "matching DiLoCo's recipe", not retuned per H.
- **Key findings:**
  - Sync-DP perplexity 17.53 at 10B tokens.
  - DiLoCo perplexity at 10B tokens: H = 100 18.65; H = 500 22.67; H = 1k 28.17 (§5, §6).
  - (inference) About 19k steps, so R ≈ 190 / 38 / 19 rounds. Loss gaps +2.2% / +9.0% / +16.6%.
  - Scaling (Fig. 5, figure only): H = 1k "has only a small effect at 160M, but is noticeably worse at 600M (and at 1.5B), indicating reduced tolerance to long local intervals as scale increases". On 160M WikiText, sync-DP "is not always best".
- **Tags:** [REMEDY | lower H | averaging cost | 1.5B | pretraining | perplexity 28.17 → 22.67 → 18.65 for H 1k → 500 → 100 (DP 17.53) | §5 to §6, v1]
- **Bears on:** Q1. It disagrees with A2 on how H tolerance changes with model size. Outer lr was not retuned here, while A2 shows the optimal outer lr rises with H.
- **Differences from ours:** Nesterov at a fixed outer lr; BPE; large model; few rounds at large H.
- **Question for us:** Is our R = 40 rounds a bigger driver than H itself?

### B1. Understanding Outer Optimizers in Local SGD: Learning Rates, Momentum, and Acceleration

- **Authors:** Khaled, Kale, Douillard, Jin, Fergus, Zaheer. 2025.
- **Venue:** NeurIPS 2025 per OpenAlex (DOI 10.52202/085713-3354). The arXiv record lists none.
- **arXiv:** 2509.10439. Versions: v1 12 Sep 2025, v2 11 Dec 2025. **Read v2** (PDF, plus arXiv HTML v2 to confirm Tables 3 to 5). https://arxiv.org/abs/2509.10439
- **Read status:** sections read: abstract, §1 (contributions), §4.2 (transformer pretraining), Appendix A.1.1 to A.1.6, Tables 1 to 5. The theory sections (§2 to §3 and the appendix proofs) were not read beyond the contribution statements.
- **Setting:**
  - Chinchilla decoder (DiLoCo architectures) of 150M/400M/1B on C4, from scratch.
  - Batch 512 per replica × 1,024 tokens; cosine inner lr.
  - "The inner optimizer state is never shared across replicas, and is passed from one round to the other" (§4.2).
  - Outer optimizers: "SGD(lr=1) (equivalent to simple averaging of local models)", Nesterov, and Schedule-Free SGD.
  - Baselines: DP at the per-replica batch (1/M of the compute) and "DP 4x BS" at the same steps with 4× batch (equal FLOPs).
  - The 150M model trains for about 24,000 steps (Appendix A.1.6 example; PDF text).
- **Key findings, Table 3 (150M, M = 4), perplexity:**

  | Arm | Perplexity |
  |---|---|
  | DP, 1× batch | 18.07 |
  | DP, 4× batch | 16.89 |

  | H | SGD lr 1.0 (plain averaging) | Nesterov lr 0.7 | Nesterov lr 1.0 | SF-SGD lr 2.0 |
  |---|---|---|---|---|
  | 50 | 17.75 | 17.25 | 16.38 | 16.88 |
  | 150 | 17.58 | 17.90 | 16.79 | 16.96 |
  | 250 | 18.20 | 18.09 | 17.12 | 16.97 |
  | 500 | 18.44 | 17.95 | 18.15 | 17.18 |
  | 1000 | 18.18 | 18.16 | 18.75 | 17.29 |
  | 2000 | 18.11 | 18.40 | 18.36 | 17.59 |

  - (inference) Plain-averaging loss gap vs DP 4× batch is +1.8% (H = 50), +1.4% (150), +2.6% (250), +3.1% (500), +2.6% (1000), +2.5% (2000). At H ≥ 250, plain averaging with 4 workers is no better than one DP worker at a quarter of the compute (18.07).
  - **Varying M at H = 50, per-replica batch fixed (so compute grows with M):**

    | M | SGD lr 1.0 | Nesterov lr 1.0 |
    |---|---|---|
    | 2 | 18.64 | 16.81 |
    | 4 | 17.75 | 16.38 |
    | 8 | 18.38 | 16.27 |
    | 16 | 19.86 | 16.25 |

    Only the M = 4 rows are comparable to the 4× batch DP baseline.
  - **Table 4 (H = 50, M = 4, outer lr sweeps; single runs):**
    - Nesterov with cosine outer schedule: 0.3 → 17.16, 0.5 → 17.06, 0.7 → 16.93, 0.9 → 17.19, 1.1 → 17.56.
    - SGD: 0.3 fixed 21.04; 0.3 cosine 17.68; 0.5 cosine 16.63; 0.7 cosine 18.84; 1.0 cosine 19.21. These are non-monotone, as printed.
  - **A.1.2:** "averaging … is relatively constant w.r.t the synchronization frequency: its performance stay stable from H = 250 to H = 2000". Nesterov with high outer lr is "particularly unstable", degrading 10.7%, so "the learning rate should be tuned alongside the synchronization frequency".
  - **A.1.3 and Fig. 4:** "their flops-efficiency disappear as the number of replicas increases". Increasing DP batch or steps "still rapidly improves perplexity". Cosine similarity of outer gradients falls from 30% (M = 2) to 10% (M = 16) even with IID data.
  - **A.1.5:** constant outer lr is the best schedule. Outer warm-up was "always found to be harmful". Increasing H as the inner lr decreases (QSR, C3) is suggested but not tested.
  - **Theory (abstract and §1):**
    - The outer lr trades optimization error against noise variance and can compensate for an ill-tuned inner lr, "even in the absence of any stochastic gradient noise".
    - It "should sometimes be set to values greater than 1".
    - Nesterov outer acceleration improves the dependence on rounds R.
- **Tags:**
  - [REMEDY | Nesterov outer (lr 1.0) vs plain averaging | averaging cost | 150M | pretraining | perplexity 16.38 vs 17.75 at H = 50 (≈ 2.9% in loss); advantage shrinks or reverses by H = 500 to 2000 at fixed outer lr | Table 3, v2]
  - [REMEDY | Schedule-Free SGD outer (lr 2.0) | averaging cost | 150M | pretraining | 17.18 vs 18.44 at H = 500 | Table 3, v2]
  - [REMEDY | outer lr schedule (constant vs cosine vs plateau+linear) | averaging cost | 150M | pretraining | constant best; figure only | A.1.5, Fig. 7, v2]
- **Bears on:** Q1. This is the most direct published measurement of plain averaging (outer SGD lr 1) at M = 4 with H in our range.
- **Differences from ours:**
  - Adam state kept, not reset; cosine schedule; 150M dense BPE model.
  - Baseline is 4× batch DP at the same steps, not 4× steps.
  - About 24k steps per replica (480 to 12 rounds); our setup has 40 rounds.
- **Question for us:** Their plain averaging at H = 500 (48 rounds) is +3.1% in loss with Adam state kept and a same-step baseline. How much of our extra 3 points comes from the Adam reset, the more-steps baseline, and scale?

### B2. Can Model Merging Improve Aggregation in DiLoCo?

- **Authors:** Horoi, Thérien, Wolf, Belilovsky (Mila, Montréal, Concordia). 2026. Preprint.
- **arXiv:** 2607.03011. Versions: v1 3 Jul 2026 only. **Read v1.** https://arxiv.org/abs/2607.03011
- **Code:** https://github.com/shoroi/isoloco, MIT, created and pushed 2026-06-16.
- **Read status:** full text of the main body (§1 to §4.4) and Appendix A (hyperparameter tables; Table 6 layout garbled).
- **Setting:**
  - Llama-style 178M, 512M and 1B on DCLM; Chinchilla tokens; sequence length 2,048.
  - Global batch 524k tokens (178M), matched across R ("inner batch size for each worker is set to global batch size divided by R").
  - AdamW β 0.9, 0.95, weight decay 0.1; warm-up 10% of steps; H = 30, R = 8 by default.
  - DiLoCo "retains inner optimizer states across outer rounds rather than resetting them" (§2.1).
  - AdamW DP baseline swept over lr and weight decay.
- **Key findings:**
  - **Table 1 (178M, R = 8, H = 30, outer SGD):**

    | Method | Validation loss |
    |---|---|
    | AdamW DP | 2.881 |
    | DiLoCo SGD | 2.990 |
    | TIES | 2.997 |
    | DARE | 2.993 |
    | TSV-M | 3.160 |
    | Iso-C | 2.929 |
    | Iso-CTS | 2.986 |

  - **Table 2 (178M, H = 30), validation loss by number of workers R:**

    | R | DiLoCo SGD | DiLoCo (Nesterov) | SGD + Iso-C | IsoLoCo |
    |---|---|---|---|---|
    | 1 | 2.887 | 2.869 | 2.855 | 2.842 |
    | 2 | 2.905 | 2.882 | 2.872 | 2.852 |
    | 4 | 2.937 | 2.911 | 2.891 | 2.864 |
    | 8 | 2.990 | 2.950 | 2.929 | 2.889 |
    | 16 | 3.064 | 3.005 | 2.992 | 2.930 |
    | 32 | 3.178 | 3.077 | 3.070 | 2.992 |
    | 64 | 3.357 | 3.195 | 3.162 | 3.062 |
    | 128 | 3.601 | 3.355 | 3.280 | 3.160 |

    - (inference) At R = 4: +1.9% (SGD), +1.0% (Nesterov), +0.3% (SGD + Iso-C), −0.6% (IsoLoCo) vs DP 2.881.
    - At 512M, DiLoCo vs IsoLoCo, R = 1…64: 2.630/2.589 … 2.863/2.716.
  - **Table 4 (178M, R = 8), varying H:**

    | H | DiLoCo | IsoLoCo |
    |---|---|---|
    | 30 | 2.950 | 2.889 |
    | 60 | 2.957 | 2.907 |
    | 120 | 2.976 | 2.944 |
    | 240 | 3.008 | 2.991 |

    Both methods were "extensively tuned in each case". (inference) DiLoCo goes from +2.4% to +4.4% vs DP.
  - **Table 3 (1B, R = 8):** DiLoCo 2.450; IsoLoCo 2.421.
  - **Appendix A:** tuned outer SGD lr for "DiLoCo SGD" is 1.6 at R = 8, H = 30 (Table 5, clean). Table 6 (garbled; first row read as DiLoCo SGD) gives 1.2/1.4/1.4/1.6 for R = 1/2/4/8. This means the best plain-SGD outer step is larger than averaging (lr 1).
  - **§2.1:** increasing H "leads to worse performance, as local replicas diverge further before aggregation".
- **Tags:**
  - [REMEDY | Iso-C aggregation (flatten singular values of the averaged pseudo-gradient) replacing averaging | averaging cost | 178M | pretraining | 2.929 vs 2.990 (outer SGD, R = 8, H = 30) | Table 1, v1]
  - [REMEDY | IsoLoCo (Iso-C + Nesterov) | averaging cost | 178M to 1B | pretraining | R = 4, H = 30: 2.864 vs DiLoCo 2.911 vs DP 2.881; persists to H = 240 | Tables 2 to 4, v1]
  - [REMEDY | outer SGD lr > 1 | averaging cost | 178M | pretraining | tuned optimum 1.6 at R = 8 (loss values for lr = 1 not reported) | Table 5, v1]
- **Bears on:** Q1 and Q5. It gives the cleanest small-scale M = 4 numbers separating outer SGD, Nesterov and merge-based aggregation.
- **Differences from ours:** same-global-batch DP baseline; kept Adam state; H = 30; tuned outer lr; dense BPE.
- **Question for us:** Would an Iso-C or Newton-Schulz aggregation step close part of our gap at H = 125? It is cheap to try.

### B3. MuLoCo: Muon is a practical inner optimizer for DiLoCo

- **Authors:** Thérien, Huang, Defazio, Rish, Belilovsky. 2025. Preprint.
- **arXiv:** 2505.23725. Versions: v1 29 May 2025, v2 25 Feb 2026, v3 2 Jun 2026. **Read v3.** https://arxiv.org/abs/2505.23725
- **Code:** https://github.com/facebookresearch/MuLoCo. The GitHub API reports no licence; created 2026-02-05, pushed 2026-04-13.
- **Read status:** sections read: abstract, §1 (partial), §5 setup, §6.1 to §6.2.
- **Setting:** 416M base task (Gemma3-style), plus a 150M to 3.1B scaling study and 15B; AdamW β2 0.99; H = 30 default; Nesterov outer; DP baselines tuned.
- **Key findings:**
  - Fig. 6a (figure only): loss increase relative to DP grows with K. Both DiLoCo and MuLoCo beat their DP baselines at K = 1 and 2.
  - §6.2 (K = 8): H was doubled from 15 to 240. MuLoCo's advantage over DiLoCo (relative to DP) "remain[s] mostly constant across H".
  - Abstract: MuLoCo has "larger critical batch sizes".
- **Tags:** [REMEDY | Muon instead of AdamW as inner optimizer | averaging cost | 150M to 15B | pretraining | better worker scaling relative to DP; figure only | Fig. 6, v3]
- **Bears on:** Q1 (worker-count dependence; critical batch).
- **Differences from ours:** inner optimizer; scale.
- **Question for us:** none at present. A Muon inner optimizer is a larger change than the outer-optimizer remedies.

### B4. DES-LOC: Desynced Low Communication Adaptive Optimizers for Training Foundation Models

- **Authors:** Iacob, Sani, Safaryan, Giampouras, Horváth, Jovanović, Kurmanji, Aleksandrov et al. (11). 2025. Preprint ("Under review" in the PDF).
- **arXiv:** 2505.22549. Versions: v1 28 May 2025 only. **Read v1.** https://arxiv.org/abs/2505.22549
- **Read status:** sections read: abstract, §1, Fig. 2 caption, §4.1 setup and baselines, §5.3, Fig. 5 legend values, §5.4 opening.
- **Setting:**
  - 135M GPT-style model; 6.4B tokens (about 3,200 sequential steps at a global batch of 2M tokens split across M = 4 IID workers).
  - Adam or ADOPT; WSD lr schedule.
  - Baselines:
    - DDP;
    - Local Adam, which averages parameters and both moments;
    - "FAVG+OPT", which keeps optimizer states local;
    - "FAVG−OPT", which resets optimizer states each round.
- **Key findings:**
  - **Fig. 5 legend values, perplexity "(mean ± spread)"** (whether these are final or window-averaged values is not stated in the text read):

    | | Sync every Kx = 16 steps | Sync every Kx = 256 steps |
    |---|---|---|
    | DDP | 10.20 | 10.19 |
    | DES-LOC | 12.11 | 17.33 |
    | Local Adam | 12.27 | 17.22 |
    | keep states (FAVG+OPT) | 12.77 | 17.79 |
    | reset states (FAVG−OPT) | 26.77 | 17.72 |

  - **Introduction:** "re-initializing optimizer states … destabilizes training by triggering loss spikes", citing [33] Sani et al. 2405.10853 and [34] Photon.
  - **Fig. 2 (toy):** periodically resetting states "similarly stalls due to repeated oscillations".
- **Tags:**
  - [REMEDY | keep vs reset Adam state between rounds | averaging cost | 135M | pretraining | Kx = 16: perplexity 12.77 (keep) vs 26.77 (reset); Kx = 256: 17.79 vs 17.72 (no difference) | Figs. 5a and 5b, v1]
  - [REMEDY | average Adam moments with parameters (Local Adam) | averaging cost | 135M | pretraining | 12.27 vs 12.77 (keep) at Kx = 16 | Fig. 5a, v1]
- **Bears on:** Q1 (direct evidence on resetting AdamW each round).
- **Differences from ours:**
  - Kx (the sync period) is 16 or 256, bracketing our H = 125. "K" here is a period, not a worker count.
  - Only about 12.5 rounds at Kx = 256.
  - Global batch fixed (2M tokens split 4 ways); ADOPT/Adam with β2 = 0.9999 in some runs.
- **Question for us:** Does the reset penalty at H = 125 with β2 = 0.95 look more like their Kx = 16 case or their Kx = 256 case? The per-round loss traces in our logs could tell.

### B5. SlowMo: Improving Communication-Efficient Distributed SGD with Slow Momentum

- **Authors:** Wang, Tantia, Ballas, Rabbat (FAIR). 2019. ICLR 2020 (arXiv comment "Accepted to ICLR 2020").
- **arXiv:** 1910.00643. Versions: v1 1 Oct 2019, v2 19 Feb 2020. **Read v2.** https://arxiv.org/abs/1910.00643
- **Read status:** sections read: §4 experiments setup paragraphs, Table 1 (garbled layout; WMT rows mapped using Table B.1's row order), Appendix B.1, B.3, B.4 (Tables B.1 to B.3).
- **Setting:**
  - CIFAR-10, ImageNet (SGD with Nesterov) and WMT'16 En-De Transformer (Adam).
  - 8 nodes for WMT with batch 200k tokens; local steps τ = 12 for Local Adam/SGD and 48 for SGP/OSGP.
  - Slow learning rate α = 1 fixed; slow momentum β tuned (typically 0.4 to 0.8).
- **Key findings:**
  - **WMT validation NLL (Table B.1):** Local Adam 2.179 → 2.137 with SlowMo; SGP 2.137 → 2.106; AR-Adam (synchronous) 2.108. BLEU: Local Adam 26.62 → 27.14; AR-Adam 27.17 (Table 1).
  - "Using τ > 12 for Local SGD resulted in significantly worse loss/accuracy on ImageNet and WMT'16 En-De."
  - **Buffer strategies (Appendix B.4, Table B.3, WMT), training / validation loss:** average buffers 2.438 / 2.101; reset buffers 5.093 / 4.732; maintain buffers 2.447 / 2.106.
    - "When using Adam as base optimizer, reseting the second moment to zeros hurts the optimization performance".
    - The maintain value 2.106 equals the SGP-with-SlowMo entry in Table B.1. (inference) The base algorithm in Table B.3 is probably SGP with Adam at τ = 48.
    - ImageNet (SGD momentum): the strategies are similar (Table B.2), so reset was the default there.
  - The text read does not say whether "reset" also restarts Adam's step counter (bias correction). This matters for comparison with our fresh-AdamW construction.
- **Tags:**
  - [REMEDY | slow (outer) momentum on top of Local Adam | averaging cost | Transformer-base WMT | training from scratch (MT) | validation NLL 2.179 → 2.137 (sync 2.108) | Table B.1, v2]
  - [REMEDY | maintain/average vs reset Adam buffers | averaging cost | Transformer WMT | MT | reset: validation loss 4.732 vs 2.106 | Table B.3, v2]
- **Bears on:** Q1 (Adam reset; outer momentum).
- **Differences from ours:** machine translation; gossip base algorithm in B.3; reset implementation unknown.
- **Question for us:** Our "fresh AdamW" restarts bias correction. Is that what made the reset survivable for us, where SlowMo's reset was catastrophic?

### B6. Asynchronous Local-SGD Training for Language Modeling

- **Authors:** Liu, Chhaparia, Douillard, Kale, Rusu, Shen, Szlam, Ranzato. 2024. Preprint; no venue stated on the arXiv record or found in OpenAlex.
- **arXiv:** 2401.09135. Versions: v1 17 Jan 2024, v2 23 Sep 2024. **Read v2.** https://arxiv.org/abs/2401.09135
- **Code:** Colab at https://github.com/google-deepmind/asyncdiloco, Apache-2.0 (toy example).
- **Read status:** sections read: §4 (optimization challenge), §7 (experiments, Tables 1 to 4), Appendix 10.1.
- **Setting:** 20M/60M/150M models on C4; continued training from a 24k-step pretrained checkpoint; 4 to 16 workers; synchronous DiLoCo as reference. "the same state is used from one round to another, without reset" (Appendix 10.1).
- **Key findings:**
  - **Table 3 (4 workers):** DiLoCo 41.35 / 24.55 / 17.23 vs single-worker fine-tuning at 4× batch 42.47 / 24.80 / 17.47 (20M / 60M / 150M). DiLoCo beats the large-batch baseline.
  - **Table 2 (20M):** with 16 workers, single-worker fine-tuning at 16× batch (40.60) beats DiLoCo (41.25). "As the number of workers increases, the benefit of Local-SGD training diminishes."
  - **§4 (Fig. 5, figure only):** for synchronous Local-SGD, "incorporating Nesterov momentum into the OuterOpt significantly boosts the performance" compared with AdamW + SGD outer.
- **Tags:** [REMEDY | Nesterov outer vs SGD outer (synchronous) | averaging cost | 20M | continued pretraining | "significantly boosts"; figure only | §4, v2]
- **Bears on:** Q1. These are the smallest LM DiLoCo results with numbers found (20M), but they continue from a checkpoint.
- **Differences from ours:** fine-tunes a pretrained checkpoint; the baseline is large-batch, not more steps.
- **Question for us:** none beyond the worker-count trend.

### B7. Smoothing DiLoCo with Primal Averaging for Faster Training of LLMs

- **Authors:** Defazio, Mishchenko, Raman, Shi, Xiao (Meta). 2025. Preprint.
- **arXiv:** 2512.17131. Versions: v1 18 Dec 2025, v2 29 Jan 2026, v3 27 Feb 2026. **Read v3.** https://arxiv.org/abs/2512.17131
- **Code:** https://github.com/facebookresearch/optimizers (GitHub licence field "NOASSERTION").
- **Read status:** sections read: abstract, §1. Table 2's layout was too garbled to use; its values are not recorded.
- **Key finding:** "single-worker DiLoCo outperforms AdamW even in the non-distributed setting". On 160M Llama it reaches AdamW's final loss with "speedups of up to 6.32%" in steps (Fig. 1b).
- **Bears on:** Q1. Like A2 Finding 2, this means part of tuned DiLoCo's parity with DP comes from the outer Nesterov acting as an optimizer. Plain averaging forgoes that gain.
- **Question for us:** none.

### B8. Adaptive Federated Optimization (FedOpt)

- **Authors:** Reddi, Charles, Zaheer, Garrett, Rush, Konečný, Kumar, McMahan. 2020. ICLR 2021 (arXiv comment).
- **arXiv:** 2003.00295. Versions: v1 29 Feb 2020, v2 10 Jul 2020, v3 2 Dec 2020, v4 24 Aug 2021, v5 8 Sep 2021. **Read v5.** https://arxiv.org/abs/2003.00295
- **Read status:** sections read: §3 Remark 1 and the discussion items (i) to (ii), Appendix D.2 (Tables 8 to 10).
- **Setting:** federated, non-IID tasks, including Stack Overflow next-word prediction; E = 1 local epoch; client and server lr tuned on grids.
- **Key findings:**
  - "The server learning rate η = 1 typically used in FEDAVG does not necessarily minimize the upper bound" (Remark 1).
  - "one must decay ηl, not the server learning rate η, to obtain convergence", because "client drift … does not vanish as T → ∞ when ηl is constant" (Discussion ii).
  - Stack Overflow NWP test accuracy (Table 10): FedAdam 25.7; FedYogi 25.7; FedAvgM 24.5; FedAvg 20.5. The tuned FedAvg server lr for SO NWP is 10^0 = 1 (Table 8).
- **Tags:** [REMEDY | adaptive or momentum server optimizer vs FedAvg | averaging cost | small LM (SO NWP; model size not read) | federated training, non-IID | accuracy 25.7 (FedAdam) vs 20.5 (FedAvg) | Table 10, v5]
- **Bears on:** Q1 (theory on schedule and drift; outer optimizer).
- **Differences from ours:** non-IID cross-device FL; local epochs; partial participation.
- **Question for us:** Our client lr stays at 1e-3 for 80% of training. Does the drift term stay at its high-lr level for that whole period?

### C1. SCAFFOLD: Stochastic Controlled Averaging for Federated Learning

- **Authors:** Karimireddy, Kale, Mohri, Reddi, Stich, Suresh. 2019. ICML 2020 (arXiv comment "ICML version" for v3).
- **arXiv:** 1910.06378. Versions: v1 14 Oct 2019, v2 17 Feb 2020, v3 9 Aug 2020, v4 9 Apr 2021. **Read v4.** https://arxiv.org/abs/1910.06378
- **Read status:** sections read: abstract, §1 (contributions), §3.1 (Theorem I and its discussion), §4 (SCAFFOLD idea, partial), §6 (Hessian similarity, partial), §7 intro.
- **Key findings:**
  - FedAvg "suffers from 'client-drift' when the data is heterogeneous (non-iid)" (abstract). The drift is driven by the gradient-dissimilarity parameter G in assumption A1.
  - In the "simpler iid. case i.e. with G = 0 and B = 1", FedAvg's strongly convex rate has no drift term. But it "do[es] not match the lower-bound for the identical case": the local steps K help the noise term, not the optimization term (§3.1).
  - For identical clients (δ = 0), SCAFFOLD matches the IID lower bound "up to acceleration" (§6).
- **Bears on:** Q1 theory. (inference) With IID shards, SCAFFOLD-style control variates target a drift source (G) that is nominally zero for us. SCAFFOLD is therefore not a natural remedy for our averaging cost; only finite-sample differences between shards remain.
- **Differences from ours:** convex or non-convex SGD theory; heterogeneous clients.
- **Question for us:** none for IID. It becomes relevant if Chorus moves to skewed data (the harness supports it).

### C2. Is Local SGD Better than Minibatch SGD?

- **Authors:** Woodworth, Patel, Stich, Dai, Bullins, McMahan, Shamir, Srebro. 2020. Preprint: the arXiv record and the PDF read state no venue (see "Could not verify").
- **arXiv:** 2002.07839. Versions: v1 18 Feb 2020, v2 20 Jul 2020. **Read v2.** https://arxiv.org/abs/2002.07839
- **Read status:** sections read: abstract, §1, §2 (baselines including "thumb-twiddling" SGD, alternative viewpoint), §3 opening, §5 lower-bound discussion (fragments).
- **Key findings:**
  - With IID data, the fair comparison is minibatch SGD with R steps of batch KM.
  - For quadratics, local SGD's error depends only on the product KR, and it "strictly dominates minibatch SGD".
  - For general convex objectives there is a regime "where M is large and K ≳ R" in which local SGD beats minibatch. There is also a lower bound in which local SGD is worse than minibatch and even than "thumb-twiddling" SGD in "the small K and large M regime".
  - The minibatch lower bound's second term "holds even for first-order algorithms that compute MKR stochastic gradients sequentially".
- **Bears on:** Q1 theory.
  - (inference) In IID theory, the extra error of local SGD as H grows comes from non-quadratic curvature (third-order effects) interacting with noise, not from drift.
  - Our centralized arm is the sequential MKR-step baseline, the strongest of the three baselines this paper discusses.
  - Our K = 125 > R = 40 lies in the regime where local SGD is predicted to beat minibatch SGD. That is a statement about a different, weaker baseline.
- **Question for us:** Does local averaging at H = 125 beat a batch-128 minibatch run of 5,000 steps? We have not run that baseline.

### C3. A Quadratic Synchronization Rule for Distributed Deep Learning (QSR)

- **Authors:** Gu, Lyu, Arora, Zhang, Huang. 2023. ICLR 2024 (arXiv comment).
- **arXiv:** 2310.14423. Versions: v1 22 Oct 2023, v2 12 Apr 2024. **Read v2.** https://arxiv.org/abs/2310.14423
- **Read status:** abstract and §1 only.
- **Key finding:** set H "in proportion to 1/η²" as the learning rate decays. On ImageNet (ResNet, ViT), QSR improves test accuracy over other synchronization strategies. With 16 or 64 GPUs, Local AdamW with QSR on ViT-B gets "1.12% or 0.84% higher top-1 validation accuracy" than data-parallel training, in less time.
- **Tags:** [REMEDY | H growing as 1/η² during lr decay | averaging cost | ViT-B / ResNet ImageNet | vision training | +1.12% / +0.84% top-1 vs DP | abstract, v2]
- **Bears on:** Q1 (schedule interaction). Vision only.
- **Question for us:** Our H is fixed through the decay phase. Would QSR-style H scheduling matter at H = 125? It needs a code change.

### C4. Why (and When) does Local SGD Generalize Better than SGD?

- **Authors:** Gu, Lyu, Huang, Arora. 2023. ICLR 2023 (arXiv comment).
- **arXiv:** 2303.01215. Versions: v1 2 Mar 2023, v2 9 Mar 2023. **Read v2.** https://arxiv.org/abs/2303.01215
- **Read status:** abstract only (from the PDF).
- **Key finding:** an SDE analysis shows local SGD induces a stronger drift toward flatter regions. "having a small learning rate and long enough training time enables the generalization improvement over SGD but removing either of the two conditions leads to no improvement."
- **Bears on:** Q1 (why some papers see local SGD beat baselines). (inference) Our runs are short and mostly at high lr, the regime where this paper predicts no generalization benefit.

### C5. Don't Use Large Mini-Batches, Use Local SGD

- **Authors:** Lin, Stich, Patel, Jaggi. 2018. ICLR 2020 (arXiv comment).
- **arXiv:** 1808.07217. Versions: v1 22 Aug 2018, v2 6 Oct 2018, v3 21 Oct 2018, v4 5 Feb 2019, v5 5 Jun 2019, v6 17 Feb 2020. **Read v6.** https://arxiv.org/abs/1808.07217
- **Read status:** sections read: abstract, §1 (partial), §3 (post-local SGD), §4 opening; Appendix B.4.1 headings only.
- **Key findings:**
  - Post-local SGD runs mini-batch SGD until the first lr decay and then switches to local SGD. On CIFAR/ImageNet it closes the large-batch generalization gap.
  - "local SGD with large H and K (e.g. H = 16, K = 16) … can encounter optimization issues during initial training".
- **Tags:** [REMEDY | synchronous warm phase, then local SGD (post-local SGD) | averaging cost | ResNet CIFAR/ImageNet | vision | closes the large-batch generalization gap | §3 to §4, v6]
- **Bears on:** Q1 (start-up phase). Vision only.
- **Question for us:** Did our round-0 phase, with warm-up inside each worker but no synchronization, cost more than later rounds?

### C6. Trade-offs of Local SGD at Scale: An Empirical Study

- **Authors:** Gonzalez Ortiz, Frankle, Rabbat, Morcos, Ballas. 2021. Preprint.
- **arXiv:** 2110.08133. Versions: v1 15 Oct 2021 only. **Read v1.** https://arxiv.org/abs/2110.08133
- **Read status:** sections read: abstract, §1 contributions, §3 setup paragraph on momentum buffers, §5.2 to §5.3 (partial), §6 opening.
- **Key findings:**
  - On ImageNet, local and post-local SGD "suffer from non-trivial accuracy drops as workers or local steps increase".
  - Momentum buffers are "kept local and not synchronized".
  - The lr at the switch to local SGD "is crucial".
  - SlowMo "consistently provided improvements".
- **Tags:** [REMEDY | slow momentum | averaging cost | ResNet-50/101 ImageNet | vision | improves validation accuracy in all cases; figure only | §6, v1]
- **Bears on:** Q1. Vision; documents the "local SGD struggles at scale" counterpoint that DiLoCo argues against.

### C7. Convergence of Distributed Adaptive Optimization with Local Updates (Local Adam)

- **Authors:** Cheng, Glasgow. 2024. ICLR 2025 (PDF header "Published as a conference paper at ICLR 2025").
- **arXiv:** 2409.13155. Versions: v1 20 Sep 2024, v2 12 Feb 2025. **Read v2.** https://arxiv.org/abs/2409.13155
- **Read status:** abstract, §1 (partial), Algorithm 1.
- **Key findings:**
  - In the homogeneous (IID) setting, "Local SGD with momentum (Local SGDM) and Local Adam can outperform their minibatch counterparts in convex and weakly convex settings in certain regimes".
  - Algorithm 1 tracks per-worker moments. Per DES-LOC and Photon, Local Adam averages parameters and optimizer states each round. The averaging step itself was not inspected in the algorithm text read.
- **Bears on:** Q1 theory (inner-optimizer state).

### D1. An Empirical Model of Large-Batch Training

- **Authors:** McCandlish, Kaplan, Amodei, OpenAI Dota Team. 2018. Preprint.
- **arXiv:** 1812.06162. Versions: v1 14 Dec 2018 only. **Read v1.** https://arxiv.org/abs/1812.06162
- **Read status:** sections read: abstract, §2.3 (Eqs. 2.11 to 2.12).
- **Key findings:**
  - Steps and examples trade off as (S/S_min − 1)(E/E_min − 1) = 1 (Eq. 2.11), with the critical batch size B_crit = E_min/S_min (Eq. 2.12).
  - At B = B_crit, training needs twice the minimum steps and twice the minimum examples.
  - The critical batch "depends on the level of performance" targeted. For LSTMs on Billion Word, the noise scale is roughly independent of LSTM size at fixed loss.
- **Bears on:** Q1 (the cost of 4× fewer sequential steps). See the synthesis for the arithmetic.

### D2. How Does Critical Batch Size Scale in Pre-training?

- **Authors:** Zhang, Morwani, Vyas, Wu, Zou, Ghai, Foster, Kakade. 2024. ICLR 2025 (arXiv comment).
- **arXiv:** 2410.21676. Versions: v1 29 Oct 2024, v2 8 Nov 2024, v3 20 Feb 2025, v4 21 Apr 2025. **Read v4.** https://arxiv.org/abs/2410.21676
- **Read status:** abstract and §1 opening.
- **Key finding:** for 85M to 1.2B models on C4, "CBS scales primarily with data size rather than model size".
- **Bears on:** Q1. (inference) Our run is small in data (164M characters), which would push the critical batch down. That would make a batch-128 parallel arm more likely to lose to a batch-32 sequential arm.

### D3. Lower-relevance items opened

- **Exploring Scaling Laws for Local SGD in LLM Training.**
  - He, Zhuang, Wu. 2024. arXiv 2409.13198, v1 20 Sep 2024 only. **Read v1.** Technical report.
  - Read status: abstract and setup grep (§3).
  - 8 nodes; 4M-token global batch matched to DDP; Nesterov outer; a fitted local-SGD loss law versus DDP (Fig. 1).
  - Notes a "significant loss spike … after each outer optimizer" step with 6k local steps (§3, partial).
  - Bears on Q1 only weakly.
- **Overcoming the Communication-Performance Tradeoff in LLM Pretraining (SparseLoCo).**
  - Sarfi, Thérien, Lidin, Belilovsky. 2025. arXiv 2508.15706: v1 21 Aug 2025, v2 5 Nov 2025, v3 23 Jul 2026. **Read v3.**
  - Read status: abstract, §1 (partial), §4 setup (partial), Fig. 3 caption.
  - Scope is compression. It names DiLoCo with outer SGD "LocalAdam". It reports that "naively combining TOP-k with DiLoCo's outer momentum leads to large performance degradation", and that error feedback "naturally acts as a local approximation of outer momentum".
  - Not a source for averaging-cost numbers.
- **Outer-Momentum Restarting in High-Dimensional Two-Phase Optimization.**
  - Topollai, Ma, Dimlioglu, Tay, Choromanska. 2026. arXiv 2605.28585, v1 27 May 2026 only. **Read v1.**
  - Read status: abstract and grep of the experiments appendix.
  - 150M Llama on C4, 2-replica DiLoCo, communication periods 64 to 2048. Periodic outer-momentum restarts "widen the stable range of outer learning rates and momentum values across communication periods".
  - Figures only. A search result attributed it to ICML 2026; not verified at source.
- **Cosine-Gated Adam-Decay (CGAD) for Decoupled DiLoCo.**
  - Shah, Sun. 2026. arXiv 2605.09126, v1 9 May 2026 only. **Read v1.**
  - Read status: abstract, §5.1 setup, Appendix G.
  - Asynchronous staleness setting at 10M/25M/1B/7B, but with a 30M-token C4 slice, K = 4 (or 2) workers and H = 8.
  - Final losses are far above converged values (for example 7.56 nats at 1B), so it is not informative for the synchronous gap (inference).
  - Appendix G, Table 11 (10M, staleness τ = 8): Nesterov 0.7/0.9 diverges (91.0). The best setting was outer lr 0.1 with no momentum (7.6).
- **Moshpit SGD (2103.03239) and DeMo (2411.19870).**
  - Abstract only, from the arXiv API.
  - Moshpit SGD: Ryabinin, Gorbunov, Plokhotnyuk, Pekhimenko. NeurIPS 2021 (arXiv comment). Versions: v1 4 Mar 2021 … v4 11 Jan 2022. An averaging protocol for unreliable devices; it changes how averages are computed, not the averaging cost. Code yandex-research/moshpit-sgd, Apache-2.0.
  - DeMo: Peng, Chen, Su, Quesnelle, Kingma, Liu. Versions: v1 29 Nov 2024, v2 6 Feb 2026. Compressed momentum exchange every step (300M and 1B), not local averaging. Code bloc97/DeMo, no licence per the GitHub API.
  - Neither bears directly on the +6.1%.

## Synthesis for question 1

### 1. Anchor table: published local-averaging gaps nearest to our setting

Definitions:

- "rel." is the relative increase in loss (or log-perplexity) versus the paper's baseline. Perplexity was converted with ln; all conversions are mine.
- "abs." is the absolute loss difference in nats per *token* (BPE). Ours is in nats per *character*.
- "same-step DP" means data-parallel with global batch M × local batch and the same number of steps, i.e. equal compute and equal sequential steps.
- "more-steps" means M× more sequential steps at the local batch, which is our centralized arm.

| Paper (locator, version) | Size | M | H | Rounds R | Outer | Inner state | Baseline type | rel. gap | abs. gap |
|---|---|---|---|---|---|---|---|---|---|
| **Ours** (Stage 0 Task B) | 46M MoE (≈ 10M active), char-level | 4 | 125 | 40 | SGD lr 1 (plain) | reset each round | more-steps (4×) | **+6.1%** | **0.061 nats/char** |
| DiLoCo T2 (v3) | 150M | 8 | 500 | 128 | Nesterov 0.7/0.9 | kept | more-steps (8× updates) | +0.75% | 0.020 |
| same | 150M | 8 | 500 | 128 | Nesterov | kept | same-step DP (8× batch) | −0.68% | −0.019 |
| Khaled T3 (v2) | 150M | 4 | 50 | ≈ 480 | SGD lr 1 (plain) | kept | same-step DP (4× BS) | +1.8% | 0.050 |
| same | 150M | 4 | 150 | ≈ 160 | SGD lr 1 | kept | same-step DP | +1.4% | 0.040 |
| same | 150M | 4 | 500 | ≈ 48 | SGD lr 1 | kept | same-step DP | +3.1% | 0.088 |
| same | 150M | 4 | 50 | ≈ 480 | Nesterov lr 1.0 | kept | same-step DP | −1.1% | −0.031 |
| Horoi T2 (v1) | 178M | 4 | 30 | ≈ 226 (inference: ≈ 3.56B tokens ÷ 524k per step ÷ 30) | SGD (tuned lr ≈ 1.4) | kept | same-step DP | +1.9% | 0.056 |
| same | 178M | 4 | 30 | | Nesterov | kept | same-step DP | +1.0% | 0.030 |
| Horoi T4 (v1) | 178M | 8 | 120 / 240 | | Nesterov (tuned) | kept | same-step DP | +3.3% / +4.4% | 0.095 / 0.127 |
| Scaling Laws T4 (v1) | 35M | 4 | 30 | Chinchilla | Nesterov (tuned) | kept | same-step DP, tuned batch | +2.0% | 0.069 |
| Streaming T6 (v1) | 35M | 4 | 30 / 100 | Chinchilla | Nesterov 0.4, streaming FP4 | not stated | DP (batch convention not stated) | +2.6% / +3.7% | 0.09 / 0.13 |
| OpenDiLoCo T2 (v1) | 1.1B | 4 | 125 / 500 | 352 / 88 | Nesterov 0.7 | not stated | same-step DP (4×) | +0.96% / +2.4% | 0.023 / 0.057 |
| Factored Gossip (v1) | 1.5B | 8 | 100 / 500 / 1000 | ≈ 190 / 38 / 19 | Nesterov 0.7 (not retuned) | not stated | same-step DP | +2.2% / +9.0% / +16.6% | 0.062 / 0.26 / 0.47 |
| SlowMo B.1 (v2) | Transformer, WMT | 8 | 12 | many | none (Local Adam) | maintained | synchronous Adam, same batch | +3.4% (NLL) | 0.071 |
| DES-LOC F5 (v1) | 135M | 4 | 16 / 256 | ≈ 200 / 12.5 | none (FAVG+OPT) | kept | same-step DDP | +9.7% / +24% | 0.225 / 0.557 |
| DES-LOC F5 (v1) | 135M | 4 | 16 / 256 | | none (FAVG−OPT) | **reset** | same-step DDP | +41.6% / +23.8% | 0.965 / 0.553 |

### 2. Is a gap of about 6% expected at our setting?

What the literature shows:

- No published local-SGD or DiLoCo result at our combination was found. The combination is character-level, about 10M active parameters, MoE, M = 4, H = 125, R = 40, plain averaging, a fresh AdamW each round, and a more-steps baseline. Not found in this search; coverage is described in the query log.
- The smallest-scale pretraining gaps with numbers are 35M with M = 4. They are +2.0% at H = 30 with tuned Nesterov (Scaling Laws) and +2.6%/+3.7% at H = 30/100 (Streaming DiLoCo).
- The closest plain-averaging measurement is Khaled et al. at 150M, M = 4: +1.4% to +3.1% in loss at H = 150 to 500, with Adam state kept and a same-step DP baseline.
- Every one of these is smaller than our +6.1% in relative terms.

Inference: what could make up the difference. Our design stacks at least four handicaps that each paper measures separately. Their sizes are not additive and not measured in our setting.

1. **The baseline is harder.**
   - Our centralized arm takes 4× more sequential steps. Most DiLoCo-family papers instead compare with DP at the same steps and a larger batch.
   - The one paper with both baselines (DiLoCo Table 2, 150M, 8 workers) shows the more-steps baseline is 1.44% better in loss than the same-step large-batch DP. DiLoCo sits between the two.
   - DiLoCo's own limitations section attributes this to outer updates having "effectively too large a batch size".
   - McCandlish's model says this cost depends on how large 128 × 256 characters is relative to B_crit for our task. We do not know B_crit (gap G2).
2. **No outer momentum and outer lr = 1.**
   - At 150M, M = 4, H = 50: plain averaging 17.75 vs Nesterov lr 1.0 16.38, about 2.9% in loss.
   - The tuned outer SGD lr is above 1: 1.6 at R = 8 (Horoi Table 5) and about 1.4 at R = 4 (garbled table).
   - Averaging nearly orthogonal pseudo-gradients shrinks the step norm by about 1/√M (DiLoCo §6.2; Decoupled DiLoCo D.2).
3. **Optimizer reset.**
   - The direct evidence is mixed: catastrophic in SlowMo (WMT) and DES-LOC at Kx = 16, neutral in DES-LOC at Kx = 256, and used successfully by Photon at ≥ 1.3B.
4. **Small model.**
   - The gap shrinks with N in Scaling Laws (M = 4: +2.0% at 35M → +0.3% at 2.4B). The "Future is federated" paper (75M loses, 1.3B ties) and Photon point the same way.
   - Factored Gossip reports the opposite trend for H tolerance (160M tolerant, 600M/1.5B not), but with an untuned outer lr.

Inference on whether 6% is plausible: given (1) to (4), a gap of about 6% is plausible. It is not the number any single paper would predict.

- The largest single documented penalties relevant to us are the plain-averaging penalty (about 2 to 3% at 150M) and the more-steps baseline (about 1.4% at 150M with 8 workers).
- The Adam-reset penalty at H = 125 is unknown. It could be near zero (DES-LOC Kx = 256 case) or large (Kx = 16 case).

Units caveat (inference):

- A relative gap in loss per unit is invariant to tokenization on the same text, because total code length is the same quantity in bits per character or nats per token.
- Relative gaps are still not comparable across datasets or loss levels (text8 characters vs C4 BPE), because the entropy floor differs.
- Absolute gaps per character and per token cannot be compared without the characters-per-token ratio.
- Neither metric gives a clean cross-paper comparison. Relative % is the less bad choice for our comparison and matches the 5% criterion.

### 3. Dependence on H

- **Monotone worsening with H beyond very small H, in every LM study with an H sweep:**
  - Scaling Laws Fig. 9;
  - Horoi Table 4 (R = 8: +2.4% → +4.4% for H 30 → 240);
  - Streaming DiLoCo Table 6;
  - OpenDiLoCo 1.1B (H 125 vs 500);
  - Factored Gossip;
  - MuLoCo Fig. 6b;
  - DiLoCo Fig. 4 (H = 1000 only +2.9% perplexity over H = 50, non-IID, from a pretrained start).
- **Exception:** plain averaging in Khaled et al. is "relatively constant" from H = 250 to 2000. It is already about as bad as a single worker by then (18.1 to 18.4 vs one-worker DP 18.07).
- **Interaction with outer lr:** the optimal outer lr rises with H (Scaling Laws Fig. 8). Nesterov at a fixed high outer lr becomes unstable at large H (Khaled A.1.2, a 10.7% degradation).
- **Inference: rounds may matter as much as H.**
  - The very large gaps (DES-LOC Kx = 256 with about 12 rounds; Factored Gossip H = 1000 with about 19 rounds) occur with few rounds.
  - Our 40 rounds is close to Factored Gossip's H = 500 case (about 38 rounds, +9% with an untuned outer lr) and Khaled's H = 500 case (about 48 rounds, +3.1% for plain averaging).
  - Only one sweep per paper varies H at fixed total steps, so H and R are confounded everywhere.

### 4. Dependence on worker count

- **At a fixed global batch, the gap grows with M:**
  - Scaling Laws Table 4: 35M, +0.7/+2.0/+3.9% for M = 2/4/8;
  - Horoi Table 2: R = 2/4/8, +0.8/+1.9/+3.8% for outer SGD;
  - MuLoCo Fig. 6a.
- **At a fixed per-worker batch (more compute with more workers):**
  - plain averaging gains nothing from more workers and gets worse at M = 16 (Khaled: 18.64/17.75/18.38/19.86 for M = 2/4/8/16);
  - Nesterov improves, then plateaus (16.81 → 16.25);
  - DiLoCo Table 3 shows diminishing returns beyond 8 workers.
- **Fine-tuning from a checkpoint** (Async Local-SGD Table 2, 20M): with 16 workers a large-batch single worker beats DiLoCo.

### 5. Dependence on model size

- **The gap shrinks with N:**
  - Scaling Laws Table 4 (all M);
  - Sani et al. 2405.10853 (75M loses, 1.3B ties);
  - Photon ("perplexity gains grow with model size");
  - DiLoCo's conjecture that larger models suffer "less interference" (§5, v3).
- **Disagreement:** Factored Gossip finds tolerance to H = 1000 falls with size (160M → 1.5B). This used a fixed outer lr and few rounds, so it is not a clean contradiction.
- **Inference:** our model is smaller (about 10M active parameters) than every DiLoCo-family result with numbers except CGAD's undertrained async runs. Extrapolating the Scaling Laws trend down to 10M would predict a larger gap than the 35M value. This has not been measured.

### 6. Outer optimizer (plain averaging as the special case)

- **Plain averaging (outer SGD, lr 1) is worse than tuned Nesterov in the LM papers that compare them:**
  - DiLoCo Fig. 6 (figure only);
  - Async Local-SGD §4 (figure only);
  - Khaled Table 3 (2.9% loss at H = 50, 150M);
  - Horoi Table 2 (+1.9% vs +1.0% at R = 4);
  - SlowMo on WMT (2.179 → 2.137 NLL).
- **Tuned outer SGD lr exceeds 1** (Horoi Table 5: 1.6; Khaled theory "sometimes … greater than 1").
- **Merge-based aggregation beats averaging:** Iso-C or IsoLoCo (Horoi; R = 4: 2.864 vs Nesterov 2.911 vs DP 2.881), and RDA in Decoupled DiLoCo. TIES and DARE did not help (Horoi Table 1; Decoupled DiLoCo D.2).
- **Disagreement:** Photon (125M, N = 4, local batch 32, global 128) reports plain averaging reaching targets about 2× faster than DiLoCo. Its DiLoCo outer lr was restricted to 0.1 because higher values diverged (Fig. 6 caption). Inference: this tells us Nesterov can be unstable at small batch and small scale. It does not show that averaging is better when Nesterov is stable.
- **Inference on whether Nesterov helps at our H:** in Khaled Table 3 (Adam state kept), Nesterov lr 0.7 versus plain averaging is inconsistent across H.
  - It is better at H = 50 (17.25 vs 17.75), 250 (18.09 vs 18.20) and 500 (17.95 vs 18.44).
  - It is worse at H = 150 (17.90 vs 17.58) and 2000 (18.40 vs 18.11), and equal at 1000 (18.16 vs 18.18).
  - These look like single runs within noise; the paper reports no seeds.
  - Nesterov lr 1.0 is clearly better at H = 50 to 250 (16.38, 16.79, 17.12), about equal at 500 (18.15 vs 18.44), and worse at 1000 to 2000 (18.75 and 18.36).
  - So the benefit at H in the hundreds needs the outer lr retuned with H.
  - The most robust option across H in that table is Schedule-Free SGD (17.18 at H = 500; 17.59 at H = 2000).
- **Single-worker gains:** single-worker DiLoCo beats AdamW (Scaling Laws Finding 2; Defazio et al. up to 6.32% fewer steps). Part of "DiLoCo matches DP" is an optimizer improvement that plain averaging does not get.

### 7. Inner-optimizer state (reset, keep, average)

- **Standard practice is "keep".** DiLoCo, Scaling Laws, Khaled, Horoi and Async Local-SGD all keep the state. DiLoCo found syncing states gave no significant improvement.
- **Reset evidence:**
  - catastrophic: SlowMo WMT (validation loss 4.732 vs 2.106) and DES-LOC Kx = 16 (perplexity 26.77 vs 12.77);
  - neutral: DES-LOC Kx = 256 (17.72 vs 17.79);
  - deliberately used, with good reported results: Photon at billion scale (baseline caveats above);
  - loss spikes after reset are claimed by DES-LOC, citing the Photon group's papers.
- **Averaging states:** Local Adam (12.27 vs keep 12.77 at Kx = 16) and DES-LOC improve modestly over keep, at extra communication (2× to 3×).
- **Inference on why our reset may be milder than SlowMo's:**
  - We construct a fresh AdamW, which restarts bias correction. SlowMo's reset implementation is not described.
  - With β2 = 0.95, the second-moment estimate has a time constant of about 20 steps, short compared with H = 125.
  - The first post-reset steps are nearly sign-like updates of size about lr per coordinate, at full lr (1e-3), because warm-up runs only in round 0. That could cause per-round loss spikes.
  - Not measured. Our existing logs could show it (gap G6).

### 8. Learning-rate schedule

- **Inner lr decay reduces outer-gradient norms naturally**, so DiLoCo found cosine decay of the outer lr unnecessary (§3.1).
- **Outer lr schedule:** a constant outer lr was best, and outer warm-up harmful (Khaled A.1.5).
- **Client lr decay:** the client lr, not the server lr, must decay for drift to vanish (Reddi Discussion ii).
- **Sync frequency during decay:** QSR (vision) recommends more local steps as lr decays, H ∝ 1/η².
- **Generalization:** local SGD's generalization benefit needs a small lr and long training (Gu et al. 2023).
- **Post-local SGD:** the switch point and its lr matter (Lin et al.; Ortiz et al.).
- **Small batches:** Photon argues that small client batches allow high lr and a cosine period scaled to the client batch.
- **Inference for our WSD-like schedule** (constant 1e-3 for 80%, linear to 1e-4):
  - Drift from a constant client lr persists for 80% of training.
  - H is not adapted during the decay.
  - The decay ends at 1e-4, not 0.
  - No paper isolates a WSD inner schedule under local averaging. INTELLECT-1 used one without a baseline. Not found in this search.

### 9. Critical batch size and "4× fewer sequential steps"

- **Steps-examples trade-off:** (S/S_min − 1)(E/E_min − 1) = 1, with B_crit = E_min/S_min (McCandlish Eqs. 2.11 to 2.12).
  - Below B_crit, a 4× larger batch with 4× fewer steps costs little.
  - At or above B_crit, it costs up to 2× in examples.
- **Data dependence:** CBS grows mainly with data size (Zhang et al.). DiLoCo raises the optimal batch (Scaling Laws Finding 3; MuLoCo).
- **Direct measurements of the more-steps vs larger-batch difference at equal compute:**
  - DiLoCo Table 2 (150M): 8× batch DP is 1.44% worse in loss than 8× updates.
  - Khaled Fig. 4: figure only.
- **Inference:** we cannot apportion our 6.1% between "4× fewer steps" and "local averaging per se" without a batch-128 baseline.

### 10. Baseline mapping

| Paper | Its baseline | Relation to our equal-compute "4× more steps at batch 32" arm |
|---|---|---|
| DiLoCo 2311.08105 | Four baselines, including "8× updates" (more steps) and "8× batch" DP | 8× updates is our analogue; DiLoCo loses 0.75% in loss to it |
| Scaling Laws 2503.09799 | DP at the same N and tokens, each with its own tuned batch | Easier than ours (DP may take a smaller batch and more steps, but DiLoCo is also tuned) |
| Streaming 2501.18512 | DP at the same tokens | Same-step style |
| OpenDiLoCo 2407.07852 | DP at 4× or 8× batch, same steps | Same-step; easier than ours |
| Khaled 2509.10439 | DP 1× batch (¼ compute) and DP 4× batch, same steps | Same-step; the Fig. 4 "vary steps" curve is our analogue (figure only) |
| Horoi 2607.03011 | AdamW DP at a matched global batch | Same-step |
| Photon 2411.02908 | "Centralized" with equal workers; not equal compute (Table 3) | Not comparable to D17 |
| DES-LOC 2505.22549 | DDP at the same global batch and steps | Same-step |
| Factored Gossip 2606.22768 | Sync-DP at the same global batch | Same-step |
| Woodworth 2002.07839 | Minibatch SGD (R steps of batch KM); also notes serial MKR-step algorithms | Our centralized arm is the serial baseline, the strongest of the three |

### 11. Theory for IID data as H grows

- **Client drift (SCAFFOLD) needs heterogeneity.** With G = 0 the drift term disappears. SCAFFOLD-type corrections therefore target a cause our IID setup lacks (C1).
- **Remaining IID costs:**
  - local steps do not improve the optimization term (C1 §3.1);
  - for non-quadratic objectives, local SGD's error depends on K and R separately, not just on KR (C2);
  - with a constant client lr, a drift-like term persists (B8 Remark/Discussion);
  - the outer lr trades optimization error against variance (B1);
  - outer acceleration improves the dependence on R (B1).
- **Inference: the theory predicts direction, not magnitude.** The gap should grow with H at fixed total steps, through curvature changes within a round. An outer lr above 1 or outer momentum should partly offset it. Nothing in the theory read predicts a 6% figure for a 46M MoE.

### 12. Where papers disagree, and what is silent

- **Disagreements:**
  - Plain averaging vs DiLoCo: Photon vs DiLoCo, Khaled and Horoi.
  - Model-size trend of H tolerance: Scaling Laws vs Factored Gossip.
  - Optimizer reset: Photon (uses it) vs SlowMo and DES-LOC (harmful at short periods).
- **Silent (not found in this search):**
  - character-level LMs with local averaging;
  - MoE with local averaging below 2.8B active;
  - Adam reset at H ≈ 100 to 150 with β2 = 0.95;
  - a WSD inner schedule under local averaging;
  - the cost of a more-steps baseline measured at M = 4;
  - any study combining reset + plain averaging + small model.

## Candidates for the joint reading list

1. **DiLoCo, 2311.08105 (v3). Foundational, read early.** It defines the method we partly implement. Table 2 contains the only "more sequential steps" baseline in the family. Its limitations section names the large-effective-batch cost. It also covers inner-state handling, outer optimizers and H.
2. **Understanding Outer Optimizers in Local SGD, Khaled et al., 2509.10439 (v2; NeurIPS 2025). Specific, read early.** The only paper measuring plain averaging (outer SGD lr 1) at M = 4 across H = 50 to 2000 against both 1× and 4× DP. Its theory explains why the outer lr should exceed 1.
3. **Scaling Laws for DiLoCo, 2503.09799 (v1; NeurIPS 2025). Foundational.** Small-scale (35M) M = 4 gaps, the gap's shrinkage with size, outer-lr dependence on M and H, and the batch-size tolerance finding.
4. **Can Model Merging Improve Aggregation in DiLoCo?, 2607.03011 (v1). Specific, read later.** Clean 178M tables for outer SGD vs Nesterov vs merge-based aggregation across R and H. IsoLoCo is the strongest averaging-replacement remedy found. MIT code.
5. **DES-LOC, 2505.22549 (v1), together with SlowMo Appendix B.4, 1910.00643. Specific, read later.** The only LM measurements of reset vs keep vs averaged Adam state, which bears directly on our D19 choice.

## Gaps

Questions no paper answers that the existing harness could answer. Harness features are taken from the brief: other H, Nesterov outer momentum, slice sizes, worker counts, assignment policies, partial/full/sliced modes, skewed data, worker dropout.

- **G1. H sweep at fixed total compute, plain averaging vs Nesterov outer, full-model mode, M = 4.** For example H ∈ {25, 50, 125, 250, 500}, i.e. R ∈ {200, 100, 40, 20, 10}. This gives the averaging cost as a function of H at about 10M active parameters, character level. No small-scale character-level H curve exists.
- **G2. Outer lr sweep, including lr > 1 without momentum and several Nesterov lr values, at H = 125.**
  - Horoi and Khaled suggest the best SGD outer lr is 1.4 to 1.6, and that Nesterov's lr must be retuned with H.
  - Whether the harness's outer optimizer takes an lr above 1 should be checked in code (inference: the Nesterov implementation presumably has an lr parameter).
- **G3. Worker count at fixed total compute (M = 2, 4, 8 with H fixed, or with R fixed).** Published worker-count curves come from dense BPE models at 35M or larger.
- **G4. Baselines that apportion the 6.1%** (these need the centralized script, not the simulated arms):
  - (a) centralized at batch 128 for 5,000 steps, the "same-step DP" analogue. This isolates the 4×-fewer-steps cost;
  - (b) centralized at batch 32 for 5,000 steps (¼ compute), the "single worker" floor. Khaled's plain-averaging runs at H ≥ 250 were no better than this floor.
  - Both are likely configuration changes; to be verified in the script.
  - Note: an H = 1 full-averaging run is not equivalent to DP at batch 128 in our harness. A fresh AdamW every round makes each H = 1 step a bias-corrected first Adam step, close to a sign update. This is inference from our D19 implementation as described in the brief.
- **G5. Keep vs reset vs average AdamW state at H = 125.**
  - DES-LOC brackets our H, with a catastrophic effect at Kx = 16 and none at 256.
  - Not a listed harness feature: a small code change is needed.
- **G6. Per-round loss traces from the existing Stage 0 logs**, around each merge and each optimizer reset. No new runs. This tests whether reset-induced spikes (DES-LOC's claim) occur at our H and β2.
- **G7. Skewed vs IID data at M = 4.** This tests whether the IID-theory prediction (no drift term) holds in practice for our model. The harness supports skewed data.
- **G8. Dense vs MoE at matched active parameters.** This would show whether local-only load balancing adds to the averaging cost (Decoupled DiLoCo is the only MoE evidence, at 2.8B active). It is not clearly a harness feature: model-config change, to be verified.
- **G9. Schedule variants: H increasing during the decay phase (QSR), or decay to a lower final lr.** Needs a code change.

## Could not verify

- **Photon's centralized baseline token count:**
  - Table 6 (v2) gives the same batch and schedule length for the centralized and federated 1.3B/3B runs.
  - Table 3 gives federated compute time 1.6× to 2.8× the centralized compute time.
  - Read: §5, Appendix A to C. Not resolved.
- **SlowMo's "reset buffers" implementation** (whether Adam's step counter or bias correction was also reset) and the exact base algorithm and τ of Table B.3. Read: Appendix B.4 text; not stated.
- **Streaming DiLoCo's venue.** A citation in 2605.28585 hints at a conference; OpenAlex lists arXiv only. Recorded as preprint.
- **Woodworth et al.'s venue:** not stated on the arXiv record or in the PDF read, and not checked in OpenAlex. Recorded as preprint.
- **Outer-Momentum Restarting at ICML 2026** comes from a search result (an icml.cc page) that was not opened. Recorded as preprint.
- **Factored Gossip at ICML 2026** comes from the arXiv comment only.
- **Garbled tables:**
  - Scaling Laws Fig. 7 best-outer-lr values (heatmap text layer);
  - Horoi Table 6 (outer SGD lr per R; first row assumed to be DiLoCo SGD);
  - INTELLECT-1 Appendix A (values mapped by order);
  - Defazio et al. Table 2 (not used).
- **Streaming DiLoCo Table 6's batch convention** (global batch fixed or growing with M): not stated in the text read.
- **DES-LOC Fig. 5 legend values:** whether they are final or window-averaged perplexities is not stated in the text read. *Resolved 2026-10-11 by the coordinator's audit:* §4.1's "Metrics" paragraph (raw text, v1) says plotted values are "means and standard deviations computed over the last round (shown next to labels)".
- **Not opened at all (leads):** EDiT (2412.07210), Pseudo-Asynchronous Local SGD (2504.18454), HALoS (2506.04531), HeLoCo (2606.00271), LoRDO (2602.04396), "Not Every Sync Is Safe" (2607.02544), Eager Updates (2502.12996; abstract via API only), Distributed Sign Momentum with Local Steps (2411.17866; title and metadata via API only), Stich "Local SGD Converges Fast and Communicates Little" (1805.09767), Wang & Joshi Cooperative SGD.
- **Seen in OpenAlex results, relevant to other strands:** FoMoE "Breaking the Full-Replica Barrier with a Federation of MoEs" (2606.19025). Not opened; flagged for the MoE and closest-methods researchers.

## Query log

All times local (TST), 2026-10-11.

| Time | Tool or site | Query or action |
|---|---|---|
| 10:28 | n/a | Started; read the brief, `docs/prior-work.md`, `docs/stage0-report.md` |
| 10:29 | export.arxiv.org API | `id_list` for 25 IDs (DiLoCo family, classic local SGD, MuLoCo, SparseLoCo, DES-LOC, Khaled, DeMo, Moshpit, merge paper, QSR, Gu 2023, He 2024, Sani 2024) |
| 10:30 to 10:34 | arxiv.org | PDFs and abs pages (`sleep 3` between requests) for 23 papers; `pdftotext -layout` |
| 10:39 | arxiv.org | HTML of 2509.10439v2 (clean Tables 3 to 5) |
| 10:41 | WebSearch (standard) | "DiLoCo inner optimizer state reset AdamW local SGD 2025" |
| ≈ 10:41 | WebSearch (standard) | "local SGD small language model outer learning rate momentum ablation arXiv 2026" |
| ≈ 10:41 | WebSearch (standard) | "DiLoCo critical batch size sequential steps local SGD language model" |
| ≈ 10:41 | WebSearch (standard) | "Cheng Glasgow "Convergence of Distributed Adaptive Optimization with Local Updates" arXiv" |
| ≈ 10:41 | WebSearch (standard) | "DiLoCo learning rate schedule warmup-stable-decay inner learning rate outer synchronization arXiv 2025" |
| ≈ 10:41 | WebSearch (standard) | "local SGD pretraining fewer sequential steps versus minibatch equal compute language model 2026 arXiv" |
| ≈ 10:41 | WebSearch (standard) | "averaging Adam moments local SGD transformer pretraining "optimizer state" synchronization ablation 2026" |
| ≈ 10:41 | WebSearch (standard) | "DiLoCo small models 2026 arXiv number of inner steps H workers gap data-parallel ablation" |
| 10:42 | export.arxiv.org API | `id_list` for 9 new IDs (2606.22768, 2605.28585, 2512.17131, 2605.09126, 2502.12996, 2409.13155, 1812.06162, 2410.21676, 2411.17866) |
| 10:42 to 10:44 | arxiv.org | PDFs and abs pages for 7 of them |
| 10:48 | api.github.com | `repos` for shoroi/isoloco, facebookresearch/MuLoCo, facebookresearch/optimizers, google-deepmind/asyncdiloco, yandex-research/moshpit-sgd, bloc97/DeMo, PrimeIntellect-ai/OpenDiloco, PrimeIntellect-ai/prime |
| 10:48 | api.openalex.org | `works?search=` for 8 titles (venues): Khaled; Streaming DiLoCo; Async Local-SGD; Scaling Laws; DiLoCo; OpenDiLoCo; DES-LOC; MuLoCo |
| 10:50 | n/a | Began writing these notes |

Not covered in this round:

- No citation chasing (Semantic Scholar was not tried; OpenAlex was used only for venues).
- No GitHub code search; no inspection of any repository's code (for example how OpenDiLoCo, Photon or torchft handle optimizer state).
- Not read beyond abstract or setup:
  - MuLoCo's critical-batch figures;
  - Factored Gossip's 160M/600M figure;
  - DiLoCo's figures (outer optimizers, H);
  - Scaling Laws Fig. 9 (H);
  - the theory sections of Khaled et al.
- Not opened: EDiT, Pseudo-Async Local SGD, HALoS, HeLoCo, LoRDO, Eager Updates (body), Distributed Sign Momentum, Stich 2019, Wang & Joshi, Covenant-72B, INTELLECT-2/3.
- No search for character-level or byte-level LMs trained with local SGD beyond the general queries above. This combination was not found.
- No non-English venues; no workshop proceedings outside arXiv.
