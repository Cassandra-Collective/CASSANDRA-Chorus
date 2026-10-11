# Round 2: forward citations of the six closest papers, routing to non-held experts, and a FoMoE check
> Correction (2026-10-11, coordinator): our experts are SwiGLU with three matrices, so expert parameters are 42.47M of 46.05M (92%), about 14.2M are active per token, and a partial-arm worker trains about 54%. Figures in this file based on two-matrix experts (about 10M active, about 28M expert parameters, about 61% or 70%) are wrong; see the report's header.

| | |
|---|---|
| Date | 2026-10-11, 11:00 to 11:23 local machine time ("TST"), from the `date` command |
| Scope | (a) Papers citing FoMoE (2606.19025), Gating Dropout (2205.14336), MaskMoE (2407.09816), HARC (2606.03391), FedAlign-MoE (2603.21276) and DDOME / FedJETs (2306.08586), classified on our four axes. (b) Evidence on routing a fraction of tokens to experts a worker does not hold. (c) A source check of FoMoE. |
| Read first | `docs/research/2026-10-11-deep-research-prompt.md` (in full) and round-1 notes 02a, 02b, 04a and 04b (skimmed for duplicates and "Could not verify" leads). |
| Method | Citation lists from the OpenAlex `cites:` filter and the Semantic Scholar citations endpoint. Discovery through 20 arXiv API queries, 6 WebSearch queries and the GitHub repository-search API. Papers fetched as arXiv PDF, converted with `pdftotext -layout`, and read from that raw text. FoMoE tables were parsed from the arXiv HTML of v1 and v2 with a local script. No number below comes from a search snippet; WebFetch was not used. |
| Conventions | "(inference)" marks my reasoning, not a paper's claim. Locators give section, table or figure, and version. Quotes are under 15 words. |

