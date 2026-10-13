# Question 3: the cost of partial updates (sub-model and partial training)
> Correction (2026-10-11, coordinator): our experts are SwiGLU with three matrices, so expert parameters are 42.47M of 46.05M (92%), about 14.2M are active per token, and a partial-arm worker trains about 54%. Figures in this file based on two-matrix experts (about 10M active, about 28M expert parameters, about 61% or 70%) are wrong; see the report's header.

| | |
|---|---|
| Date | 2026-10-11 (session started 10:28 TST) |
| Prepared by | Research subagent for question 3 of `docs/research/2026-10-11-deep-research-prompt.md` |
| Scope | Q3 only, plus remedy evidence on slice size, overlap and assignment. SPES, MoE routing and local-averaging theory beyond the IST papers are out of scope. |
| Method | Every number below was read from raw paper text (PDF fetched from arXiv with `curl`, converted with `pdftotext -layout`; one HTML cross-check; one CVF open-access PDF). Search snippets were used only to find papers. Where a PDF table's layout came out garbled, the note says so and explains how the numbers were mapped. |

**Our number, restated.** In `docs/stage0-report.md` the +1.4% partial-update step is measured in points of centralized BPC: (partial − full) / centralized, which gives +1.42, +1.61 and +1.32 points for seeds 7, 11 and 19 (+1.3 to +1.6). Measured directly against full-model averaging, the gap is +1.33%, +1.52% and +1.24% (mean of the per-seed ratios +1.37%). In absolute terms it is +0.021 bits per character (seed means 1.5462 against 1.5254). The two definitions differ by less than 0.1 point. (Computed from the report's Task B table.)

**How the published numbers are converted.** BPC is cross-entropy in bits, so a relative BPC gap equals a relative gap in mean cross-entropy (nats per token). Where a paper reports perplexity (PPL), I convert with relative gap = ln(PPL_partial) / ln(PPL_full) − 1, and I also give the raw PPL gap. Relative gaps at different loss levels, and over different units (characters, sub-words, words), are not equivalent. For example, a 1.4% gap at PPL 12.75 is about 0.036 nats per token, while ours is 0.021 bits per character. Treat cross-paper comparisons as order-of-magnitude only.

**Facts about our partial arm that matter for comparisons.** These come from reading the code; they are not stated in the brief.
- `configs/task_b/sliced.toml` with `--set sim.mode=partial` uses `policy = "coverage"`, `cross_layer = "same"` and `capacity = 4`, with H = 125 and R = 40.
- `cassandra_chorus/coordinator/assignment.py` (`_coverage`, seeded by `assignment/round{r}`) draws the assignment again in every round. It first deals each expert to one worker in turn, then fills each worker's remaining capacity at random.
- (inference from reading the code; not executed, because the Python interpreter failed to start in this session.) With 4 workers of capacity 4 and 8 experts, each expert's holder count in a round is 1 + Binomial(3, 1/3). That gives 1 holder with probability 8/27 ≈ 0.30, 2 with 12/27 ≈ 0.44, 3 with 6/27 ≈ 0.22 and 4 with 1/27 ≈ 0.04, a mean of 2. "Each expert is updated by 2 of 4 workers" is therefore the average, not a fixed count. In about 30% of (expert, round) pairs a single worker updates the expert.
- The `rolling` policy, with the same capacities, would give exactly 2 holders per expert in every round (offsets 0, 4, 0, 4).
- Per-worker trainable fraction (inference, using the owner's estimate of about 28M expert parameters): (46.05 − 28) + 14 ≈ 32M of 46M, about 70%.

## Papers

### P1. Partial Parameter Updates for Efficient Distributed Training (closest in structure; full text)
- **Authors:** Anastasiia Filippova, Angelos Katharopoulos, David Grangier, Ronan Collobert (Apple). **Year:** 2025.
- **Venue:** the PDF names none ("Date: September 29, 2025"). The raw HTML of `neurips.cc/virtual/2025/poster/124341` lists the paper on the NeurIPS 2025 site; main track or workshop was not determined.
- **arXiv:** 2509.22418, v1 only (26 Sep 2025); read v1 PDF, and the HTML v1 to check Figure 4b. https://arxiv.org/abs/2509.22418. DOI 10.48550/arXiv.2509.22418 (arXiv DOI).
- **Code:** none mentioned in the text.
- **Read status:** full text (main body, Appendices A to D).
- **Setting and scale:**
  - Pretraining from scratch: 1.3B dense GPT-3-XL-style transformer (24 layers, width 2048, vocabulary 32,000) on RedPajama-V2, 1,024-token sequences.
  - K = 32 nodes (one H100 each), per-node batch 16 (global 512). Inner AdamW (0.9, 0.99, wd 0.1), learning rate 3e-4, warm-up 1,500 steps, cosine schedule.
  - Outer optimizer: Nesterov SGD (momentum 0.9, learning rate 0.4) with H = 100, and Streaming-DiLoCo grouping (8 groups of 3 layers) (Sec 3.1).
  - Each node updates a *fixed* slice for the whole run, with a full forward pass. MLP hidden units are split into N slices, and node k trains slice k mod N, so each slice has K/N holders. Attention, embeddings and norms are trained on all nodes. Deltas are averaged element-wise over each parameter's holders (Algorithm 1, Sec 2.2 to 2.2.1).
  - Baseline: Streaming DiLoCo, a full-model method with the same outer optimizer, H, and token and bandwidth budget.
- **Key findings:**
  - **Table 1 (v1), 26B tokens, test PPL** (Streaming DiLoCo 12.75; log-PPL gap against it in brackets):

    | Configuration | Trainable parameters | Test PPL | Log-PPL gap |
    |---|---|---|---|
    | Streaming DiLoCo | all | 12.75 | reference |
    | 1/2 MLPs | 0.87B | 12.24 | −1.6% |
    | 1/4 MLPs | 0.67B | 12.72 | −0.1% |
    | 1/8 MLPs | 0.57B | 13.59 | +2.5% (PPL +6.6%) |
    | 1/16 MLPs | 0.52B | 14.21 | +4.3% (PPL +11.5%) |

  - Combined MLP and attention slicing, at 28B tokens (not token-matched to the 26B baseline): 1/2 MLPs + 1/2 heads gives 12.22; 1/4 MLPs + 1/4 heads gives 12.79.
  - On the 1/8 slicing (each slice on 4 of 32 nodes), it "required almost 50% more tokens to match" (Sec 3.2, "Parameter Slicing"). Trained on 37B tokens, 1/8 MLPs reached 12.68 (Table 1).
  - Figure 4b (values confirmed in the HTML table): DiLoCo 12.78, Streaming DiLoCo 12.75, ours (1/4 MLPs, no streaming) 12.73, ours by slices 13.47, ours by layers 12.72.
  - Summary claim: "despite fewer updates per parameter than full-model baselines, our method achieves comparable perplexity" (Sec 2.2).
  - Slicing the attention output projection W_O degraded results (Sec 2.2.1; Appendix A.2, Fig 5, no number).
  - Horizontal slicing (each node trains MLPs of a subset of *layers*) diverged with gradient explosion (Appendix A.2, Fig 5).
  - Detaching frozen slices from the backward Jacobian failed. At 335M, 1/4 MLPs, keeping one slice in the Jacobian exploded, and keeping one plus one random slice gave PPL 17.38 against 16.44 (Appendix D, Fig 6).
  - Dynamic reassignment was not tried, because it would need "replicating the full optimizer state on every node or transferring optimizer state" (Sec 3.2).
  - Bearing on Q1: low-communication methods needed 1.7× more tokens than DDP to reach validation loss 2.41 (Fig 3 caption).
- **Remedy tags:**
  - [REMEDY | larger slices (fewer slices N; more holders per slice) | partial updates | 1.3B, 32 nodes, H = 100 | pretraining | PPL 14.21 (N = 16), 13.59 (8), 12.72 (4), 12.24 (2) against 12.75 full | Table 1, v1]
  - [REMEDY | extra training tokens for small slices (26B → 37B) | partial updates | same | pretraining | 1/8 MLPs PPL 13.59 → 12.68 (full 12.75 at 26B) | Table 1, Sec 3.2, v1]
  - [REMEDY (negative) | synchronizing slices at different times ("by slices" streaming) | partial updates | same | pretraining | 13.47 against 12.72 by layers | Fig 4b, Appendix A.1, v1]
  - [REMEDY (negative) | horizontal (layer-subset) assignment | partial updates | same | pretraining | diverged (no number) | Appendix A.2, Fig 5, v1]
- **Bears on:** Q3 (central), Q5 (slice size), Q1 (Fig 3).
- **How it differs from ours:**
  - Dense MLP slices, not MoE experts. Every slice is active for every token, while each of our experts sees only the tokens routed to it.
  - 1.3B parameters, sub-word tokens, 26B tokens, against our 46M parameters, characters and about 164M characters.
  - K = 32 against our 4 workers.
  - Nesterov outer optimizer (learning rate 0.4) against our plain averaging.
  - Slices fixed for the whole run against our per-round redraw.
  - Inner AdamW state persists across rounds (not stated otherwise), against our fresh AdamW each round.
- **Question for us:** is our +1.4% driven by the absolute holder count (about 2, like their 1/16 row) or by the holder share and trainable fraction (1/2 and about 70%, like their 1/2 row, which *beat* full averaging)? And does an outer Nesterov step change the sign, as their baseline uses one?

### P2. Model Parallelism With Subnetwork Data Parallelism (SDP) (full text)
- **Authors:** Vaibhav Singh, Zafir Khalid, Pietro Cagnasso, Edouard Oyallon, Eugene Belilovsky. **Year:** 2025 to 2026.
- **Venue:** preprint (the PDF says "Preprint.").
- **arXiv:** 2507.09029, v1 11 Jul 2025, v2 1 Oct 2025, v3 2 Oct 2025, v4 3 Oct 2025, v5 31 May 2026; read v5. https://arxiv.org/abs/2507.09029.
- **Code:** "We shall release code ... at the time of publication" (Sec 4); none found.
- **Read status:** full text of v5, including Appendices A to J.
- **Setting and scale:**
  - LLaMA-style pretraining on FineWeb at 134M, 500M and 1B, with 8 workers, sequence 1024 and 1.05M tokens per step. AdamW (0.9, 0.95), wd 0.1, clip 1.0, cosine schedule. The DDP token budget is Chinchilla (20× parameters) (Sec 4.1, Appendix E).
  - Also ResNet-18, WideResNet-18 and Swin-T on CIFAR.
  - Masks are fixed for the whole run and overlap across workers. **Synchronization is every step** (gradient averaging over holders), so there are no local steps.
  - **FLOP-matched:** iterations scale inversely with the active fraction C, so sub-network runs take more steps than DDP (Sec 4).
  - Two regimes. Backward masking runs the full forward pass and masks the update, which is the analogue of our partial arm. Forward masking drops the parameters from the forward pass too, which is the analogue of our sliced arm.
- **Key findings:**
  - **1B, Table 1 (v5):**

    | Run | C | Validation loss | Gap to DDP |
    |---|---|---|---|
    | DDP | 1.00 | 2.452 | reference |
    | B-SDP | 0.69 | 2.437 | −0.6% |
    | Bb-SDP (backward-masked blocks) | 0.69 | 2.437 | −0.6% |
    | N-SDP | 0.69 | 2.434 | −0.7% |

    Downstream averages: 0.448, 0.457, 0.447 and 0.446. This confirms the prior survey's fetched-summary number.
  - 500M: B-SDP at C = 0.5 reached 2.72 against DDP 2.73 (Sec 4.1).
  - The authors state "convergence quality degrades with reduced overlap" (Sec 2).
  - **Theory (Theorem 3.1, Appendix B):** for backward masking with single-step SGD, the masked average stays unbiased. Its variance term is multiplied by the squared distance of the mask-averaging operator from uniform averaging, ‖(1/n)m_uni − (1/c)m‖²_F. Fewer holders give more variance and no bias.
  - **CIFAR-100, ResNet-18, cosine schedule, Table 4** (layout garbled; values mapped in column order C = 7/8 … 3/8, which agrees with the text's 87.91 and 58.73 at C = 3/8). DDP is 68.62.

    | Variant | C = 7/8 | 6/8 | 5/8 | 4/8 | 3/8 |
    |---|---|---|---|---|---|
    | Bb-SDP (backward) | 67.33 | 64.90 | 61.87 | 59.89 | 58.73 |
    | N-SDP (forward) | 69.02 | 68.42 | 67.69 | 65.20 | 9.79 |

    On CIFAR-10, Bb-SDP at C = 3/8 held 87.91, while N-SDP fell to 22.56 and B-SDP to 42.68 (Table 4; Sec 4.2).
- **Remedy tags:**
  - [REMEDY | backward (full-forward) masking instead of forward masking at low coverage | partial-update / sliced contrast | ResNet-18, 8 workers | vision training from scratch | C = 3/8, CIFAR-10: 87.91 (Bb) against 22.56 (N) and 42.68 (B) | Table 4, v5]
  - [REMEDY | higher coverage C | partial updates | same | vision | Bb-SDP CIFAR-100 from 67.33 (7/8) down to 58.73 (3/8), DDP 68.62 | Table 4, v5]
  - [REMEDY | FLOP-matched extra iterations for sub-networks | partial updates | 1B LLaMA | pretraining | matches or beats DDP at C ≥ 0.5 | Fig 1, Table 1, v5]
- **Bears on:** Q3 (theory and LLM scale), the sliced arm by cross-reference (forward masking).
- **How it differs from ours:** synchronization every step (no H); FLOP-matched rather than step-matched; dense model; fixed masks. Whether Bb-SDP propagates gradients through skipped blocks to earlier layers is not explicit in the text. Sec 1 says backward masking saves "gradients and accumulators", which suggests only parameter gradients are skipped (inference).
- **Question for us:** with H = 1, would our partial arm's cost vanish, as SDP's backward-masking theory suggests (unbiased, variance only)? That would locate the +1.4% in the interaction between partial updates and local steps.

### P3. Towards a Better Theoretical Understanding of Independent Subnetwork Training (IST theory; main body in full)
- **Authors:** Egor Shulgin, Peter Richtárik (KAUST). **Year:** 2023 to 2024.
- **Venue:** ICML 2024 (arXiv comment).
- **arXiv:** 2306.16484, v1 28 Jun 2023, v2 4 Jun 2024; read v2. https://arxiv.org/abs/2306.16484.
- **Code:** none.
- **Read status:** Sections 1 to 6 in full, Appendix C.2 (generalization to smooth losses) and Appendix D (comparison with Yuan et al. and Mohtashami et al.). Appendix B proofs were seen only at heading level.
- **Setting:**
  - Distributed submodel gradient descent (Algorithm 1). The gradient is computed **at the sketched submodel** C_i x and sketched again: g_i = C_i ∇f_i(C_i x) (eq. 5).
  - Permutation sketches, meaning a disjoint partition scaled by n. A quadratic model.
  - **Single local step by assumption** (Sec 2.2, simplification (b)).
  - Experiments: quadratic with d = 1000 and n = 10; a 1-hidden-layer ReLU network on ResNet-50 features (CIFAR-10) with n = 10.
- **Key findings:**
  - With interpolation (b_i = 0) and suitable preconditioning, IST matches gradient descent (Theorems 1 and 3.1 to 3.2).
  - In general the estimator is biased and the method converges to a fixed point different from the optimum (Sec 4.1). Theorem 2 has a neighbourhood term proportional to the bias ‖h‖²_L and to heterogeneity σ², and part of it cannot be removed by shrinking the step size (Sec 4.2).
  - In the homogeneous case the heterogeneity term vanishes but the bias remains (Sec 4.2).
  - For general smooth losses, "IST can converge to the irreducible neighborhood of the stationary point" (Appendix C.2).
  - In the neural-network experiment, IST plateaus at an error floor that a smaller step size does not lower (Fig 2, Sec 5.1).
  - The paper contrasts this with compressed-gradient SGD, which is unbiased when the gradient is taken at the *full* model (Sec 4.2). It sets aside methods that need full-model gradients as "not suitable for our problem setting" (Appendix D).
- **Bears on:** Q3 theory. Its bias mechanism is **forward masking** (gradient at a sparsified model). That maps onto our *sliced* arm (masked routing), not onto the partial-update arm, which runs the full forward pass (inference).
- **How it differs from ours:** quadratic model; disjoint partition (each coordinate on exactly one worker); one local step (we use H = 125); no outer optimizer; no MoE.
- **Question for us:** does the gap between the sliced and partial arms (+3.2%) behave like IST's irreducible neighbourhood, meaning it does not shrink with a smaller learning rate or with more rounds?

### P4. Scaling Language Model Size in Cross-Device Federated Learning (clearest language-model partial-update number)
- **Authors:** Jae Hun Ro, Theresa Breiner, Lara McConnaughey, Mingqing Chen, Ananda Theertha Suresh, Shankar Kumar, Rajiv Mathews (Google). **Year:** 2022.
- **Venue:** the arXiv text names none. A search snippet said FL4NLP 2022; not verified at source.
- **arXiv:** 2204.09715, v1 31 Mar 2022, v2 24 Jun 2022; read v2. https://arxiv.org/abs/2204.09715.
- **Code:** FedJAX is mentioned as the simulation library; no project code was found.
- **Read status:** sections read: abstract, Sec 3 (data and models), Sec 4 "Partial model training", Appendix A (Tables 2 to 3 and hyperparameters), Table 4 and the opening of Appendix B.
- **Setting and scale:**
  - Federated **training from random initialization** on Stack Overflow: 4K sentence-piece vocabulary, maximum sequence length 30.
  - 800 clients per round, 10K rounds, 1 local epoch at batch 16 with at most 1200 sequences per client (so at most 75 local steps).
  - Server optimizer Adam (server learning rate 0.001) (Appendix A, Table 3).
  - Partial Variable Training (PVT) with per-client-per-round (PCPR) random freezing of multiplicative vectors and matrices, full forward pass (Sec 4; Appendix B).
  - Baseline: the same model at 100% trainable under the same FedAvg/FedAdam scheme.
- **Key findings (Table 4, test PPL after 10K rounds):**

  | Model | 100% | 40% trainable | 20% trainable |
  |---|---|---|---|
  | Large Transformer (21.0M) | 29.15 | 30.45 (log-PPL +1.3%, PPL +4.5%) | 32.61 (+3.3%, PPL +11.9%) |
  | Large Conformer (20.2M) | 29.06 | 30.06 (+1.0%) | 31.51 (+2.4%) |
  | Large LSTM (18.8M) | 30.83 | 31.53 (+0.65%) | 32.93 (+1.9%) |

  - "Large LSTM and Conformer seem to be able to handle more aggressive parameter freezing" than the Transformer (Sec 4).
- **Remedy tag:** [REMEDY | larger trainable fraction (20% → 40% → 100%) | partial updates | 21M Transformer, 800 clients per round | pretraining (federated, from scratch) | log-PPL gap +3.3% → +1.3% → 0 | Table 4, v2]
- **Bears on:** Q3 (the closest language-model partial-versus-full contrast under one averaging scheme).
- **How it differs from ours:** cross-device, with 800 clients per round, so each variable has about 320 holders per round at 40% (inference); random masks per client per round; sub-word tokens; dense model; server Adam; short local training.
- **Question for us:** their 40% row (+1.0 to +1.3%) is close to our +1.4% at about 70% trainable. Is our cost per unit of frozen fraction higher because we have 2 holders instead of hundreds?

### P5. Partial Variable Training for Efficient On-Device Federated Learning (PVT)
- **Authors:** Tien-Ju Yang, Dhruv Guliani, Françoise Beaufays, Giovanni Motta (Google). **Year:** 2021 to 2022.
- **Venue:** the PDF shows an IEEE 2021 copyright. The IEEE SPS page for ICASSP 2022 lists the title (raw HTML title tag checked).
- **arXiv:** 2110.05607, v1 only (11 Oct 2021). https://arxiv.org/abs/2110.05607.
- **Code:** none.
- **Read status:** full text except the reference list.
- **Setting:**
  - Speech recognition, trained from scratch on Librispeech (IID and non-IID) with a non-streaming Conformer (size not given in the text read). Domain adaptation with a streaming Conformer of about 137M.
  - 1024 clients, 5 local steps, batch 16.
  - 90% of freezable variables frozen per client per round. Freezable means multiplicative vectors and matrices; additive vectors are always trained. Full forward pass (Sec 2, 3.1).
- **Key findings:**
  - IID Librispeech, word error rate (dev/dev-other/test/test-other): all-variable training 2.1/4.6/2.2/4.8 against PVT 2.1/4.9/2.3/4.8. The table layout is garbled; WERs are mapped in row order, which agrees with the memory and communication figures in the text (Table 2).
  - Non-IID: all-variable 2.0/4.7/2.2/4.9 against PVT 2.1/4.8/2.2/5.0 (Table 3).
  - "PCPR generally attains the highest accuracy given the same number of rounds" (Sec 2.2).
  - The per-round scheme (one mask shared by all clients in a round) "is unable to converge to reasonable WERs within 200K rounds", while PCPR reached 2.4/5.7/2.5/5.7 (Sec 3.4.1, ablation with 1 local step and 128 clients).
  - PVT only, as local steps grow: 1 step gives 2.2/5.5/2.4/5.4 (350K rounds); 5 steps 2.1/4.9/2.2/4.9 (155K); 128 steps 2.0/4.8/2.2/4.6 (15K) (Table 5).
  - PVT only, as clients grow: 128 clients give 2.2/5.5/2.4/5.4; 1024 give 2.1/5.0/2.3/4.9 (Table 6).
- **Remedy tags:**
  - [REMEDY | per-client-per-round random masks rather than one mask per round | partial updates | Conformer, 128 clients | speech, from scratch | per-round scheme did not converge in 200K rounds; PCPR close to all-variable training | Sec 3.4.1, v1]
  - [REMEDY | more local steps | partial updates | same | speech | WER and rounds improve, 1 → 128 steps; no all-variable baseline at each setting | Table 5, v1]
  - [REMEDY | more clients per round | partial updates | same | speech | WER and rounds improve, 128 → 4096 | Table 6, v1]
- **Bears on:** Q3 and Q5 (assignment policy, local steps).
- **How it differs from ours:** speech, not language; very small trainable fraction (10% of freezable variables) offset by about 1024 clients; cross-device. "More clients" adds data per round, unlike our fixed-compute worker count.
- **Question for us:** does our per-round redraw already deliver PVT's per-client-per-round benefit? Would a fixed (static) expert assignment be worse, as PVT's per-round scheme was?

### P6. FedRolex: Model-Heterogeneous Federated Learning with Rolling Sub-Model Extraction
- **Authors:** Samiul Alam, Luyang Liu, Ming Yan, Mi Zhang. **Year:** 2022.
- **Venue:** NeurIPS 2022 (arXiv comment).
- **arXiv:** 2212.01548, v1 3 Dec 2022, v2 20 Jan 2023; read v2. https://arxiv.org/abs/2212.01548.
- **Code:** https://github.com/AIoT-MLSys-Lab/FedRolex (Apache-2.0 per the GitHub API; last push 2024-08-27).
- **Read status:** sections read: 4 (setup), 4.1 to 4.5, Appendices A.3 to A.5, and Appendix A.7 Table 8.
- **Setting:**
  - Stack Overflow next-word prediction with a 3-layer Transformer: vocabulary 10,000, embedding 128, FFN 2048, 8 heads of 12 dimensions.
  - 200 of 342,477 clients per round; non-IID by user; 3 seeds.
  - Client capacities {1, 1/2, 1/4, 1/8, 1/16}, uniform, made by shrinking the attention hidden width.
  - **Forward-masked** sub-models (clients hold only their sub-model).
  - Local epoch 1 (Table 8; the column alignment is partly garbled).
  - Baseline: "homogeneous (largest)", where every client trains the full model.
- **Key findings:**
  - Stack Overflow accuracy (Table 3): FedRolex (rolling) 29.22 ±0.24; HeteroFL (static nested) 27.21 ±0.22; Federated Dropout (random) 23.46 ±0.12; homogeneous smallest 27.32 ±0.12; homogeneous largest 29.79 ±0.32. Relative to largest that is −1.9%, −8.7% and −21.3%.
  - HeteroFL and Federated Dropout "perform even worse than the model homogeneous case using the smallest model" (Sec 4.2).
  - Overlap ablation, vision only: the effect of the window overlap r is "non-linear and inconsistent" (Appendix A.4, Fig 6).
  - Server model larger than all clients (β = 2 to 16): on Stack Overflow the accuracy "has a much smaller drop" as β grows. The figure gives no numbers (Sec 4.4).
- **Remedy tags:**
  - [REMEDY | rolling rather than static or random sub-model extraction | partial updates (forward-masked) | 3-layer Transformer, 200 clients per round | federated LM training | 29.22 against 27.21 against 23.46 (full 29.79) | Table 3, v2]
  - [REMEDY | more overlap between consecutive windows | partial updates | ResNet-18 CIFAR | vision | inconsistent | Appendix A.4, v2]
- **Bears on:** Q3 and Q5 (assignment policy). Its sub-models are forward-masked, so it is closer to our sliced arm than to the partial arm.
- **How it differs from ours:** heterogeneous capacities rather than equal slices; random client sampling; non-IID data; width slicing of a dense model; a small word-level LM.
- **Question for us:** is our coverage redraw closer to "rolling" (all parts trained evenly) or to "random" (uneven) over a 40-round run? The per-expert update-count variance is measurable from our logs.

### P7. HeteroFL: Computation and Communication Efficient Federated Learning for Heterogeneous Clients
- **Authors:** Enmao Diao, Jie Ding, Vahid Tarokh. **Year:** 2020 to 2021.
- **Venue:** ICLR 2021.
- **arXiv:** 2010.01264, v1 3 Oct 2020, v2 19 Feb 2021, v3 14 Dec 2021; read v3. https://arxiv.org/abs/2010.01264.
- **Code:** the repository diaoenmao/HeteroFL-Computation-and-Communication-Efficient-Federated-Learning-for-Heterogeneous-Clients is MIT per the GitHub API (last push 2023-02-27). The PDF text only says "Our code is available here."
- **Read status:** sections read: 3.1 (aggregation), 4 (setup), Table 3, Table 6 (layout garbled).
- **Setting:**
  - WikiText2 **masked** language modelling (15% masking) with a Transformer of up to 19.3M parameters; 100 clients, 10% active per round.
  - Width-nested static sub-models: model 'a' is full and 'b' to 'e' shrink with ratio 0.5. Each parameter is averaged over the clients holding it (Sec 3.1).
  - Tables use the "Dynamic" assignment, in which clients resample their level each round.
- **Key findings (Table 3, perplexity):**

  | Mix | Perplexity | Gap to 'a' |
  |---|---|---|
  | a (all clients full) | 3.37 | reference |
  | a-b-c-d-e | 3.55 | log-PPL +4.3% |
  | a-e (half 'a', half 'e', in expectation) | 3.75 | log-PPL +8.8% |
  | e alone (1.1M) | 7.41 | |

  - Nested static sub-models gave "better results than uniformly sampled subnetworks" (Sec 3.1, no number).
- **Remedy tag:** [REMEDY | nested static sub-models rather than uniformly sampled ones | partial updates (forward-masked) | ≤19.3M Transformer | federated MLM | "better results", no number | Sec 3.1, v3]
- **Bears on:** Q3 (language-model numbers, forward-masked).
- **How it differs from ours:** masked LM at PPL ≈ 3.4, not causal; heterogeneous widths; clients do not hold the full model.
- **Question for us:** none beyond P6; the numbers are mainly a range marker for forward-masked width slicing.

### P8. Expanding the Reach of Federated Learning by Reducing Client Resource Requirements (Federated Dropout)
- **Authors:** Sebastian Caldas, Jakub Konečný, H. Brendan McMahan, Ameet Talwalkar. **Year:** 2018.
- **Venue:** preprint.
- **arXiv:** 1812.07210, v1 18 Dec 2018, v2 8 Jan 2019; read v2. https://arxiv.org/abs/1812.07210.
- **Code:** none.
- **Read status:** sections read: 3.2, 4.1 (setup), 4.3.
- **Setting:** MNIST, CIFAR-10 (all-convolutional) and EMNIST. 10 clients per round (35 for EMNIST), 1 local epoch, batch 10. Forward-masked fixed-size random sub-models: a fixed number of activations or filters dropped per layer.
- **Key findings:**
  - For every model some keep-rate below 1.0 "matches or, in some cases, even improves" final accuracy (Sec 4.3).
  - A keep-rate of 0.75 "seems to work across the board", which is about 43% fewer parameters in the fully connected models.
  - More aggressive rates slow convergence. Results are given only in Fig 4.
- **Bears on:** Q3, historical baseline. FedRolex (P6) shows the random variant losing 21% relative accuracy on Stack Overflow.
- **How it differs from ours:** small vision models; forward masking; random masks.
- **Question for us:** none specific.

### P9. Distributed Learning of (Fully Connected / Deep) Neural Networks using Independent Subnet Training (IST)
- **Authors:** Binhang Yuan, Cameron R. Wolfe, Chen Dun, Yuxin Tang, Anastasios Kyrillidis, Christopher M. Jermaine. **Year:** 2019 to 2022.
- **Title note:** the arXiv listing title says "Deep Neural Networks"; the v7 PDF says "Fully Connected Neural Networks".
- **Venue:** PVLDB 15(8), 2022, DOI 10.14778/3529337.3529343 (from the PDF).
- **arXiv:** 1910.02120, v1 4 Oct 2019, v2 7 Feb 2020, v3 4 Mar 2020, v4 8 Jun 2020, v5 5 Nov 2020, v6 7 Mar 2022, v7 18 Apr 2022; read v7. https://arxiv.org/abs/1910.02120.
- **Code:** https://github.com/BinhangYuan/IST_Release (the PDF links it; the GitHub API shows no licence; last push 2020-12-09).
- **Read status:** sections read: 2.2 (training subnets), 2.3 (summary of the convergence claim), 3.1 and 3.2 (Tables 1 to 3). The theory appendix was not read.
- **Setting:**
  - Neurons of fully connected layers are partitioned **disjointly** over workers (forward-masked). Each worker runs a number of local SGD steps, after which the subnets are re-sampled.
  - Tasks: Google Speech Commands (2-layer and 3-layer FC networks), ResNet-18 on CIFAR-10 (IST on the FC parts), VGG12 on full ImageNet-21k (top-10 accuracy), Amazon-670k. 2, 4 or 8 nodes. Baselines are data parallel and local SGD.
- **Key findings:**
  - Final accuracy with 2 nodes (Table 2):

    | Task | Data parallel | Local SGD | IST |
    |---|---|---|---|
    | Speech 2-layer | 0.7938 | 0.7998 | 0.8153 |
    | Speech 3-layer | 0.7950 | 0.7992 | 0.8327 |
    | CIFAR-10 | 0.9128 | 0.9087 | 0.9102 |
    | Full ImageNet | 0.3688 | 0.3685 | 0.3802 |

  - IST against ensemble (no re-sampling), Table 3: 2-layer 0.82/0.82, 0.79/0.80, 0.76/0.77 at 2, 4 and 8 nodes; 3-layer 0.84/0.74, 0.82/0.71, 0.78/0.70. IST accuracy falls as the node count rises (smaller subnets). Re-sampling matters for deeper networks.
- **Remedy tag:** [REMEDY | re-sampling subnets every few local steps rather than fixed partitions | partial updates (forward-masked) | 3-layer FC, 8192 wide | speech, from scratch | 0.84 against 0.74 at 2 nodes | Table 3, v7]
- **Bears on:** Q3 (worker-count dependence; assignment).
- **How it differs from ours:** shallow FC networks, CPU clusters, disjoint partitions, forward masking.
- **Question for us:** our coverage policy already re-samples each round. Would a fixed assignment (owners never change) cost more, as IST's ensemble baseline did?

### P10. ResIST: Layer-Wise Decomposition of ResNets for Distributed Training
- **Authors:** Chen Dun, Cameron R. Wolfe, Christopher M. Jermaine, Anastasios Kyrillidis. **Year:** 2021 to 2022.
- **Venue:** UAI 2022, PMLR v180 (proceedings page `proceedings.mlr.press/v180/dun22a.html`, raw HTML title checked). The arXiv comment says "pre-print under review".
- **arXiv:** 2107.00961, v1 2 Jul 2021, v2 14 Mar 2022; read v2. https://arxiv.org/abs/2107.00961.
- **Code:** none found in the text.
- **Read status:** sections read: 2.2 to 2.4 (construction and tuning notes), 5 (setup), 6.1 and 6.2 (Tables 2 and 3).
- **Setting:**
  - Pre-activation ResNet-101. Residual blocks are randomly permuted and dealt round-robin to sub-ResNets each round; about 30% of layers are shared. Blocks are averaged over the sub-ResNets that hold them.
  - Local iterations 50 by default, 15 for ImageNet.
  - CIFAR-10/100 with 2, 4 or 8 machines; ImageNet with 2 or 4. Baseline: local SGD with the same synchronization schedule.
- **Key findings:**
  - CIFAR-10, local SGD against ResIST (Table 2): 92.36/91.95 (2 machines), 92.90/92.35 (4), 92.00/91.45 (8).
  - CIFAR-100: 70.67/70.06, 71.51/71.30, 69.64/70.26.
  - ImageNet: 73.32/71.60 (2 machines), 72.66/70.74 (4) (Table 3).
  - The default of 50 local iterations was chosen because fewer did not noticeably improve performance (Sec 2.4, paraphrased). A minimum of 5 blocks per sub-ResNet was found optimal; ImageNet needed a local-SGD warm-up.
- **Remedy tags:**
  - [REMEDY | minimum sub-network depth (shared blocks) | partial updates | ResNet-101 | vision | 5 blocks optimal, no number | Sec 2.4, v2]
  - [REMEDY | full-model local-SGD warm-up | partial updates | ResNet-101 ImageNet | vision | "without a significant performance decrease", no number | Sec 2.4, v2]
- **Bears on:** Q3. This is the cleanest partial-versus-full comparison under the *same* local-SGD scheme with H of 15 to 50, though forward-masked: −0.2 to −0.6 points on CIFAR (+0.6 once), −1.7 to −1.9 points on ImageNet.
- **How it differs from ours:** vision; depth slicing (sub-networks skip blocks); forward masking; SGD with momentum.
- **Question for us:** the cost grows with task difficulty (CIFAR against ImageNet). Does ours grow with model or data scale too?

### P11. TwIST: Rigging the Lottery in Transformers with Independent Subnetwork Training
- **Authors:** Michael Menezes, Barbara Su, Xinze Feng, Yehya Farhat, Hamza Shili, Anastasios Kyrillidis. **Year:** 2025.
- **Venue:** preprint.
- **arXiv:** 2511.03983, v1 only (6 Nov 2025). https://arxiv.org/abs/2511.03983.
- **Code:** none found in the extracted text.
- **Read status:** sections read: 4.1 (implementation: masked and true TwIST), 5 setup, 5.1, 5.2, Tables 1 and 2, Fig 5 heat-map values.
- **Setting:**
  - **Fine-tuning** a pretrained GPT-2 124M for 3 epochs on WikiText-103: Adam at 1e-4, batch 2, 1024 tokens.
  - 4 compute nodes. Repartition every 15 batches. The first two and last two layers are shared. Masked TwIST zeroes the activations of inactive blocks (forward masking).
- **Key findings:**
  - The paper evaluates **randomly extracted subnets** (pruning). It reports no full-model (12/12) perplexity of the TwIST-trained model against DDP. Table 1's "Data Parallelism" columns are post-training pruning of a DDP-trained model.
  - Example: 23.14 PPL against SparseGPT's 31.64 (Table 1; abstract).
  - Attention setting, evaluated with 10 blocks, by number of blocks used in training: 4 → 17.46, 6 → 16.87, 8 → 16.64, 10 → 16.63 (Fig 5).
- **Bears on:** Q3 only weakly. It gives **no partial-versus-full quality number**.
- **How it differs from ours:** fine-tuning, forward masking, pruning objective.
- **Question for us:** none for the cost question.

### P12. FjORD: Fair and Accurate Federated Learning under heterogeneous targets with Ordered Dropout
- **Authors:** Samuel Horváth, Stefanos Laskaridis, Mario Almeida, Ilias Leontiadis, Stylianos I. Venieris, Nicholas D. Lane. **Year:** 2021.
- **Venue:** NeurIPS 2021.
- **arXiv:** 2102.13451, v1 26 Feb 2021, v2 1 Mar 2021, v3 10 May 2021, v4 4 Jun 2021, v5 11 Jan 2022; read v5. https://arxiv.org/abs/2102.13451.
- **Code:** FedRolex states FjORD's code "is not open-source" (FedRolex footnote 4); FjORD itself says it was built on Flower.
- **Read status:** sections read: 3.5, 5 (setup and Table 1), 5.2, 5.3.
- **Setting:** ordered (nested) dropout. CIFAR-10 ResNet-18; FEMNIST CNN; **Shakespeare character-level** 2-layer LSTM with 715 clients. Baselines are extended Federated Dropout (eFD) and FjORD with eFD.
- **Key findings:**
  - FjORD beats eFD by 0.01 to 0.82 points of (negative) perplexity on Shakespeare, and beats the best eFD model by 0.13 (Sec 5.2).
  - Knowledge distillation adds 0.10 on Shakespeare (Sec 5.3).
  - Centralized, ordered dropout is "very close" to separately trained sub-models of each width (Sec 3.5, Fig 3).
  - No comparison with full-model FedAvg was found in the sections read.
- **Remedy tag:** [REMEDY | self-distillation from larger to smaller nested sub-models | partial updates (nested) | small LSTM | char-level federated training | +0.10 negative perplexity, Shakespeare | Sec 5.3, v5]
- **Bears on:** Q3 only indirectly (the only character-level LM in this strand).
- **How it differs from ours:** nested widths, forward masking, tiny model.
- **Question for us:** none for the cost question.

### P13. NeFL: Nested Model Scaling for Federated Learning with System Heterogeneous Clients
- **Authors:** Honggu Kang, Seohyeon Cha, Jinwoo Shin, Jongmyeong Lee, Joonhyuk Kang. **Year:** 2023 to 2024.
- **Venue:** the PDF header reads IEEE Transactions on Mobile Computing, 2024, with volume "X".
- **arXiv:** 2308.07761, v1 15 Aug 2023, v2 9 Oct 2023, v3 10 Sep 2024; read v3. https://arxiv.org/abs/2308.07761.
- **Code:** project page https://honggkang.github.io/nefl (cited in the PDF; not opened).
- **Read status:** sections read: Table III, Sec V-A3/A4 (heterogeneity and training details), Sec V-B1.
- **Setting:** vision only (CIFAR-10/100, CINIC-10, SVHN, ResNet-18/34; also ViT). 100 clients, 10% per round, E = 5 local epochs. Five nested sub-models with γ from 0.2 to 1.
- **Key findings:**
  - Table III compares the worst-case and average sub-model across methods. ResNet-18, CIFAR-10 worst/average: NeFL 86.86/87.88, FjORD 85.12/87.32, HeteroFL 80.62/84.26, DepthFL 64.80/82.44, ScaleFL 79.47/85.18.
  - No full-model FedAvg baseline appears in the sections read.
  - Depth-scaling methods (DepthFL, ScaleFL) "struggled with convergence issues" in the worst case (Sec V-B1).
- **Bears on:** Q3 only marginally; no cost against full training.
- **Question for us:** none.

### P14. ScaleFL: Resource-Adaptive Federated Learning with Heterogeneous Clients
- **Authors:** Fatih Ilhan, Gong Su, Ling Liu. **Year:** 2023.
- **Venue:** CVPR 2023, pp. 24532 to 24541 per the CVF page. No arXiv version was found.
- **Source read:** CVF open-access PDF (`openaccess.thecvf.com/.../Ilhan_ScaleFL_..._CVPR_2023_paper.pdf`).
- **Code:** https://github.com/git-disl/scale-fl (no licence per the GitHub API; last push 2025-12-11).
- **Read status:** sections read: abstract, 4.1 to 4.5, Tables 3 to 5.
- **Setting:** width and depth scaling with early exits and self-distillation. CIFAR, ImageNet, and **BERT fine-tuning** on SST-2 and AgNews. 5 local epochs.
- **Key findings:**
  - The "FedAVG" baseline trains the *smallest* model on all clients, not the full model. No full-model upper bound is reported in Tables 3 to 5.
  - The "drop below 2%" claim concerns inference with smaller local models (abstract; Sec 1), not the training cost of the global model.
- **Bears on:** Q3: no usable number.
- **Question for us:** none.

### P15. No One Left Behind: Inclusive Federated Learning over Heterogeneous Devices (InclusiveFL)
- **Authors:** Ruixuan Liu, Fangzhao Wu, Chuhan Wu, Yanlin Wang, Lingjuan Lyu, Hong Chen, Xing Xie. **Year:** 2022.
- **Venue:** KDD 2022, DOI 10.1145/3534678.3539086.
- **arXiv:** 2202.08036, v1 16 Feb 2022, v2 17 Jul 2022; read v2. https://arxiv.org/abs/2202.08036.
- **Code:** none found.
- **Read status:** sections read: 4 (setup and baselines), Tables 2 and 3.
- **Setting:** **fine-tuning** RoBERTa (12 layers) on GLUE, with weak, medium and strong clients holding 4, 8 and 12 layers. 1000 clients, 2% per round, FedAdam.
- **Key findings:** GLUE average (Table 2): AllLarge (everyone trains the full model) 85.72; InclusiveFL (depth sub-models plus momentum distillation) 83.15; ExclusiveFL 79.98; AllSmall 74.29; HeteroFL (width sub-models) 53.28, with CoLA at 8.15 and MNLI at 31.83.
- **Remedy tag:** [REMEDY | depth sub-models plus momentum distillation instead of width slicing | partial updates (forward-masked) | RoBERTa-base | fine-tuning | 83.15 against 53.28 (full 85.72) | Table 2, v2]
- **Bears on:** Q3 (a warning that width slicing of a *pretrained* transformer can collapse). It does not transfer to from-scratch pretraining.
- **Question for us:** none.

### P16. Every Parameter Matters: Ensuring the Convergence of Federated Learning with Dynamic Heterogeneous Models Reduction
- **Authors:** Hanhan Zhou, Tian Lan, Guru Venkataramani, Wenbo Ding. **Year:** 2023.
- **Venue:** NeurIPS 2023 (PDF).
- **arXiv:** 2310.08670, v1 12 Oct 2023, v2 26 Oct 2023; read v2. https://arxiv.org/abs/2310.08670.
- **Code:** the PDF says "Link anonymized, see supplementary materials"; not found.
- **Read status:** sections read: 4.2 and 4.3 (algorithm, assumptions, Theorems 1 and 2), 5 (interpretation), 6 (setup and discussion). Table 1's PDF layout is too garbled to map, so no numbers are taken from it.
- **Setting:**
  - Theory for FL in which client n trains θ ⊙ m_{q,n} (pruned or extracted local model) for T local steps. Each parameter is averaged over the clients whose mask contains it (eq. 3), which is our holder-averaging rule.
  - Assumptions: a "model reduction noise" bound ‖θ − θ⊙m‖² ≤ δ²‖θ‖², bounded gradients, and IID or non-IID gradient noise.
- **Key findings:**
  - Theorem 1 (IID): with minimum coverage index Γ_min ≥ 1, the method converges to a neighbourhood of a stationary point of standard FL. The optimality gap is proportional to δ² times the average model norm, and the constants and gap fall as Γ_min rises (Sec 4.3, 5).
  - Theorem 2 (non-IID): Γ_min "no longer plays a role in the optimality gap" (Sec 5).
  - "increasing local epochs or communication rounds cannot mitigate such noise" (Sec 6.2).
  - Experiments that raise Γ_min ("optimized") improved accuracy "on almost all" settings (Sec 6.2). These are MNIST MLP and CIFAR WideResNet with 100 clients.
- **Bears on:** Q3 theory (coverage and holder count).
- **How it differs from ours:** forward masking (θ⊙m zeroes frozen weights). For our partial arm the analogue of δ would be zero, because frozen weights keep their values (inference). The theory assumes bounded gradients and is vision-validated.
- **Question for us:** our per-round Γ_min is 1 under coverage (about 30% of experts have one holder) and 2 under rolling. Does rolling lower the partial cost?

### P17. Masked Training of Neural Networks with Partial Gradients
- **Authors:** Amirkeivan Mohtashami, Martin Jaggi, Sebastian U. Stich. **Year:** 2021 to 2022.
- **Venue:** AISTATS 2022.
- **arXiv:** 2106.08895, v1 16 Jun 2021, v2 8 Nov 2021, v3 22 Mar 2022; read v3. https://arxiv.org/abs/2106.08895.
- **Code:** none.
- **Read status:** sections read: 3.1 to 3.3 (partial SGD, assumptions, Theorem 1, Criteria 1 to 3, the model-parallel/IST paragraph).
- **Setting:** serial "partial SGD", where a mask restricts the update and an optional perturbation changes where the gradient is evaluated.
- **Key findings:**
  - With **no perturbation** (full forward, masked update, which is our partial arm per step), gradient alignment and similarity hold automatically (c_sim = c_align = 1). Convergence then depends only on gradient-norm preservation, ‖∇f‖ / ‖p⊙∇f‖ (Sec 3.3, Criteria 1 to 3).
  - IST maps onto the framework only because disjoint partitions make parallel and interleaved steps identical (Sec 3.3, "Model-Parallel Training").
  - Shulgin and Richtárik (P3, Appendix D) argue that its bounded-perturbation assumption can fail even for quadratics.
- **Bears on:** Q3 theory (partial updates without forward masking are the benign case per step).
- **How it differs from ours:** serial, with no averaging of overlapping workers and no local-step drift.
- **Question for us:** none beyond P2.

## Synthesis for question 3

**1. Which published comparisons are closest to our contrast** (partial against full under the same local-averaging scheme; the worker holds the full model and runs the full forward pass):
- **Filippova et al. 2025 (P1):** 1.3B pretraining, H = 100, partial against Streaming DiLoCo, token-matched. The only result with *local steps, full forward and LM pretraining* together.
- **Ro et al. 2022 (P4):** 21M LM trained from scratch, PCPR partial against 100% under one FedAvg/FedAdam scheme.
- **PVT (P5):** speech, the same contrast.
- **SDP backward masking (P2):** full forward and LM pretraining, but synchronized every step and FLOP-matched, so it isolates the per-step effect without H.
- Forward-masked comparisons are structurally closer to our *sliced* arm. Of these, ResIST against local SGD (P10) and FedRolex/HeteroFL against homogeneous-largest (P6, P7) are the cleanest.
- No paper found compares partial against full expert updates in an MoE under the same local-averaging scheme other than SPES, which is excluded from this strand. Not found in this search.

**2. Reported cost against full-model training (same averaging scheme), with settings:**

| Paper | Setting | Partial configuration | Cost against full |
|---|---|---|---|
| P1 Filippova | 1.3B dense, 32 nodes, H = 100, Nesterov outer, 26B tokens, pretraining | 1/2, 1/4, 1/8, 1/16 MLP slices | log-PPL −1.6%, −0.1%, +2.5%, +4.3% |
| P4 Ro | 21M Transformer, 800 clients per round, ≤75 local steps, from scratch | 40% / 20% trainable (PCPR) | +1.3% / +3.3% (Conformer +1.0 / +2.4; LSTM +0.65 / +1.9) |
| P5 PVT | Conformer speech, 1024 clients, 5 local steps | 10% of freezable variables | WER test-other 4.8 against 4.8 IID; 5.0 against 4.9 non-IID |
| P2 SDP, Bb-SDP (backward-masked, the analogue of our arm) | 1B LLaMA, 8 workers, per-step sync, FLOP-matched (partial gets more steps) | C = 0.69 | loss −0.6% (2.437 against 2.452) |
| P2 SDP, B-SDP and N-SDP (forward-masked) | 500M and 1B LLaMA, same | C = 0.5 (500M), 0.69 (1B) | loss −0.4% (500M B-SDP); −0.6% and −0.7% (1B) |
| P2 SDP, Bb-SDP (backward-masked) | ResNet-18 CIFAR, 8 workers, per-step sync, FLOP-matched | C = 4/8 (each block on about 4 of 8 workers) | CIFAR-10 88.80 against 92.45; CIFAR-100 59.89 against 68.62 |
| P10 ResIST (forward-masked) | ResNet-101, 2 to 8 machines, H = 15 to 50 | depth sub-networks | CIFAR −0.2 to −0.6 points (once +0.6); ImageNet −1.7 to −1.9 points |
| P6 FedRolex (forward-masked) | 3-layer Transformer LM, 200 clients per round | capacities 1 to 1/16 | accuracy −1.9% rolling, −8.7% static, −21% random |
| P7 HeteroFL (forward-masked) | ≤19.3M masked LM | mixed widths | log-PPL +4.3% to +8.8% |

**3. Where our +1.4% sits.** It depends on which axis is held fixed. The literature does not separate the axes, because in Filippova's Table 1 trainable fraction and holder count move together.

| | Trainable fraction per worker | Holders per updated block | Holders / workers | Gap against full |
|---|---|---|---|---|
| P1 1/2 MLPs | 0.87/1.3 ≈ 67% | 16 | 1/2 | −1.6% |
| P1 1/4 MLPs | ≈ 52% | 8 | 1/4 | −0.1% |
| P1 1/8 MLPs | ≈ 44% | 4 | 1/8 | +2.5% (closed with 37B against 26B tokens) |
| P1 1/16 MLPs | ≈ 40% | 2 | 1/16 | +4.3% |
| P4 40% (PCPR) | 40% | ≈ 320 of 800 (inference) | ≈ 0.4 | +1.0 to +1.3% |
| P2 Bb-SDP 1B, C = 0.69 (H = 1, FLOP-matched) | ≈ 69% | ≈ 5.5 of 8 (inference from balanced masks) | ≈ 0.69 | −0.6% loss |
| P2 Bb-SDP CIFAR, C = 4/8 (H = 1, FLOP-matched) | 50% of blocks | ≈ 4 of 8 | 1/2 | −3.7 points (CIFAR-10), −8.7 points (CIFAR-100) accuracy |
| **Ours (partial arm)** | **≈ 70% (inference)** | **mean 2; 1 to 4 per round (inference from code)** | **1/2 (shared part 4/4)** | **+1.4%** |

- On trainable fraction and holder share, we match Filippova's 1/2 row, where partial updates *beat* full averaging. By that comparison our +1.4% is **above** the reported range.
- On absolute holder count (about 2), we match the 1/16 row (+4.3%), which puts us **below** it.
- Against Ro's 40% row (+1.0 to +1.3%) we are **inside or slightly above** the range, despite training a larger fraction (inference).
- Overall: a cost of 1 to 2% for partial updates of a few tens of percent of parameters is consistent with the language-model literature, and it can shrink to zero or become negative with many holders, an outer optimizer, or more compute. The sign and size are not robust across settings.

**4. Dependence on the fraction updated.**
- Monotone within each paper: Ro (100% > 40% > 20%), Filippova (more slices, worse), SDP CIFAR (Bb-SDP falls from C = 7/8 to 3/8), IST (more nodes and smaller subnets, lower accuracy, Table 3).
- Filippova shows the curve need not start at zero: mild slicing *improved* perplexity.

**5. Overlap, coverage and holder count.**
- SDP's Theorem 3.1 (backward masking, per step) gives no bias; variance grows with the distance from uniform averaging, so fewer holders mean more variance. The authors also state that quality degrades with reduced overlap.
- Every Parameter Matters (P16) gives a gap that falls with minimum coverage Γ_min under IID data, but its bias term comes from forward masking.
- FedRolex's overlap ablation is inconsistent (vision).
- (Inference) For our arm the theory points to *variance* from averaging an expert over about 2 rather than 4 trajectories (sometimes 1), and to half the tokens per expert, not to bias.

**6. Worker count.**
- IST loses accuracy as nodes rise (forward-masked, disjoint partitions, so the subnet shrinks).
- ResIST shows no consistent trend from 2 to 8.
- PVT improves with more clients, but in cross-device settings more clients means more data per round, which does not correspond to our fixed-compute worker count (inference).
- No paper varies the worker count at fixed total compute and fixed holder share for partial updates. Gap.

**7. Local steps.**
- PVT improves with more local steps (no full baseline at each setting).
- ResIST: fewer than 50 local iterations did not help.
- Every Parameter Matters: more local epochs cannot remove reduction noise.
- IST theory assumes one step.
- **No paper measures how the partial-versus-full gap changes with H** at matched compute. SDP (H = 1, about −0.6%) against Filippova (H = 100, −1.6% to +4.3%) and ours (H = 125, +1.4%) hints that H matters, but the settings differ in everything else (inference).

**8. Assignment policy.**
- Rolling beats static nested, which beats random, on Stack Overflow (FedRolex, forward-masked, heterogeneous capacities).
- Per-client-per-round random masks beat one mask per round (PVT, which failed to converge with the latter).
- Re-sampling beats a fixed partition for deeper FC networks (IST).
- Fixed overlapping slices work at 1.3B (Filippova) and 1B (SDP).
- (Inference) FedRolex's penalty for static and random extraction comes from nested capacities in which some parameters are rarely or never trained. Our coverage policy trains every expert every round, so that penalty probably does not transfer.
- Filippova rejects dynamic reassignment because of optimizer-state transfer. Our fresh AdamW each round removes that cost, so rolling against coverage against fixed is cheap to test.

**9. What theory says (IST and related).**
- Forward-masked submodel training (gradient at C x: IST theory, Every Parameter Matters) has a bias. It converges to an irreducible neighbourhood that step-size decay does not remove (Shulgin and Richtárik, Theorem 2 and Appendix C.2).
- Backward-masked (full forward) partial updates are unbiased per step and pay only variance (SDP Theorem 3.1; Mohtashami Criteria 2 and 3 hold trivially).
- None of these analyses covers many local steps of backward-masked training. There, frozen experts become stale relative to a shared part and router that keep moving for 125 steps; that interaction is not analysed (inference).
- Cross-reference for Q2 (inference): the forward-masked bias results are the theory closest to our *masked-routing* step (+3.2%). Filippova's Appendix D failure when frozen slices are cut out of the backward Jacobian is related, but it is not the same intervention.

**10. Where papers disagree.**
- Partial training sometimes *beats* full training: Filippova 1/2 slicing, SDP at 500M and 1B, IST Table 2, N-SDP on CIFAR, and Federated Dropout "even improves".
- Elsewhere it consistently costs: Ro, ResIST, FedRolex, HeteroFL, InclusiveFL.
- Candidate explanations stated by the papers are FLOP matching (SDP), regularization and ensemble effects (SDP Sec 4.2; Federated Dropout), and the outer optimizer and scale (Filippova does not explain the improvement). Not resolved.
- The strongest evidence, from within a single paper, that the cost depends on scale and task is SDP. The same backward-masked regime costs nothing at 1B LLaMA (C = 0.69, −0.6% loss). On CIFAR at C = 4/8 it costs 3.7 points (CIFAR-10, 88.80 against 92.45) and 8.7 points (CIFAR-100, 59.89 against 68.62), even with extra FLOP-matched steps (P2, Table 1 and Table 4, v5).

**11. Transfer to our setting.**
- Almost every result is dense; most are vision, fine-tuning, or cross-device FL with tiny per-client steps.
- Only Filippova and SDP are LM pretraining above 100M; neither is character-level or MoE.
- The only character-level LM (FjORD's Shakespeare) has no full-model baseline in the sections read.
- Findings may not transfer to 46M character-level MoE pretraining with 4 workers and plain averaging.

## Candidates for the joint reading list
1. **Filippova et al. 2025, "Partial Parameter Updates for Efficient Distributed Training" (2509.22418).** The only partial-against-full comparison with local steps in LM pretraining. It maps directly onto our partial arm and has a slice-size dose-response. **Foundational for Q3; read early.**
2. **Singh et al., SDP (2507.09029 v5).** Separates backward from forward masking in theory (unbiased plus variance) and at 1B, which is the frame needed to keep the partial (+1.4%) and masked-routing (+3.2%) steps apart. **Foundational; read early.**
3. **Shulgin and Richtárik, IST theory (2306.16484).** The irreducible-neighbourhood result for gradients taken at a sub-model. Bears mainly on the sliced arm and is useful as the contrast case. **Specific; read after 2.**
4. **Ro et al. (2204.09715).** The cleanest small-LM numbers for partial against full under one averaging scheme (Table 4). **Specific; read later; short.**
5. **FedRolex (2212.01548).** Assignment-policy evidence on an LM (rolling against static against random). Optional if the list is tight. **Specific; read later.**

## Gaps
Questions no paper answers that the existing harness could answer:
1. **Separate holder count from trainable fraction** (the main ambiguity in Synthesis 3).
   - 8 workers × capacity 4 keeps the fraction at 70% and doubles holders to about 4.
   - 4 workers × capacity 2 keeps about 1 holder and lowers the fraction.
   - 4 workers × capacity 6 gives about 3 holders.
2. **Coverage against rolling against a fixed assignment at Task B.** Rolling gives exactly 2 holders per expert per round; coverage gives 1 to 4. This tests the holder-count variance (SDP Theorem 3.1, Every Parameter Matters) and the static-against-dynamic question (PVT, IST) at no optimizer-state cost.
3. **H sweep for partial against full** (for example H = 1, 25, 125 and 500 at equal total steps). Does the partial cost vanish at H = 1, as SDP's backward-masking theory suggests, and grow with staleness?
4. **Nesterov outer momentum** in both partial and full arms. Does the gap shrink or flip sign, as with Filippova's outer-optimizer baseline?
5. **Compute-matched against step-matched.** Give the partial arm the extra steps its skipped expert gradients would buy (SDP accounting), and test whether more training closes the gap (Filippova's 1/8 overtraining).
6. **Per-expert diagnosis.** Correlate each expert's cumulative holder count and token count with its final usage and quality, from existing logs, to see whether rarely held experts drive the cost.
7. **Skewed data.** Every Parameter Matters predicts coverage stops helping under non-IID data; does the partial cost grow under skew?

## Could not verify
- **DepthFL** (Kim et al., ICLR 2023, OpenReview forum pf8RIZTMU58): `curl https://openreview.net/pdf?id=pf8RIZTMU58` returned HTML with HTTP 403, and the arXiv API title search `ti:DepthFL` returned no entries. Not read; no numbers recorded. The ID 2303.04887 that came up in a DepthFL search is titled "Memory-adaptive Depth-wise Heterogeneous Federated Learning", a different paper (not opened).
- **Venue of Ro et al. (FL4NLP 2022):** search snippet only.
- **Filippova et al.:** the NeurIPS 2025 listing was confirmed only as a page title on neurips.cc; main track or workshop not determined. No code found.
- **TwIST, Every Parameter Matters, NeFL code links:** anonymous or supplementary links not found or not opened.
- **Prior-survey claim that TwIST used "4 P100 workers":** P100 not seen in the sections read (4 compute nodes confirmed).
- **Not opened** (cited by papers read, or seen only in listings):
  - MAST, Demidovich et al. (2311.16086)
  - Liao and Kyrillidis (TMLR 2022)
  - AsyncDrop, Dun et al. (AISTATS 2023)
  - Beton et al., sparse parameter averaging (ICLR 2025 workshop)
  - HtFLlib (2506.03954)
  - GASLoC (2606.11081)
  - "Towards Opportunistic Federated Learning Using Independent Subnetwork Training" (2024; OpenAlex title only)
  - "Submodel Partitioning in Hierarchical Federated Learning" (2024; OpenAlex title only)
  - FedPT, partially trainable networks (2110.03450; snippet only)
  - EST (2406.06962) and RaPTr (2402.05913): centralized, out of scope
- **Our holder-count distribution (1 to 4 per round)** is derived by reading `assignment.py`, not by running it. Python failed to start in this session ("Permission denied" and "The specified disk or diskette cannot be accessed").

## Query log
All times are TST (`date`), 2026-10-11.

| Time | Action |
|---|---|
| 10:28:48 | Session start; read the brief, `docs/prior-work.md` and the Task B rows of `docs/stage0-report.md` |
| 10:29:49 | arXiv API `export.arxiv.org/api/query?id_list=` for 9 named IDs (all verified) |
| ≈10:30 | WebSearch, 5 queries: (1) "Partial Parameter Updates for Efficient Distributed Training arXiv"; (2) "ResIST layer-wise decomposition ResNets distributed training arXiv"; (3) "NeFL nested model scaling federated learning arXiv"; (4) "ScaleFL resource-adaptive federated learning heterogeneous clients CVPR 2023"; (5) "DepthFL depthwise federated learning heterogeneous clients ICLR 2023" |
| ≈10:30 | WebSearch, 5 queries: (6) "Partial Variable Training on-device federated learning freeze variables"; (7) "Every parameter matters convergence federated learning dynamic heterogeneous model reduction coverage index"; (8) "masked training of neural networks with partial gradients convergence"; (9) "independent subnetwork training large language model pretraining 2025 2026"; (10) "sub-model federated learning language model perplexity rolling extraction 2024" |
| ≈10:30 | WebSearch, 3 queries: (11, extended) "low-communication training each worker updates subset of parameters frozen remainder language model 2026"; (12) "model-heterogeneous federated learning benchmark HeteroFL FedRolex language model 2025"; (13) "Scaling Language Model Size in Cross-Device Federated Learning partial model training Stack Overflow" |
| 10:31:00 | `curl` of 16 arXiv PDFs (sleep 3 s between; all HTTP 200); `pdftotext -layout`; CVF ScaleFL PDF (200); OpenReview DepthFL (403) |
| ≈10:32 to 10:33 | 16 arXiv abs pages for version histories (sleep 3 s) |
| 10:39:54 | OpenAlex: IDs for 2509.22418, 2507.09029, 2306.16484, 2212.01548, 2310.08670; citing-works queries for FedRolex (2024 to 2026), Every Parameter Matters and IST theory (OpenAlex listed 0 citers for Filippova and SDP) |
| ≈10:40 to 10:41 | WebSearch: (14, extended) "arXiv 2026 distributed pretraining each node trains subset of parameters frozen local steps perplexity versus DiLoCo"; (15) "federated sub-model training language model pretraining from scratch perplexity gap full model 2025" |
| ≈10:41 | arXiv HTML v1 of 2509.22418 (Figure 4b table check) |
| 10:43:00 | GitHub API `repos/` for AIoT-MLSys-Lab/FedRolex, BinhangYuan/IST_Release, git-disl/scale-fl and the HeteroFL repo |
| 10:46:26 | arXiv API `search_query=ti:DepthFL`; raw HTML of the neurips.cc 2025 poster page (Filippova), the PMLR v180 page (ResIST) and the IEEE SPS ICASSP 2022 page (PVT) |
| (no time) | Read repository files (no changes): `cassandra_chorus/coordinator/assignment.py`, `configs/queues/task_b_matrix.toml`, `configs/task_b/sliced.toml` |

**Not covered:**
- DepthFL full text.
- NeFL beyond Table III and setup; FjORD appendices.
- Theory appendices of IST (Yuan et al.) and of Every Parameter Matters; proofs in Shulgin and Richtárik Appendix B.
- HtFLlib benchmark; LLM federated fine-tuning with layer subsets (for example FedRA); AsyncDrop; MAST.
- GitHub code search (the GitHub MCP connector failed to connect; the unauthenticated REST API was used for metadata only).
- Semantic Scholar (not tried; OpenAlex used instead, with thin coverage of 2025 to 2026 arXiv preprints).
- No 2026 follow-up to Filippova et al. was found.
- Chinese-language venues.