**Our setting** (from the brief, with the caller's correction):

- **Slices:** each worker holds the shared part plus 4 of 8 experts per layer.
- **Routing:** a top-2 softmax over the 4 held experts during local training (renormalized over the chosen 2), and over all 8 after the merge.
- **Slice policy:** the "coverage" policy redraws slices every round. Each expert has 1 holder about 30% of the time, 2 about 44%, 3 about 22% and 4 about 4% (mean 2).
- **Merge:** holder-only averaging of experts and their router rows; plain averaging; a fresh AdamW every round.
- **Run:** IID data, N = 4, H = 125, 40 rounds, 46.05M parameters, text8 characters.
- **Gaps to centralized (test bpc):** full averaging +6.1%, partial update +7.6%, sliced +10.8%.

---

## FoMoE check

**Paper.** "FoMoE: Breaking the Full-Replica Barrier with a Federation of MoEs".
- **Authors:** Lorenzo Sani, Zeyu Cao, Meghdad Kurmanji, Alex Iacob, Andrej Jovanović, Yan Gao, Wanru Zhao, Nicholas D. Lane (Cambridge ML Systems Lab; Flower Labs).
- **Links:** https://arxiv.org/abs/2606.19025 and DOI 10.48550/arXiv.2606.19025 (OpenAlex W7165168211).

### 1. Version history and venue

**Versions.** From the arXiv abs page, fetched 11:05:
- v1: Wed 17 Jun 2026 12:50:07 UTC (424 KB).
- v2: Sat 20 Jun 2026 12:18:17 UTC (424 KB).
- No later version as of 2026-10-11.

**Venue.** "Preprint." (v2 page 1 footer). No venue is given in either version.

**Read status.**
- v2: full text from the PDF (main text and Appendices A to G; references skimmed). Tables 1 and 3 to 7 were re-read from the v2 HTML because the PDF text interleaves rows.
- v1: abstract, §5 and §6.1 to §6.3 read from the PDF and HTML text. All v1 table cells were compared with v2 by script.

**What changed from v1 to v2.**
- **Numbers.** All 126 "mean ± spread" cells are identical in v1 and v2 (script diff of the HTML tables).
- **Table numbering.**
  - v1's O_e table was Table 7 and its DiLoCo full-replica table was Table 6.
  - v2 renumbers them as Tables 3 to 6; its Table 7 is the reproducibility summary.
  - The reproducibility appendix moves from "Section D" (v1) to "Sec. F" (v2).
- **Abstract.**
  - v1 calls skip-token "a novel 'skip-token' mechanism".
  - v2 drops "novel" and adds that FoMoE skips "non-resident experts during local training".
- **Centralized claim (§6.1).**
  - v1 says LocalAdamW "enables FoMoE to match centralized baseline performance" (v1 §6.1).
  - v2 softens this: LocalAdamW "tracks the centralized quality reference more closely than DiLoCo" (v2 §6.1).
  - Neither version gives a number.
- **Overlap conclusion (§6.2).**
  - v1: "choosing Oe≈4 ensures a Pareto-optimal trade-off in our studied setting".
  - v2: "Oe≈4 yields the configurations that best balance quality against these costs".
  - In both versions the symbol is ≈ (from the HTML). Round-1 note 04b's "O_e ≥ 4" misreads it; 04a's "≈ 4" is correct.
- **How the spread is described (§5).**
  - v1: "we report perplexity achieved across the entire dataset".
  - v2: "mean and standard deviation of evaluation perplexity across the dataset".
  - Both versions keep the Table 7 sentence that the deviations are "computed across runs with different seeds".

### 2. Centralized (single-machine) baseline

There is **no centralized number in either version.**
- "Centralized" appears only as a legend entry in Fig. 5. v2 §6.1 calls it "a quality reference and not a practical baseline".
- App. C, Fig. 13 plots learning-rate sweeps for "centralized (local step size of one)" runs. These values are in the figure only.
- App. C states that centralized baselines were tuned over η ∈ {0.01, 0.02, 0.03, 0.04, 0.07} and that η ≈ 0.01 was best everywhere. No perplexity value is given.
- So FoMoE's cost against centralized training cannot be read from the text. Only its cost against full replication can, as round 1 said; this is now reconfirmed for v1 as well.

### 3. What the "±" values mean

- v2 §5 says "across the dataset", while v2 App. F, Table 7 (and v1's Table 7) says "across runs with different seeds". The paper contradicts itself.
- **Arithmetic (inference).** I divided the spread by the mean in all 126 cells. The ratio runs from 0.126 to 0.157, with a mean of 0.138. That includes the diverged DiLoCo cells (647.11 ± 94.47 gives 0.146; 748.52 ± 105.02 gives 0.140).
- **Interpretation (inference).**
  - A spread over three seeds is unlikely to stay at about 14% of the mean in every configuration, diverged runs included.
  - A near-constant ratio is what a per-sample spread (per document or per evaluation batch) would produce.
  - So the "±" most likely describes the dataset, not the seeds. **Table 6 then carries no seed uncertainty at all**, and differences of a few perplexity points between cells cannot be judged against run-to-run noise.

### 4. Optimizer-state handling and LocalAdamW

**Local state (§3.4, v2).**
- Local optimizer states are "preserved rather than reset".
- For dense parameters, every worker tracks state.
- For experts, "workers maintain history only for their own experts".

**Under random placement (§3.4).**
- Optimizers are reinitialized for reassigned experts, with a learning-rate warm-up applied only to the reassigned weights.
- The paper says preserving local momentum "prevents the divergence observed in stateless approaches". No number, table or figure supports this claim (v1 and v2).

**Outer step.**
- LocalAdamW "syncs both" parameters and optimizer states, "roughly tripling traffic" (§4.2, v2).
- App. F, Table 7 (v2): "LocalAdamW synchronizes first and second optimizer moments". DiLoCo/Nesterov uses server learning rate 0.7 and momentum 0.9.
- The text read gives **no outer learning rate or server momentum for LocalAdamW.**
- Algorithm 2 (App. G) labels the outer step "OuterOpt ... (e.g., Adam)". Its closing prose says "gradients are synchronized only among the Oe replicas". §5 instead says the coordinator "aggregates only the parameters owned by each expert replica group". The wording is inconsistent.

**Inner optimizer (App. F, Table 7 and App. C).**
- AdamW with weight decay 0, betas (0.9, 0.95), ε = 1e-8, learning rate about 0.01.
- 640 optimizer batches, 160 of them warm-up.

**Contrast with ours (inference).** We reset AdamW every round and average parameters only.

### 5. Gating

- **Sigmoid, not softmax.** App. B.3.2, Eq. 17 (v2): p_i(x) = σ(xᵀw_r,i). Top-k (k = 2) is taken over these independent scores.
- **Stated reason:** a missing expert "must not skew the probability distribution of the remaining available experts" (App. B.3.2).
- **Output weights.** App. A.1, Eqs. 13 and 14 give y = Σ_{i∈T(x)} s_i(x)E_i(x) with s_i = σ(w_g,iᵀx). No renormalization over the selected experts appears (inference from the equations).
- **Router inputs** are normalized by Peri-LN (App. B.1).
- **Partitioned mode** (used "for most of our work", §3.3.3): "the gating network projects only to local experts" (§4.1). The router is split together with the experts.
- **Skip-token mode:** the full router is kept, and tokens assigned to "ghost experts" skip that expert path.
- **Difference from ours (inference).** Our softmax top-2 over the held experts, renormalized over the chosen 2, is the form FoMoE avoids on purpose.

### 6. Parameter breakdown (embeddings against experts)

What the paper states:
- Table 1 (v2 HTML): Small Proxy with d_model 256, 4 layers, 4 heads, 8 experts, d_expert 128, 2 active, "∼54M".
- Embeddings are "tied by default" (§3.2).
- The vocabulary is 200,019 tokens (App. F).
- Each expert projects d_model → d_expert and then applies SiLU (App. B.3.1). The projection back to d_model is not described there; I assume it.
- The paper gives **no parameter breakdown** itself.

**My arithmetic (inference; two weight matrices per expert, the second assumed; norms ignored):**

| Component | Calculation | Parameters |
|---|---|---|
| Embeddings | 200,019 × 256 | 51,204,864 |
| Attention | 4 × 256² × 4 layers | 1,048,576 |
| Experts | 2 × 256 × 128 × 8 × 4 | 2,097,152 |
| Router | 256 × 8 × 4 | 8,192 |
| **Total** | | **54,358,784** (≈ "54M") |

- So experts are about **3.9%** of all parameters, and experts plus router about 67% of the non-embedding parameters.
- **Ours, same assumption:** 2 × 384 × 768 × 8 × 6 = 28.3M of 46.05M, about **61%**.

### 7. Code and licence

- **No code repository** is linked in v1 or v2.
  - The only links in the v2 HTML are the SmolLM-corpus dataset and arXiv/LaTeXML boilerplate.
  - §5 promises "artifact status" in the reproducibility appendix, but App. F, Table 7 has no artifact entry.
- GitHub repository search ("FoMoE": 14 hits; "federation of MoEs": 1; "fomoe mixture experts": 0) found nothing by the authors.
  - `pmerolla/fomoe` (MIT, created 2026-03-19) is an unrelated MoE inference engine.
- The arXiv abs page shows arXiv's non-exclusive distribution licence 1.0. That licenses the paper, not code.
- **Verdict: no code, so no code licence.** This reconfirms round-1 notes 04a and 04b.

### 8. Resolving the two notes' cost figures

**The cells.** Table 6 (v2; numerically identical to v1's Table 7). LocalAdamW, M = 4 workers, validation perplexity on C4-en. O_e = 2 means each expert has 2 holders, so each worker holds 2·8/4 = 4 of 8 experts, as in our runs.

| Placement | K | O_e = 1 | O_e = 2 | O_e = 4 (full replica) |
|---|---|---|---|---|
| Fixed | 32 | 121.42 ± 16.55 | **112.00 ± 15.45** | **103.91 ± 14.43** |
| Fixed | 64 | 130.79 ± 17.67 | **119.53 ± 16.34** | **104.47 ± 14.74** |
| Fixed | 128 | 143.72 ± 19.07 | **123.50 ± 16.91** | **111.89 ± 15.57** |
| Random (§4.2 equates random placement with γ = 1, a reshuffle every round; App. F does not list the shuffle period T for these runs) | 32 | 124.47 ± 17.03 | 113.65 ± 15.81 | 103.91 ± 14.43 |
| Random | 64 | 129.74 ± 17.72 | 114.88 ± 15.88 | 104.47 ± 14.74 |
| Random | 128 | 148.62 ± 19.81 | 125.36 ± 17.15 | 111.89 ± 15.57 |

**Conversion (inference).**
- If perplexity = exp(mean cross-entropy), then ln(perplexity) is the mean cross-entropy in nats.
- The relative gap in cross-entropy is ln(PPL_a) / ln(PPL_b) − 1.
- Because bpc = cross-entropy / ln 2, this equals a relative bpc gap. It is therefore comparable in kind to our percentages.

**O_e = 2 against full replica, fixed placement:**
- K = 32: ln 112.00 = 4.7185 and ln 103.91 = 4.6435, so the gap is **+1.61%** (perplexity ratio +7.8%).
- K = 64: ln 119.53 = 4.7836 and ln 104.47 = 4.6489, so the gap is **+2.90%** (+14.4%).
- K = 128: ln 123.50 = 4.8162 and ln 111.89 = 4.7175, so the gap is **+2.09%** (+10.4%).

**O_e = 2 against full replica, random placement:**
- K = 32: ln 113.65 = 4.7331, gap **+1.93%**.
- K = 64: ln 114.88 = 4.7439, gap **+2.04%**.
- K = 128: ln 125.36 = 4.8312, gap **+2.41%**.

**O_e = 1 against full replica, fixed placement:** +3.35%, +4.83% and +5.31% at K = 32, 64 and 128.

**Resolution.** The two notes do not conflict.
- They use the same three cells and the same conversion. "Log-perplexity" and "cross-entropy" are the same quantity here.
- 04b's "+1.6% to +2.9%" is the range over K ∈ {32, 64, 128}. It is not monotone in K: the K = 64 cell is the largest.
- 04a's "+2.1%" is the K = 128 cell, chosen as the nearest to our H = 125.
- Two real slips remain in round 1:
  1. 04a's "Question it raises" says "1.6 to 2.1%"; it should say 1.6 to 2.9%.
  2. 04b says "O_e ≥ 4" where the paper has "O_e ≈ 4".

**Comparing with ours (inference).**
- Our sliced arm against full averaging is 1.108 / 1.061 − 1 = **+4.4%**. This uses the mean gaps over three seeds, not per-seed values.
- FoMoE's nearest cells are +2.1% (fixed placement, K = 128) and +2.4% (random placement, K = 128; reshuffled every round per §4.2, with T not listed in App. F). Our coverage policy also redraws every round, so the random-placement cell is arguably the closer match.
- **Caveats that limit the comparison (inference):**
  1. The "±" problem in item 3: no seed noise is reported.
  2. If the reported perplexity is a mean of per-chunk perplexities rather than exp(mean cross-entropy), ln(mean perplexity) overstates the mean cross-entropy (Jensen's inequality). The conversion is then approximate.
  3. K = 128 means 640/128 = 5 rounds in FoMoE, against our 40.
  4. FoMoE's experts are about 4% of its parameters, against about 61% of ours.
  5. Its full-replica arm itself degrades with K and M. At M = 8, K = 128, partial replication beats full replication: fixed O_e = 4 gives 138.88, against 159.71 for full replica. "Cost against full replica" therefore depends on how badly full replication does.

**Internal inconsistency, confirmed in both versions.**
- Table 6 lists M = 8, K = 32, fixed, O_e = 8 as 106.91 ± 14.99. The random-placement O_e = 8 cell is 106.30 ± 14.92, and Table 4's M = 8, K = 32 cell is 106.30 ± 14.92.
- 106.91 ± 14.99 is Table 4's M = 2, K = 128 value.
- Every other O_e = M cell in Table 6 matches Tables 4 and 5.

### 9. Other FoMoE items checked

- **Routing-entropy claim.** §1 (v2) says FoMoE "maintains high routing entropy and avoids expert collapse". I found no table or figure of routing entropy: Fig. 7 plots perplexity against FLOPs. The claim is unsupported in the text, as round 1 also found.
- **Load-balancing loss.** It is mentioned only as "introducing a load-balancing loss ensures they converge to a balanced state" (§4.1, v2). Coefficient and scope are not stated.
- **Skip-token quality.** Shown only in Fig. 7, in v1 and v2. The text says it "does not significantly impact training convergence" (§6.3, v2).

---

## Citing papers screened

**Citation counts by source** (OpenAlex and Semantic Scholar, fetched 11:02):

| Cited paper | OpenAlex ID | OpenAlex citers | Semantic Scholar citers |
|---|---|---|---|
| FoMoE | W7165168211 | 0 | 0 |
| Gating Dropout | W4281688600 | 11 | 34 |
| MaskMoE | W4400702959 | 0 | 12 |
| HARC | W7163409235 | 0 | 1 |
| FedAlign-MoE | W7140215383 | 0 | 4 |
| DDOME / FedJETs | W4380993710 | 1 | 6 |

- No other OpenAlex record was found for Gating Dropout (title search); the ICML/PMLR version has no separate record.
- The 11 OpenAlex citers of Gating Dropout are all in the Semantic Scholar list, except the SustaiNLP 2022 proceedings-volume record.

**Four-axis code used below:** 1 = stores only shared part plus own experts; 2 = routing masked to held experts during local training; 3 = holder-only averaging of experts and router rows; 4 = per-worker slice sizes. "N/A" means the paper has no distributed sliced training at all.

| Cited paper | Citer | ID | Year | How screened | Four axes (1 / 2 / 3 / 4) | Relevance |
|---|---|---|---|---|---|---|
| FoMoE | **none found** (OpenAlex 0, Semantic Scholar 0, arXiv API term searches, WebSearch for the ID) | n/a | n/a | n/a | n/a | n/a |
| Gating Dropout | Fixing MoE Over-Fitting on Low-Resource Languages in Multilingual MT (Elbayad, Sun, Bhosale) | 2212.07571 (Findings of ACL 2023 per the OpenAlex DOI 10.18653/v1/2023.findings-acl.897) | 2022 | sections read | N/A (centralized synchronous expert parallelism) | **medium:** independent re-test of Gating Dropout (see Papers read) |
| Gating Dropout | MoEC: Mixture of Expert Clusters (Xie, Huang, Chen, Wei) | 2207.09094 (AAAI 2023 per OpenAlex DOI 10.1609/aaai.v37i11.26617) | 2022 | sections read | N/A / **analogue of 2: random routing mask ("global-level expert dropout")** / N/A / N/A | **medium-high:** dose-response of random expert masking (see Papers read) |
| Gating Dropout | Communication-Efficient Sparsely-Activated Model Training via Sequence Migration and Token Condensation (Luffy) | 2411.15419 (IEEE ToN per Semantic Scholar) | 2024 | abstract | N/A (moves sequences between GPUs; routing unchanged per abstract) | low |
| Gating Dropout | TopoEP: Topology-Aware Load Balancing for Expert-Parallel MoE Training | 2609.35481 | 2026 | abstract | N/A (hot-expert replication and token rerouting in synchronous expert parallelism) | low |
| Gating Dropout | HierMoE: hierarchical token deduplication and expert swap | 2508.09591 (INFOCOM 2026 per Semantic Scholar) | 2025 | abstract | N/A (systems) | low |
| Gating Dropout | Exploring the Benefit of Activation Sparsity in Pre-training (SSD) | 2410.03440 (ICML 2024 per comment) | 2024 | abstract | N/A (switches sparse and dense training, centralized) | low |
| Gating Dropout | Soft Merging of Experts with Adaptive Routing (SMEAR) | 2306.03745 (TMLR per Semantic Scholar) | 2023 | abstract | N/A | low |
| Gating Dropout | On the Expressive Power of MoE for Structured Complex Tasks | 2505.24205 (NeurIPS 2025 per comment) | 2025 | abstract | N/A (theory) | none |
| Gating Dropout | Stratified MoE with dynamic capacity; AutoMoE; Who Says Elephants Can't Run | 2305.02176; 2210.07535; 2211.10017 | 2022 to 2023 | abstract | N/A (machine-translation architecture, NAS, inference system) | none |
| Gating Dropout | Systems papers: PipeMoE (INFOCOM 2023), MPipeMoE (2506.22175), MPMoE (TPDS 2024), Parm (2407.00599), ScheMoE (EuroSys 2024), Comet (2502.19811), FSMoE (2501.10714), Mast (ICDCS 2025), BalanceMoE (IEEE TCC 2026) | as listed | 2023 to 2026 | title only | N/A (MoE training systems with synchronous expert parallelism) | none for the axes |
| Gating Dropout | Other citers: Task-Based MoE (2308.15772), MoQE (2310.02410), FineQuant (2308.09723), two surveys (2402.09748, 2412.14219), NLLB *Nature* 2024, large-batch optimization (ICML 2022, no ID), motion magnification (2403.07347), Atmos-Bench (2507.11085), CMoE humanoid control (2603.03067), battery RUL (J. Energy Storage), MoCETSE (PLOS Comp. Biol.), case-based MoE recommendation (IEEE Access 2026) | as listed | 2022 to 2026 | title only | N/A | none |
| MaskMoE | SpecDrop | 2608.04084 | 2026 | already abstract-screened in round 1 (04b); not repeated | N/A | see 04b |
| MaskMoE | MASKerade: Token-Routed Mask Experts for Dense-to-MoE Upcycling | 2610.07809 (v1 6 Oct 2026) | 2026 | abstract | N/A (vision-language fine-tuning, masks over a frozen FFN) | low |
| MaskMoE | BEAM: Binary Expert Activation Masking | 2605.14438 | 2026 | abstract | N/A (learned per-token expert masks for inference speed) | low |
| MaskMoE | AIR-MoE: Adaptive Inverted-Index Routing | 2605.04952 (v2 3 Oct 2026) | 2026 | abstract | N/A; a centralized shortlist is a data-dependent analogue of 2 | low |
| MaskMoE | Improving Routing in Sparse MoE with Graph of Tokens | 2505.00792 | 2025 | abstract | N/A (routing fluctuation, centralized) | low (Q2) |
| MaskMoE | CartesianMoE | 2410.16077 (NAACL 2025) | 2024 | abstract | N/A | low |
| MaskMoE | SliceMoE (2512.12990, DAC 2026); MoE survey (2503.07137); HARPE (2412.07171); LBPE (2411.05504); Temporal Scaling Law (2404.17785, EMNLP 2025); robot trajectory policies (2606.01047) | as listed | 2024 to 2026 | title or abstract | N/A | none |
| HARC | Routing Drift Alone Does Not Diagnose Failure in Merged MoE LLMs (Wang et al.) | 2609.32821 | 2026 | sections read | N/A / N/A / No (whole-model merges) / N/A | **medium** for the router-merge mechanism (Q2, Q5) |
| FedAlign-MoE | MedMix | 2608.13911 | 2026 | already read in round 1 (02b); not repeated | see 02b | see 02b |
| FedAlign-MoE | FluxShard (2605.06027); atmospheric adversarial perturbations (2604.14643); SL-FAC split learning (2604.07316) | as listed | 2026 | title | N/A | none |
| DDOME / FedJETs | FedCoE | 2605.21264 | 2026 | already read in round 1 (02b); not repeated | see 02b | see 02b |
| DDOME / FedJETs | FedFMX: Fisher-Routed MoE for Federated Class-Incremental Learning | 2606.28835 (ECCV 2026 per comment) | 2026 | abstract | not stated / samples routed to a Fisher-chosen expert subset / not stated / not stated; non-IID vision | low |
| DDOME / FedJETs | pFedMoAP (federated prompt learning) | 2410.10114 (ICLR 2025 per comment) | 2024 | abstract | N/A (prompts as experts) | low |
| DDOME / FedJETs | pFedMoE (model-heterogeneous personalized FL) | 2402.01350 | 2024 | abstract | N/A (whole local models as experts) | low |
| DDOME / FedJETs | Federated Inference (2603.02214); AoI-aware federated mixture of digital-twin experts (IEEE OJCOMS 2026); dynamic gradient substitution for personalized FL (Computer Networks 2025; the OpenAlex citer) | as listed | 2025 to 2026 | title or abstract | N/A | none |

**Not citers.** Found by arXiv API or WebSearch and screened for the routing question:

| Lead | ID | How screened | Four axes | Relevance |
|---|---|---|---|---|
| LocMoE (locality loss biasing tokens to intra-node experts) | 2401.13920 v3 | sections read | N/A (synchronous expert parallelism) | medium for the routing question (see Papers read) |
| DeepSeek-V2, device-limited routing | 2405.04434 v5 | §2.2.2 and the training-hyperparameter paragraph read | N/A | low-medium (qualitative claim only) |
| HybridEP: cross-datacenter expert parallelism | 2510.19470 v1 | abstract | experts sharded across datacenters, tokens sent to remote experts every step; no local steps | low-medium (systems; no quality cost in the abstract) |
| DISCO: emergent specialization in populations of vision experts without a shared gate | 2609.36770 v1 | abstract | agents train separately and can call another agent's forward pass; vision fine-tuning | low-medium (remote-call analogue) |
| RelayMoE: memory-efficient expert routing | 2610.07333 v1 | abstract | N/A (systems) | none |
| ClientMorpher: MoE router-guided clustering for federated instruction tuning | 2608.15311 v1 | abstract | N/A (fine-tuning, non-IID) | low |
| Expert-Token Resonance | 2406.00023 v4 | abstract | N/A | low |
| MAGNET (DiLoCo-based merging of domain specialists) | 2603.25813 v1 | abstract | N/A | none |
| Decoupled DiLoCo | 2604.21428 | already read in round 1 (01); not repeated | n/a | see 01 |

**Result.** No citer of the six papers matches more than one of the four axes, and none matches all four.

---

## Papers read

### A. Routing Drift Alone Does Not Diagnose Failure in Merged MoE LLMs

- **Authors:** Yuanyi Wang, Yanggan Gu, Su Lu, Guanghao Zhu, Pengkai Wang, Yifan Yang, Congkai Xie, Zhaoyi Yan, Jianmin Wu, Hongxia Yang (The Hong Kong Polytechnic University; InfiX.ai).
- **Year and venue:** 2026, preprint (no venue in the v1 text).
- **arXiv:** 2609.32821, v1 only (Sat 26 Sep 2026 17:47:55 UTC). **Read v1.** https://arxiv.org/abs/2609.32821
- **Code:** https://github.com/wyy-code/SRR, Apache-2.0 (GitHub API: created 2026-09-20, last push 2026-09-25, not archived).
- **Read status:** sections read: abstract, §1, §2 (routing drift and repair), §3.1 to §3.3, §6.1 and §6.2. Table 2 was read from the prose only, because its extracted rows interleave.
- **How found:** the only Semantic Scholar citer of HARC.

**Setting and scale.**
- One-shot merging of fine-tuned MoE LLMs: DeepSeekMoE-16B-A3B, OLMoE-7B-A1B and Qwen3-30B-A3B.
- Merge methods: Average, Task Arithmetic, TIES and WUDI-Merge.
- Evaluation: 8 benchmarks, 5-shot, each evaluated 5 times (§6.1).
- Post-training merging; no distributed or local training.
- Worker count, local steps and IID or not: not applicable (one-shot merge of separately fine-tuned models).

**Key findings (v1).**
- 26.5 to 54.3% of token-layer expert sets change after merging, across six settings (§3.1).
- Among changed routes, 77.7 to 96.9% change when only the router *input* is replaced, not when only the router *parameters* are. The paper calls these "representation-induced".
- Changes caused by router parameters alone account for at most 1.8% (§3.1, Fig. 2b).
- Divergence between source and merged routing (Jensen-Shannon) predicts the gain from restoring source routes at chance level: AUROC 0.47 to 0.52 (§3.2).
- The best single expert in a pair overlaps little: mean maximum cosine between entering and leaving experts is 0.041 to 0.096. Yet source-route and merged-route mixture outputs have mean cosine 0.896 to 0.976, and beat matched random routes by 0.112 to 0.147 (§3.3, Fig. 4).
- Router repair gains are small and inconsistent:
  - HARC on DeepSeekMoE ranges from −0.133 percentage points (TIES) to +0.236 (Average).
  - The paper's own SRR changes the average by −0.056 to +0.139 points across eight OLMoE and Qwen3 settings (§6.2, prose).
- Conclusion: drift alone is "insufficient evidence of routing failure" (abstract).

**Remedy tags.**

[REMEDY | HARC training-free router calibration after a merge | router misalignment after merging | 16B to 30B MoE, merged fine-tunes | post-training merging | −0.133 to +0.236 points average score on DeepSeekMoE (prose) | §6.2, v1]

[REMEDY | SRR, selective router repair of the final five sparse layers | same | same | post-training merging | −0.056 to +0.139 points across 8 OLMoE and Qwen3 settings (prose) | §6.2, v1]

**Which of our costs it bears on.**
- Q2, the masked-routing cost of +3.2%: it weakens a pure "the averaged router misroutes" reading of HARC. Most route changes after a merge come from shifted router inputs.
- Q5: router repair after merging shows small, sign-varying effects at 7B to 30B.
- (inference) In our sliced arm the shared trunk is averaged over all 4 workers, while router rows are averaged over holders only. Both could shift routes, and this paper's crossing method could separate them.

**How its setup differs from ours.**
- One-shot merges of large, separately fine-tuned models, against our 40 rounds of from-scratch training.
- Every expert is present in every source model.
- Downstream accuracy, against our bpc.

**Question it raises for us.** After each merge, do most top-2 changes come from the averaged shared trunk (input shift) or from the holder-averaged router rows? The two can be crossed in our harness, as in §3.1.

**Four-axis classification.** 1 N/A; 2 N/A; 3 No (whole-model merges); 4 N/A.

### B. MoEC: Mixture of Expert Clusters

- **Authors:** Yuan Xie, Shaohan Huang, Tianyu Chen, Furu Wei.
- **Year and venue:** 2022 (arXiv). AAAI 2023 per the OpenAlex and Semantic Scholar DOI 10.1609/aaai.v37i11.26617; the arXiv PDF carries an AAAI copyright line.
- **arXiv:** 2207.09094, v1 only (Tue 19 Jul 2022 06:09:55 UTC). **Read v1.** https://arxiv.org/abs/2207.09094
- **Code:** none found in the sections read; not searched further.
- **Read status:** sections read: abstract, introduction (contributions and the paragraph on Gating Dropout), method (clustering loss and cluster-level expert dropout), experiments (setup, Tables 1 to 4). Appendices not read.
- **How found:** an OpenAlex and Semantic Scholar citer of Gating Dropout.

**Setting and scale.**
- WMT-14 En-De with a Transformer-big backbone, trained from scratch.
- MoE layers of 64 experts in the 3rd encoder and 3rd decoder blocks.
- X-MoE as the MoE baseline.
- GLUE with a Transformer-base backbone.
- Table 1 averages over a set of seeds.
- Worker count, local steps and IID or not: not applicable (centralized synchronous training).

**Key findings (v1).**
- **Dose-response of random expert masking in centralized training (Table 3).** "Global-level expert dropout" deletes randomly chosen experts from the routing candidate list during training. The setting is 64 experts, cluster size 8, and BLEU 32.21 with no dropout.

  | Dropout rate | Global-level BLEU | Cluster-level BLEU |
  |---|---|---|
  | 0 | 32.21 | 32.21 |
  | 0.25 | 31.88 | 32.32 |
  | 0.5 | 31.53 | **32.50** |
  | 0.75 | 29.73 | 32.02 |

  Dropping only within clusters of similar experts helps. The authors' reason is that otherwise tokens "may be dispatched to less relevant experts" (method section).
- **My arithmetic (inference):** global-level masking at rates 0.25, 0.5 and 0.75 costs 1.0%, 2.1% and 7.7% of BLEU.
- **Table 1** (row order checked against Table 2's cluster size 1 = 30.59 and Table 3's rate 0 = 32.21): dense 27.10, MoE baseline 30.59, MoEC without dropout 32.21, MoEC 32.50.

**Remedy tags.**

[REMEDY | ablation, not a remedy: global-level expert dropout (random routing mask) at rates 0.25 / 0.5 / 0.75 | masked-routing cost (dose-response) | Transformer-big MT, 64-expert MoE layers | training from scratch (MT) | BLEU 32.21 → 31.88 / 31.53 / 29.73 | Table 3, v1]

[REMEDY | cluster-level expert dropout (mask only within clusters of similar experts) | regularization while keeping a suitable expert reachable | same | same | 32.21 → 32.50 at rate 0.5 | Table 3, v1]

**Which of our costs it bears on.**
- Masked routing (+3.2%): this is the clearest dose-response found for random routing masks.
- The sign flips from harmful to helpful when the mask always leaves a similar expert available. (inference) That is consistent with round 1's "consistency" reading of MaskMoE.

**How its setup differs from ours.**
- Centralized synchronous training.
- How often the mask is redrawn (per token, per batch or per step) is not stated in the sections read. Ours is fixed per worker for 125 steps.
- Machine translation and BLEU, against characters and bpc.
- 64 experts plus a clustering loss.

**Question it raises for us.** Does our masked-routing cost grow with the masked fraction the same way (mild to 0.5, steep beyond)? Slices of 5, 6 and 7 of 8 experts would trace this curve, as round-1 note 02a's gap 1 proposes.

**Four-axis classification.** 1 N/A; 2 analogue (random routing mask during training); 3 N/A; 4 N/A.

### C. Fixing MoE Over-Fitting on Low-Resource Languages in Multilingual Machine Translation

- **Authors:** Maha Elbayad, Anna Sun, Shruti Bhosale.
- **Year and venue:** 2022 (arXiv). Findings of ACL 2023 per the OpenAlex DOI 10.18653/v1/2023.findings-acl.897.
- **arXiv:** 2212.07571, v1 only (Thu 15 Dec 2022 01:06:55 UTC). **Read v1.** https://arxiv.org/abs/2212.07571
- **Code:** none found in the sections read.
- **Read status:** sections read: abstract, §3 (EOM, FOM, CMR), §4 (setup), §5.1 (opening), §5.2 (Table 2 and the Gating Dropout comparison).
- **How found:** an OpenAlex and Semantic Scholar citer of Gating Dropout.

**Setting and scale.**
- Multilingual machine translation: 53 languages, 110 directions, an MoE-64 model.
- 100k updates at about 1M tokens per update; top-2 gating.
- Metric: chrF++.
- Training from scratch (MT).
- Which backbone Table 2 uses (615M or 1.3B, both in Table 1) was not confirmed in the sections read.
- Worker count, local steps and IID or not: not applicable (centralized synchronous training).

**Key findings (Table 2, v1).** chrF++ averages over all directions in each group:

| Row | eng-xx | xx-eng | xx-yy |
|---|---|---|---|
| Baseline (p_drop = 0.3) | 44.3 | 54.4 | 41.9 |
| Gating Dropout (p_gd = 0.2) | 44.4 | 54.8 | 42.3 |
| EOM | 44.7 | 54.8 | 42.5 |
| CMR top-1 | 44.2 | 54.9 | 42.3 |
| CMR top-2 (about 23% more compute) | 46.2 | 55.1 | 42.8 |

- The authors sweep (p_drop, p_gd) ∈ {0.1, 0.2, 0.3}² and say Gating Dropout "performs better than the baseline MoE" (§5.2).
- They also say it is "outperformed by all of our proposed methods". By the table, CMR top-1 is below Gating Dropout on eng-xx (44.2 against 44.4).

**Remedy tag.**

[REMEDY | Gating Dropout (tokens kept on local experts with probability p_gd per step), independent re-test | regularization; inverse analogue of masked routing | MoE-64 multilingual MT | training from scratch (MT) | +0.1 / +0.4 / +0.4 chrF++ at p_gd = 0.2 | Table 2, §5.2, v1]

**Which of our costs it bears on.** An independent group confirms Gating Dropout's direction: keeping about 20% of steps local is harmless or slightly helpful in synchronous training.

**How its setup differs from ours.**
- Every step is synchronized, so forced-local steps still update one shared model.
- Translation, 64 experts.

**Question it raises for us.** Is there a fraction of masked rounds below which the masked-routing cost vanishes? The harness has both partial-update and sliced modes, so mixing them by round would trace this (an untested design, inference).

**Four-axis classification.** N/A on all four (centralized synchronous expert parallelism).

### D. LocMoE: A Low-Overhead MoE for Large Language Model Training

- **Authors:** Jing Li, Zhijie Sun, Xuan He, Li Zeng, Yi Lin, Entong Li, et al.
- **Year and venue:** 2024, preprint.
- **arXiv:** 2401.13920. Versions:
  - v1: Thu 25 Jan 2024 03:36:39 UTC.
  - v2: Sat 11 May 2024 10:11:49 UTC.
  - v3: Thu 23 May 2024 10:03:35 UTC.
  - **Read v3.** https://arxiv.org/abs/2401.13920
- **Code:** none found in the text.
- **Read status:** sections read: abstract, §1 (contributions), §3.2 (locality loss), §4 (results and ablation), appendices C to E (environment and configuration, partly).
- **How found:** arXiv API locality search and WebSearch; it does not cite any of the six.

**Setting and scale.**
- PanGu-Σ on MindSpore, Ascend 910A clusters of 64, 128 and 256 NPUs.
- 16 experts, 8 MoE layers (App. D Table 1, partly read).
- Carrier-network domain corpora.
- Pretraining from scratch.

**Key findings (v3).**
- A locality loss is added to the auxiliary balance loss (§3.2, Eq. 6). It is the KL divergence between the current assignment distribution and a "fully localized" one.
- Time per epoch falls by 12.68% to 22.24%, and All-to-All time by 5.13% (§1).
- **Quality evidence is figure-only:** validation-perplexity curves (Fig. 13) and task scores (Fig. 14).
- **No table reports the fraction of tokens kept local, or a loss difference.**
- The locality loss "would lose efficacy when the local expert does not exist" (§4.2), at 256 NPUs.

**Which of our costs it bears on.** Only the question of routing tokens to non-held experts. Even there it supplies no number.

**How its setup differs from ours.** Synchronous per-step expert parallelism: every expert is reachable every step, and locality is a soft bias.

**Question it raises for us.** None directly answerable.

**Four-axis classification.** N/A on all four.

### E. DeepSeek-V2 (device-limited routing only)

- **Authors:** DeepSeek-AI.
- **Year and venue:** 2024, technical report (preprint).
- **arXiv:** 2405.04434. Versions: v1 7 May 2024, v2 8 May, v3 16 May, v4 24 May, v5 19 Jun 2024. **Read v5.** https://arxiv.org/abs/2405.04434
- **Code:** not checked.
- **Read status:** sections read: §2.2.2 (Device-Limited Routing) and the training-hyperparameter paragraph only.

**Setting.**
- Pretraining with fine-grained routed experts spread uniformly over D = 8 devices per layer.
- Each token's experts are confined to at most M = 3 devices: the M devices holding the highest-affinity experts are picked first, then top-K is taken among their experts.

**Key finding.** With M ⩾ 3, performance is reported as "roughly aligned with the unrestricted top-K routing" (§2.2.2, v5). **No numbers are shown.**

**Which of our costs it bears on.** Restricting routing to a subset of experts is reported as nearly harmless when the subset is chosen by affinity, per step. That differs from our worker-fixed, content-independent mask (inference).

**How its setup differs from ours.** Synchronous; the restriction is data-dependent; 236B-parameter scale.

**Question it raises for us.** Would an affinity-chosen slice (assigning experts to workers by router statistics) reduce the masked-routing cost?

**Four-axis classification.** N/A on all four.

---

## Routing tokens to non-held experts

**Takeaway.** **Not found in this search:** no paper reports a measured quality result where workers, during local training between synchronizations, send a fraction of tokens to experts they do not hold and have those tokens computed remotely. The nearest evidence comes in five kinds, none of them local-step training with remote computation:

1. **Skip-token (FoMoE).**
   - The full router is kept. Tokens routed to non-resident ("ghost") experts skip that expert path; they are not computed remotely (§3.3.3, v2).
   - The quality effect is shown only in Fig. 7 (v1 and v2), with the text saying it "does not significantly impact training convergence" (§6.3, v2).
   - Measured throughput rises up to 1.4× (Fig. 11).
   - (inference) FoMoE's sigmoid gate lets an absent expert's term simply drop out. Our softmax top-2 would need a decision on whether to renormalize over the surviving expert, so skip-token results may not transfer.
2. **Frozen local copies (SPES, round-1 note 04a).** Every expert is routed to, using a full local copy whose non-owned experts are frozen. This is not remote, and SPES has no masked arm to compare against.
3. **Synchronous expert parallelism with a fraction kept local.**
   - Gating Dropout (2205.14336; re-read at 11:21 for this note, v2 PDF, Table 2 and §4.4):
     - On WMT-10 (Transformer-base), BLEU at convergence is 24.60 for the baseline, 25.06 for Gate-Drop and 25.12 for Gate-Expert-Drop.
     - Gate-Expert-Drop is best at p = 0.2. At p = 0.5 it falls below the baseline (ΔBLEU −0.23, §4.4, Figure 6 text). Gate-Drop is best at p = 0.3.
     - (Gate-Expert-Drop skips the experts entirely when it is on; Gate-Drop keeps tokens on local experts.)
   - Its independent re-test (paper C): +0.1 to +0.4 chrF++ at p_gd = 0.2.
   - DeepSeek-V2 device-limited routing (paper E): a qualitative claim of rough parity at M ≥ 3 of 8 devices.
   - LocMoE (paper D): figures only; no local fraction reported.
   - In all of these, tokens that do go to other machines reach an up-to-date expert every step, so none answers our question.
4. **Random routing masks in centralized training (MoEC, paper B).** A dose-response: masking 25%, 50% and 75% of candidate experts costs 0.33, 0.68 and 2.48 BLEU (Table 3, v1). A structured mask that always leaves a similar expert available instead gains 0.29 BLEU.
5. **Remote calls without local steps.**
   - Learning@home (04b): remote expert calls every step.
   - HybridEP (2510.19470): cross-datacenter expert parallelism, abstract only.
   - DISCO (2609.36770): agents call another agent's forward pass; vision fine-tuning; abstract only.
   - None reports a cost against a local-only alternative in our sense.

**Search coverage for this question:**
- Forward citations of Gating Dropout (Semantic Scholar 34, OpenAlex 11).
- arXiv API queries on "local experts" with DiLoCo, "local SGD" with MoE, "low-communication" with experts, "ghost experts" or "skip-token", "held experts", "expert sharding", and locality with routing and all-to-all.
- WebSearch: "route tokens to local experts", "DiLoCo MoE remote experts", "Gating Dropout follow-up".
- Leads not pursued: Occult (collaboration pruning) and TA-MoE (topology-aware dispatch), which are synchronous and in the same family as items 3 above.

---

## Synthesis

1. **No closer work was found.**
   - No citer of FoMoE, Gating Dropout, MaskMoE, HARC, FedAlign-MoE or DDOME/FedJETs matches more than one of our four axes.
   - FoMoE has no recorded citers: OpenAlex 0, Semantic Scholar 0, nothing in the arXiv API or WebSearch. It remains the closest work found, matching three of four axes; it does not have per-worker slice sizes.
   - **Our full combination was not found in this search.** That combination is shared-part-only storage, masked softmax routing, holder-only averaging with per-round redraws, plain averaging with fresh AdamW, and per-worker slice sizes.
2. **FoMoE's cost figure is settled, but it is weaker evidence than round 1 implied.**
   - The two round-1 notes agree: +1.6%, +2.9% and +2.1% in cross-entropy at K = 32, 64 and 128 (M = 4, 2 holders, fixed placement, LocalAdamW).
   - Random placement gives +1.9%, +2.0% and +2.4%. §4.2 implies it is reshuffled every round, which would make it closer to our redraws.
   - The "±" values are probably per-sample spreads, not seed spreads (inference from the near-constant 12.6 to 15.7% ratio). So no seed noise is reported.
   - No centralized number exists in either version, and v2 softened v1's claim of matching centralized quality.
   - FoMoE's experts are about 4% of its parameters, against about 61% of ours (inference).
3. **New evidence on the masked-routing cost (+3.2%).**
   - MoEC: random routing masks cost more as the masked fraction grows (1.0%, 2.1% and 7.7% of BLEU at 0.25, 0.5 and 0.75). Masks that always leave a similar expert available help. Centralized MT.
   - The Gating Dropout re-test confirms that a small fraction of forced-local steps is harmless in synchronous training.
   - Routing Drift: after merging, 77.7 to 96.9% of route changes come from shifted router inputs, and route disagreement does not predict harm. This bears on how to read HARC-style misalignment in our holder-averaged router (inference).
4. **Round-1 leads now verified.**
   - 02a's planned forward-citation search on Gating Dropout: **now done**. It found no decentralized-MoE citer; the two relevant citers are papers B and C.
   - 02b's "no citation chasing on HARC, FedAlign-MoE or DDOME": **now done**, with Semantic Scholar finding 1, 4 and 6 citers. Only HARC's citer (paper A) is relevant.
   - 04a/04b "FoMoE code: none": **now verified** for both versions and by GitHub search.
   - 04a/04b "meaning of FoMoE's ±": **partly resolved**. Both definitions appear in the paper, v1 used different wording, and the numbers point to a per-sample spread (inference).
   - 04a/04b "FoMoE centralized number": **now verified absent** in v1 and v2.
   - 04a/04b "FoMoE load-balancing scope" and "routing-entropy evidence": **still not stated**.
5. **Corrections to round-1 notes.**
   - 04a's "1.6 to 2.1%" should read 1.6 to 2.9%.
   - 04b's "O_e ≥ 4" should read "O_e ≈ 4".
   - The 106.91 / 106.30 cell inconsistency is present in v1 as well.

---

## Could not verify

- **FoMoE:**
  - which definition of "±" is correct (seeds against dataset);
  - whether the reported perplexity is exp(mean cross-entropy) or a mean of per-chunk perplexities, which affects the ln conversion;
  - the load-balancing coefficient and scope;
  - the outer learning rate or momentum for LocalAdamW;
  - the reshuffle period T of the random-placement runs (§4.2 implies every round; App. F does not list it);
  - any routing-entropy measurement;
  - skip-token quality numbers (Fig. 7 only);
  - centralized perplexity (Figs. 5 and 13 only).
  - Tried: full v2 read, v1 sections, HTML table and text extraction, a search of the HTML for links.
- **MoEC:** how often the global-level mask is redrawn, the routing top-k, code availability and affiliations. Not in the sections read.
- **Fixing MoE Over-Fitting (2212.07571):** whether Table 2 uses the 615M or 1.3B backbone.
- **LocMoE:** the fraction of tokens kept local, and any numeric quality comparison. Figures only.
- **DeepSeek-V2:** the numbers behind "roughly aligned". None in §2.2.2.
- **Routing Drift (2609.32821):** individual Table 2 cells, which were garbled in extraction. Only prose numbers are used.
- **Venues for MoEC (AAAI 2023) and 2212.07571 (Findings of ACL 2023):** these come from OpenAlex and Semantic Scholar DOI records, not from the arXiv text, apart from MoEC's AAAI copyright line.
- **Citers without arXiv IDs** (systems venues, journals) were screened by title only.
- **Google Scholar "cited by"** is not reachable through WebSearch. OpenAlex and Semantic Scholar lag on recent preprints, so a FoMoE citer posted after mid-2026 could be missed.
- **HybridEP and DISCO:** abstract only.

---

## Query log

All times are local machine time (TST) on 2026-10-11, from `date`. WebSearch calls were not individually timestamped; they are bracketed by the neighbouring `date` outputs. No HTTP 429 or 503 responses were seen.

| Time | Source | Request | Result |
|---|---|---|---|
| 11:00:59 | local | read the brief and notes 02a, 02b, 04a, 04b | n/a |
| 11:01:34 | api.openalex.org | `filter=doi:10.48550/arXiv.{ID}` for the six IDs | W7165168211, W4281688600, W4400702959, W7163409235, W7140215383, W4380993710 |
| 11:01:54 | api.openalex.org | title `search=` for Gating Dropout, MaskMoE, FedJETs, Fed-ZERO, FedAlign-MoE (v2 title and v1 title) | no extra records for the six |
| 11:02:07 | api.openalex.org | `filter=cites:{ID}&per-page=200` × 6 | FoMoE 0, GD 11, MaskMoE 0, HARC 0, FedAlign 0, DDOME 1 |
| 11:02:23 to 11:02:50 | api.semanticscholar.org | `/paper/arXiv:{ID}/citations?limit=100` × 6 (4 s apart) | FoMoE 0, GD 34, MaskMoE 12, HARC 1, FedAlign 4, DDOME 6; all HTTP 200 |
| 11:03:21 to 11:03:57 | export.arxiv.org API (3 s apart) | `all:FoMoE`; `"full-replica" AND experts`; `"partial replication" AND "mixture of experts"`; `abs:"resident experts"`; `"federation of MoEs"`; `"subset of experts" AND decentralized`; `"local experts" AND MoE AND DiLoCo`; `DiLoCo AND experts`; `decentralized AND MoE AND pretraining`; `federated AND MoE AND pre-training` | FoMoE is the only relevant hit; leads 2609.36770, 2608.15311, 2603.25813 |
| 11:04:23 to 11:04:58 | export.arxiv.org API (3 s apart) | `"local SGD" AND MoE`; `"low-communication" AND experts`; `"expert sharding"`; `"ghost experts" OR "skip-token"`; `"held experts" OR "local expert subset" OR "expert slices"`; `volunteer AND experts AND training`; `"decentralized training" AND "mixture of experts"`; `"outer optimizer" AND experts`; `"partial training" AND experts AND federated`; `locality AND routing AND all-to-all AND experts` | leads 2401.13920, 2610.07333 |
| ~11:04 to 11:05 | WebSearch (extended) | `FoMoE "Federation of MoEs" Sani Lane partial replica experts` | FoMoE pages only |
| same | WebSearch (extended) | `decentralized mixture-of-experts pretraining workers hold subset of experts router masked local experts 2026 arXiv` | nothing new (EMO, Learning@home, surveys) |
| same | WebSearch (standard) | `MoE training route tokens to local experts reduce all-to-all quality loss fraction of tokens remote experts` | LocMoE, Expert-Token Resonance, Luffy, NetMoE |
| 11:05:23 | arxiv.org | abs, PDF v1 and v2, HTML v1 and v2 of 2606.19025 (3 s apart) | read as described |
| 11:08:29 | api.github.com | `search/repositories?q=FoMoE`, `federation+of+MoEs`, `fomoe+mixture+experts` | 14, 1, 0 hits; none by the authors |
| 11:09:09 | export.arxiv.org API | `id_list` of 24 citer and lead IDs | abstracts screened |
| ~11:10 to 11:11 | WebSearch (standard) | `"2606.19025"` | no citing pages |
| same | WebSearch (extended) | `DiLoCo mixture of experts expert parallelism across sites remote experts local steps partial expert replication 2026` | lead HybridEP 2510.19470 |
| same | WebSearch (standard) | `"Gating Dropout" Liu 2022 follow-up local experts probability all-to-all skip regularization MoE 2024 2025` | MoEC (already a citer) |
| 11:11:42 to 11:12:13 | arxiv.org | PDF and abs of 2609.32821, 2401.13920, 2212.07571, 2207.09094 (3 s apart) | all HTTP 200 |
| 11:13:06 | api.github.com | `repos/wyy-code/SRR` | Apache-2.0 |
| 11:14:01 | arxiv.org; export.arxiv.org | PDF and abs of 2405.04434; `id_list=2510.19470,2405.04434` | read §2.2.2; HybridEP abstract |
| 11:14:31 | export.arxiv.org API | `id_list` of 9 more IDs (2402.01350, 2410.10114, 2609.36770, 2412.07171, 2411.05504, 2404.17785, 2512.12990, 2503.07137, 2604.21428) | abstracts screened |
| 11:16:51 | local | `date`; writing notes | n/a |
| 11:21:46 | arxiv.org | PDF of 2205.14336v2 (Gating Dropout), to check the numbers quoted in the routing section | Table 2 and §4.4 read |

**Not covered:**
- Google Scholar "cited by", OpenReview, Chinese-language venues.
- GitHub code search inside repositories: the GitHub MCP connector failed to connect, so only the unauthenticated repository-search API was used.
- Semantic Scholar keyword search (not attempted this round).
- Full texts of the systems citers, HybridEP, DISCO, FedFMX, pFedMoE and pFedMoAP.
- Occult and TA-MoE (synchronous locality-aware dispatch).
- Citers of SPES and FlexOlmo (round 1, note 04a).
