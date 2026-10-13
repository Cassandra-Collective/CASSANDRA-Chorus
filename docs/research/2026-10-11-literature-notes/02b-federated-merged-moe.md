# 02b: Federated, decentralized and merged mixture-of-experts training (question 2, federated half, and question 5)

| | |
|---|---|
| Date | 2026-10-11 (searches and reading 10:28 to 10:44 TST, UTC+3) |
| Scope | What happens to routing and expert specialization when experts are trained apart (expert subsets per worker or client) and then averaged or merged. Bears on the masked-routing cost (+3.2%), on interchangeable experts (Task A), and on router remedies (Q5). |
| Excluded by assignment | SPES, MoE-DisCo, BTX, BTM, DiPaCo, THOR, Hash Layers, X-MoE. FlexOlmo read by sections only (another researcher chases its citations). |
| Method | Every number below was read in raw text extracted with `pdftotext` (layout and reading-order modes) from PDFs fetched from arxiv.org into `scratchpad/papers/q2b/{ID}/`. Search snippets were used only to discover papers. Several tables came out garbled (row labels shifted); where that happened, the note says how the row mapping was checked, or the number is not used. |
| Our setup (for contrast) | 46.05M-parameter top-2 MoE, 8 experts, 4 workers, IID text8 data, pretraining from scratch, H = 125 local AdamW steps (fresh each round), 40 rounds, plain averaging. Sliced arm: worker holds shared part + 4 experts, top-2 over its 4; after the merge, top-2 over 8; each expert held by 2 workers and averaged over them, router row averaged over the same holders. |

Labels used: "(inference)" marks my reasoning, not a paper's claim. Version numbers are arXiv versions.

## Papers

### 1. FedAlign-MoE: Federated Mixture-of-Experts Alignment on Mobile Edge Networks under Data Heterogeneity

- **Authors (v2):** Zihan Fang, Qianru Wang, Haonan An, Zheng Lin, Yiqin Deng, Symeon Chatzinotas, Yuguang Fang. The v1 author list had Xianhao Chen instead of Symeon Chatzinotas.
- **Year / venue:** 2026, preprint (no venue stated).
- **arXiv:** 2603.21276. v1 22 Mar 2026, titled "Aggregation Alignment for Federated Learning with Mixture-of-Experts under Data Heterogeneity". v2 6 Oct 2026, retitled. **Read v2**; v1 Table I compared.
- **Link:** https://arxiv.org/abs/2603.21276
- **DOI:** none found. **Code:** none found in the text.
- **Read status:** full text (v2). v1 Table I and setup also read.
- **Setting and scale:**
  - Fine-tuning, not pretraining. Switch-base-16 (top-1 over 16 experts) and DeepSeek-MoE-16B (top-2 of 64, 8-rank LoRA).
  - N = 10 clients, one local epoch per round, 25 rounds, learning rate 1e-4 (Sec IV-4).
  - Non-IID data from a Dirichlet split with α = 0.1. Table I also has an IID column, and Table II has α = 0.5 and 1.0.
  - Tasks: AGNews, PIQA, HellaSwag, MMLU.
  - Clients route over **all** experts. A client updates the experts its own data activates, so its expert subset comes from the data, not from a hard limit.
- **What is measured as the failure** (Sec II, motivating studies, Switch with 8 experts on AGNews, non-IID):
  - **"Gating preference misalignment":** gating networks trained on different clients' data prefer different experts (Fig 2). Averaging them gives a global gate whose expert selection is misaligned with every client (t-SNE of gate parameters, Fig 3a), and accuracy drops after aggregation (Fig 3b). The abstract calls the averaged gate a "one-size-fits-none global gating network".
  - **"Expert semantic blurring":** the authors train a global MoE, then **freeze the gate on every client** and let each client update its experts on its own non-IID data. Same-index experts then produce widely different output-embedding distributions on the same test set (t-SNE, Fig 4a-c), and local accuracy is lower after averaging (Fig 4d).
  - Magnitudes are shown only in figures (bars and t-SNE). No numeric divergence metric appears in the text. **No magnitude of the failure itself can be quoted.**
- **Remedy:**
  1. Gate alignment in function space. Clients upload per-expert average routing probabilities. The server builds a weighted global routing distribution, with weights from "expert overlap" times "routing decision margin" (Eq 4-7). Each client adds a KL regularizer, Lreg, toward that distribution, restricted to selected or globally prominent experts (Eq 8-11).
  2. Semantic-aware expert aggregation. For each pair of clients, an expert's update counts only if (a) the cosine similarity of the mean hidden states routed to it exceeds a threshold, and (b) the update directions agree (cosine). The threshold adapts per expert (Eq 12-18).
- **Key numbers** (Table I, v2: test accuracy, Switch-base-16):
  - AGNews, IID: FedAvg 0.9263, FedMoE 0.9339, FedAlign-MoE 0.9424.
  - AGNews, non-IID: FedAvg 0.7740, FedMoE 0.8137, FedAlign-MoE 0.8522.
  - MMLU, IID: FedAvg 0.4641, FedAlign-MoE 0.5131.
  - MMLU, non-IID: FedAvg 0.3008, FedAlign-MoE 0.3845.
  - DeepSeek-MoE-16B AGNews: IID FedAvg 0.9206 vs FedAlign-MoE 0.9402; non-IID 0.7696 vs 0.8518.
  - My arithmetic, Switch AGNews: the remedy's gain over FedAvg is +1.6 points under IID and +7.8 under non-IID. FedAvg itself loses 15.2 points going from IID to α = 0.1.
  - Sec V-A1: "In the IID setting, all FL methods achieve comparable performance."
  - Table II (AGNews, Switch; this part of the extraction is consistent with Table I at α = 0.1): at α = 1.0, FedAvg 0.8978 vs FedAlign-MoE 0.9355. So the gap is 3.8 points at α = 1.0, 1.6 at IID and 7.8 at α = 0.1 (my arithmetic).
  - Prose summary (Sec V-A1): accuracy "improvement of 4% over FedMoE and 7% over FedAvg".
  - Ablations (Fig 16, gating alignment; Fig 17, expert aggregation): the text says each component helps. The values are in figures only, so none are recorded.
- **Version note:** v1 Table I differs from v2 in at least one cell. Switch, FedAlign-MoE, MMLU non-IID reads 0.3979 in v1 and 0.3845 in v2, by column order in a partly garbled v1 extraction. The v1 caption says "Switch-base-64" while its body says Switch-base-16; the v2 caption says Switch-base-16. **Cite v2.**
- **Tags:**
  - [REMEDY | KL regularization of local routing toward a consistency-weighted global routing distribution | gating misalignment (Q2; analog of masked routing) | Switch-base-16 / DeepSeek-MoE-16B, 10 clients | fine-tuning | component effect in figures only; full method +7.8 pts AGNews over FedAvg non-IID, +1.6 IID | Table I v2, Fig 16]
  - [REMEDY | semantic-aware (input-region plus update-direction) gated expert aggregation | expert semantic blurring | same | fine-tuning | figure only | Fig 17]
- **Bears on:** Q2 (named failure modes), Q5 (router alignment, similarity-gated expert merging). Cost: masked routing +3.2% only by analogy.
- **Differences from ours:**
  - Non-IID by construction; clients hold the full model and route over all experts.
  - Fine-tuning a pretrained MoE, one epoch per round, 25 rounds.
  - The baselines are other FL methods. **There is no centralized baseline**, so the cost of federating cannot be read off.
- **Question for us:** with IID data, do same-index experts held by two different workers drift apart at all within H = 125 steps? Their update-direction cosine (Eq 13) is cheap to log at each merge.

### 2. HARC: When Model Merging Breaks Routing: Training-Free Calibration for MoE

- **Authors:** Canbin Huang, Tianyuan Shi, Xiaojun Quan, Jingang Wang, Jianfei Zhang, Qifan Wang.
- **Year / venue:** 2026. The PDF header says Proceedings of the 43rd ICML, PMLR 306, 2026.
- **arXiv:** 2606.03391. Only v1, 2 Jun 2026. Read v1.
- **Link:** https://arxiv.org/abs/2606.03391
- **Code:** https://github.com/huangcb01/HARC. GitHub API: created 2026-05-21, last push 2026-09-15, not archived, **licence field null (no licence)**.
- **Read status:** full text, including Appendices A-D.
- **Setting and scale:**
  - Merging task-specific **fine-tunes** of one base: OLMoE-1B-7B-0125 (16 MoE layers) fine-tuned on math and on code from OLMoE-SFT; a 3-model merge adding chat (App D.1); Qwen3-30B-A3B, 128 experts with 8 active (App D.2).
  - Merges are one-shot (one merge, no rounds). The sources differ by **task**, which is extreme data heterogeneity.
- **How breakdown is measured** (Sec 1, preliminary study; two OLMoE fine-tunes merged with WUDI-merging):
  - Token-level expert assignments are tracked across all layers: "50.11% of expert selections deviate from the source models".
  - Across 16 layers, 99.98% of tokens see some routing divergence, with an average of 8.02 mismatched decisions per token.
  - Router swap (Fig 1, figure only): the merged router on a source model hurts it; the source router on the merged model recovers much of the performance.
  - Layer-wise KL between merged and source routers (Fig 4a, prose) stays low in shallow layers and rises sharply from layer 11 of 16.
- **Proposed mechanism** (Sec 3.2, Sec 1):
  - A linear merge of router weights averages the logits, but the softmax of averaged logits is not the average of the softmaxes.
  - Top-k then turns small logit shifts into different expert choices.
  - The paper argues load-balancing objectives make this worse, because balanced routers keep probabilities small and close together.
- **Remedy:**
  - Choose merged router weights that minimize the expected KL between each source router's distribution and the merged router's.
  - A second-order expansion gives a Hessian-weighted least-squares problem (Theorem 4.2), solved matrix-free by conjugate gradient, layer by layer, on calibration prompts forwarded through the merged model.
- **Effect sizes:**
  - Table 1 (OLMoE math+code; overall score):
    - Individual source models (upper bound): 40.05. Weight averaging: 34.43. Weight averaging + HARC: 34.93 (+0.50).
    - WUDI 38.08 → WUDI + HARC 38.96 (+0.88); the WUDI numbers are prose-confirmed.
    - RegMean 37.14 → 37.58; confirmed in Table 7.
    - The TIES, DARE and Fisher rows are mapped by row order only, because the extraction shifted their labels. They show gains of about +0.2 to +0.5 and are not used further.
  - HumanEval+ (prose, Sec 5.2): 33.50 for the individual model vs 20.27 after averaging. HARC partly recovers it.
  - My arithmetic: HARC recovers about 9% of the averaging gap (0.50 of 5.62) and about 45% of the WUDI gap (0.88 of 1.97).
  - 3-model merge (Table 5, App D.1): WUDI 42.84 → 43.44 (+0.60, prose); individual 47.04.
  - Qwen3-30B-A3B (Table 6, App D.2): individual 75.83; gains of +0.27 to +0.64 across five merging methods (prose); WUDI + HARC 75.11 (+0.52).
    - Small inconsistency: the prose attributes +0.27 to Fisher, but by row order +0.27 is weight averaging and Fisher is +0.31.
  - Post-merge SFT vs HARC (Table 7, App D.3; WUDI):
    - SFT: +0.27 (38.08 → 38.35), and routing KL rises from 0.00508 to 0.00544.
    - HARC: +0.88, KL 0.00484.
    - HARC + SFT: 39.36.
    - Authors: "standard fine-tuning does not correct the router".
  - Partial-layer calibration (Table 4, App C.3): the last 4 of 16 layers give 36% of the full gain; the last 8 give 52%.
- **Tags:**
  - [REMEDY | training-free Hessian-aware router recalibration after merge (KL-matching to source routers) | routing breakdown after merging (analog of masked routing) | OLMoE-1B-7B and Qwen3-30B-A3B, 2-3 source models | fine-tuning merges | +0.50 (weight averaging) to +0.88 (WUDI) overall on OLMoE; +0.27 to +0.64 on Qwen3 | Table 1, Tables 5-6, App D]
  - [REMEDY | full post-merge SFT on calibration data | same | OLMoE | fine-tuning | +0.27 alone, +1.28 combined with HARC (WUDI) | Table 7]
- **Bears on:** Q2 (mechanism of misrouting after merging), Q5 (post-merge router remedy). Cost: masked routing +3.2%.
- **Differences from ours:**
  - One-shot merge of task-divergent fine-tunes of a large pretrained MoE, versus our iterative averaging every 125 steps from a shared state on IID data.
  - Source routers in HARC were trained over the full expert set; ours were trained over 4 of 8.
  - (inference) HARC's KL target, "match each source router", has a direct analog for us: the merged router could match each worker's local routing distribution restricted to that worker's 4 experts.
- **Question for us:** after each merge, what fraction of a worker's local top-2 decisions (over its 4 experts) survives in the merged top-2 over 8, layer by layer? That is HARC's "expert mismatch" metric adapted to masking.

### 3. FlexOlmo: Open Language Models for Flexible Data Use

- **Authors:** Weijia Shi, Akshita Bhagia, Kevin Farhat, Niklas Muennighoff, Pete Walsh, Jacob Morrison, Dustin Schwenk, Shayne Longpre, Jake Poznanski, Allyson Ettinger, Daogao Liu, Margaret Li, Dirk Groeneveld, Mike Lewis, Wen-tau Yih, Luca Soldaini, Kyle Lo, Noah A. Smith, Luke Zettlemoyer, Pang Wei Koh, Hannaneh Hajishirzi, Ali Farhadi, Sewon Min.
- **Year / venue:** 2025, preprint ("Preprint. Under review." in v4).
- **arXiv:** 2507.07024. v1 9 Jul 2025, v2 11 Jul 2025, v3 2 Aug 2025, v4 23 Aug 2025. Read v4.
- **Link:** https://arxiv.org/abs/2507.07024
- **Code:** https://github.com/allenai/FlexOlmo. GitHub API: Apache-2.0, created 2025-06-05, last push 2026-04-20, not archived. Model hf.co/allenai/FlexOlmo-7x7B-1T (not opened).
- **Read status:** sections read: Abstract, 1, 2.2, 3 (3.1-3.3.3), 4 (4.1-4.4), 5 (5.1-5.4), App A.1-A.2, App D. Citations not chased.
- **Setting and scale:**
  - Continued pretraining of experts from a 7B dense OLMo-2-style public model (1T tokens).
  - Each data owner trains its expert for 50B tokens. Router tuning uses 5B tokens.
  - Final model: 37B total, 20B active (4 of 8 experts) (Sec 4.4).
  - Data split by domain (strongly non-IID by design). One-shot merge, no rounds.
- **Method** (Sec 3.3):
  - Each owner builds a 2-expert MoE: a frozen public expert plus its own expert, both initialized from the public FFN. Attention is shared and frozen ("training to coordinate").
  - Router rows: the public row is frozen. Each owner's row is initialized from a domain embedding (GritLM, average of 1,000 documents) and fine-tuned with its expert.
  - At merge, the rows are concatenated into the router.
  - A negative bias per non-public expert is added because "the model never directly compares experts M1 and M2 during training" (Sec 3.3.2, App D).
  - Optional: tune the router rows on proxy public data (Sec 3.3.3).
- **Key numbers** (Table 1, 4-expert setup, average over tasks):
  - FlexOlmo without router training: 46.7.
    - Without the bias: 45.8.
    - Without domain-embedding initialization and without the bias: 44.4.
    - **Without training to coordinate (no frozen anchor): 38.8.**
  - FlexOlmo with router training: 47.8.
  - Comparison methods:
    - Model soup: 39.6 (average) and 42.2 (weighted).
    - BTM: 43.4. BTX: 40.0 (post-merge training on public data only).
    - Unrestricted MoE at 2× FLOPs: 51.5. The 1× FLOPs row is split across two extracted lines; its average reads 46.3. Prose: FlexOlmo beats the FLOP-controlled MoE and "slightly underperforms" the data-controlled one.
  - My arithmetic: the anchor (coordinated training) is worth 7.9 points; router tuning 1.1; domain-embedding initialization 1.4; the bias 0.9.
  - Sec 5.1: with random router-row initialization, the learned rows end up "very similar to each other", which makes merging harder.
  - Sec 3.3.1: plain continued training of each expert "causes the experts to diverge too much from one another". Footnote 3 gives the same reason for the weak model-soup and BTX results.
- **Tags:**
  - [REMEDY | frozen shared anchor (public expert plus attention) during independent expert training | divergence and misrouting at merge (analog of masked routing) | 7B, 4-8 experts | continued pretraining | removing it: 46.7 → 38.8 | Table 1]
  - [REMEDY | router rows that travel with their expert, initialized from domain embeddings, plus negative bias | router rows collapsing to similar values; uncalibrated cross-expert logits | same | same | init +1.4, bias +0.9 | Table 1, Sec 5.1]
  - [REMEDY | router-only tuning after merge on proxy data | residual misrouting | same | same | +1.1 (46.7 → 47.8) | Table 1, Table 2]
- **Bears on:** Q2, Q5. Cost: masked routing +3.2%.
- **Differences from ours:**
  - One-shot, domain-split data, 7B continued pretraining from a strong dense model.
  - Each expert is held by one owner.
  - Shared parts are frozen rather than averaged.
- **Closest analog to our sliced arm in this strand** (inference): each FlexOlmo expert is trained under a router restricted to {public, own}, much as our worker's router is restricted to its 4 experts. In our coverage assignment, some expert pairs may never be co-held by any worker. Their relative logits are then never trained against each other, which is exactly the gap FlexOlmo's bias and frozen public row address.
- **Question for us:** do our averaged router rows for different experts become nearly parallel (high cosine) in the sliced arm compared with centralized training? That would match FlexOlmo's "very similar" rows and Task A's near-indifference to random routing.

### 4. DDOME (formerly Fed-ZERO, then FedJETs): Learning to Specialize: Joint Gating-Expert Training for Adaptive MoEs in Decentralized Settings

- **Authors (v3):** Yehya Farhat, Hamza ElMokhtar Shili, Fangshuo Liao, Chen Dun, Mirian Del Carmen Hipolito Garcia, Guoqing Zheng, Ahmed Hassan Awadallah, Robert Sim, Dimitrios Dimitriadis, Anastasios Kyrillidis. The v1 and v2 authors were Chen Dun, Mirian Hipolito Garcia, Guoqing Zheng, Ahmed Hassan Awadallah, Robert Sim, Anastasios Kyrillidis, Dimitrios Dimitriadis.
- **Year / venue:** 2023-2025, preprint ("Preprint. Under review." in v3).
- **arXiv:** 2306.08586. **Retitled twice** (titles verified on the abs pages):
  - v1, 14 Jun 2023: "Fed-ZERO: Efficient Zero-shot Personalization with Federated Mixture of Experts".
  - v2, 4 Oct 2023: "FedJETs: Efficient Just-In-Time Personalization with Federated Mixture of Experts".
  - v3, 3 Jun 2025: current title.
  - Read v3.
- **Link:** https://arxiv.org/abs/2306.08586
- **Code:** none found in the text.
- **Read status:** sections read: Abstract, meta-analysis card, 1, 2, 3 (Theorem 1 statement, not the proof), 4, 5 (setup and prose results), 6, App D-E.
- **Setting and scale:**
  - Experts are **whole models** (ResNet-34 for images, TinyBERT for text), 5-10 experts, plus a frozen pretrained "common expert" used as a feature extractor for the gate.
  - The gate is a 2-layer MLP. Each client receives the top-K = 2 experts ranked by the gate on its data.
  - 100 clients, 10% active per round (Na = 5 anchor + Nc = 5 normal), one local epoch, SGD, FedAvg aggregation; 1250-2000 rounds.
  - Data non-IID by class (CIFAR-10/100, EMNIST, Yahoo! Answers).
  - Supervised classification, mostly trained from scratch (image experts randomly initialized).
- **Findings:**
  - Theorem 1 (Sec 3; linear experts, top-1, Gaussian inputs): training experts with the gate frozen at initialization, and then training the gate, leaves the expected test loss bounded below by a constant. Joint gate-expert training is needed for specialization.
  - Sec 4 states the risk for clients that see only a subset of experts: wrong expert selection may "interfere with the specialization process by misaligning the experts".
  - App E: when clients are sampled at random (no anchor clients tied one-to-one to experts), DDOME "shows difficulty improving performance" because "experts' updates become inconsistent" (Fig 8; figure only).
  - App E: with a weak common expert, the gate "collapses to selecting a single expert". The breakpoint is about 66% common-expert accuracy on CIFAR-100 (prose, Fig 6-7).
  - Headline (Sec 1): DDOME about 95% / 78% / 75% on CIFAR-10 / CIFAR-100 / Yahoo! Answers for unseen clients, against about 71% / 74% / 69% for the second-best method. Table 1 is garbled in extraction and not used.
  - Table 6 (App E; experts initialized from the common expert, CIFAR-100, 2000 rounds): DDOME 83.27 vs FedAvg 73.99.
- **Tags:**
  - [REMEDY | frozen pretrained common expert as the gate's feature extractor (anchor) | gate collapse and inconsistent expert updates | ResNet-34/TinyBERT experts, 100 clients | from scratch for image experts | gate collapses below about 66% anchor accuracy | App E, Fig 6-7]
  - [REMEDY | anchor clients tied one-to-one to experts (pinned assignment) | inconsistent expert updates under random sampling | same | same | figure only | App E, Fig 8]
- **Bears on:** Q2 (theory that specialization needs joint gate-expert training; a stated risk for subset training), Q5 (anchors). Cost: masked routing +3.2% (by analogy).
- **Differences from ours:**
  - Whole-model experts, not FFN experts in a transformer.
  - Classification with class-skewed clients; a frozen external encoder drives the gate.
  - Specialization in DDOME comes *from* the non-IID data (the authors say implicit heterogeneity drives it). Under IID data that driver is absent (inference).
- **Question for us:** with IID data, what else could drive specialization in the sliced arm? Should we pin assignment (fixed expert-to-worker map, like anchor clients) instead of rotating it? Our coverage assignment may already be fixed; check.

### 5. FedMoE: Personalized Federated Learning via Heterogeneous Mixture of Experts

- **Authors:** Hanzi Mei, Dongqi Cai, Ao Zhou, Shangguang Wang, Mengwei Xu.
- **Year / venue:** 2024, preprint (no venue stated).
- **arXiv:** 2408.11304. Only v1, 21 Aug 2024. Read v1.
- **Link:** https://arxiv.org/abs/2408.11304
- **Code:** none found.
- **Read status:** full text.
- **Setting and scale:**
  - Fine-tuning pretrained Switch Transformers: 32 experts per layer for FedMoE and randomMoE, 8 for the other baselines.
  - 30 clients, 5 per round (or 3 forced to differ in task); client memory 18-24 GB.
  - Task-level heterogeneity (AG News, SQuAD, XSum on different clients), plus label skew in the "-TD" settings.
  - Local steps and number of rounds not stated in the text read.
- **Method:**
  - Stage 1: a short fine-tune collects expert activation frequencies; a heuristic search then picks a per-client sub-MoE under a memory budget.
  - Stage 2: federated training of the sub-MoEs with "modular aggregation": unactivated experts unchanged, single-holder experts copied, multi-holder experts averaged with FedAvg. Router dimensions are updated in the same pattern. Experts are added or pruned by similarity to other clients.
- **Key numbers:**
  - Prose (End-to-End Performance): average improvements of 7.63%, 15.50%, 10.00% and 12.74% over the best baseline in the four settings.
  - randomMoE is the baseline closest to our sliced arm: each client gets a **random expert subset**. Table 1 labels are shifted in extraction; I fixed the row order by checking it against the prose's memory and communication percentages, which fit only one assignment.
    - Standard-Hetero-T (task-heterogeneous): randomMoE 91.63 / 84.23 / 14.51 vs FedMoE 94.76 / 86.64 / 16.92. Metrics: TC accuracy / RC F1 / TS Rouge-2. FedMoE's row is confirmed by Table 2.
    - Standard-Hetero-TD (task plus label skew): randomMoE TC accuracy 34.19 vs FedMoE 88.44.
  - Robustness (prose): coefficient-of-variation index 0.1827 for randomMoE vs 0.0445 for FedMoE.
  - Fig 2 (figure only): a submodel of 4 random experts per layer "falls short" of 4 frequently activated ones and of the full 8.
- **Tags:**
  - [REMEDY | activation-informed expert subsets per client instead of random ones, with holder-only averaging of experts and router columns | wrong or arbitrary expert subsets | Switch, 30 clients | fine-tuning | +3.1 TC accuracy points (task-heterogeneous); +54 points under label skew, vs random subsets | Table 1(a,b)]
- **Bears on:** Q2 (random subsets vs informed subsets), Q5 (holder-only router rows: the same merge rule as ours, with no ablation of the router rule).
- **Differences from ours:**
  - Pretrained experts, so subsets can be chosen by measured activation; ours start from scratch.
  - Personalized evaluation; heavily non-IID.
  - No centralized baseline; no specialization metric.
- **Question for us:** our subsets are fixed by coverage, not by data. Under IID there is no data signal to choose from. Does that make every held subset equivalent and so push toward generalist experts (inference)?

### 6. FLEX-MoE: Federated Mixture-of-Experts with Load-balanced Expert Assignment for Edge Computing

- **Authors:** Boyang Zhang, Xiaobing Chen, Songyang Zhang, Shuai Zhang, Xiangwei Zhou, Jian Zhang, Mingxuan Sun.
- **Year / venue:** 2025-2026, preprint.
- **arXiv:** 2512.23070. v1 28 Dec 2025, titled "FLEX-MoE: Federated Mixture-of-Experts with Load-balanced Expert Assignment". v2 17 May 2026 adds "for Edge Computing". **Read v2.** The prior survey read v1 HTML.
- **Link:** https://arxiv.org/abs/2512.23070
- **Code:** none found.
- **Read status:** full text (v2; 6 pages).
- **Setting and scale:**
  - One MoE layer of E = 8 ResNet experts with a shared feature extractor, on CIFAR-10, EMNIST and GTSRB.
  - C = 20 clients, capacity k_c from 2 to 6 experts.
  - 100 rounds, R = 3 local training rounds per client.
  - IID, Dirichlet α = 0.8, and severe skew (2-class partition, Dirichlet α = 0.1).
  - **Gates are private per client and never aggregated.** The extractor is averaged with FedAvg; experts are averaged over the clients assigned to them, weighted by usage (Eq 3).
- **Key numbers** (Table I, IID; accuracy %, CV of expert load in brackets):
  - CIFAR-10: random assignment 72.03 (0.027) vs FLEX-MoE 79.48 (0.003, accuracy-driven) and 83.00 (0.003, loss-driven); greedy top-k 78.44 (0.310) and 78.71 (0.298).
  - EMNIST: random 97.48 vs 98.33 / 98.08.
  - GTSRB: random 57.34 vs 98.00 (accuracy-driven) / 76.48 (loss-driven); loss-greedy 90.88. Prose concedes greedy wins in this case.
  - Table II (severe skew, CIFAR-10): random 7.19 (2-class) and 23.42 (α = 0.1) vs FLEX-MoE 61.00 / 67.60 (accuracy-driven).
- **Tags:**
  - [REMEDY | load-balanced, fitness-scored expert assignment solved as a linear program | random or greedy assignment of expert subsets | 8 ResNet experts, 20 clients | from-scratch classification | IID CIFAR-10 +7.4 to +11.0 pts over random assignment; expert-load CV 0.003 vs about 0.3 for greedy | Table I]
- **Bears on:** Q2 (the only expert-subset paper here with an **IID** condition), Q5 (assignment policy). Cost: masked routing +3.2% (assignment side).
- **Differences from ours:**
  - Vision, a single MoE layer, private routers, and a fresh random draw of expert subsets each round.
  - **No centralized or full-model baseline**, so the cost of subset training itself cannot be read off. Only assignment policies are compared.
- **Question for us:** under IID data, random per-round assignment loses 7-11 points to a fitness-based assignment on CIFAR-10. Would a data-free but *stable* assignment (ours) sit closer to the random or the fitness-based end?

### 7. FedMoE-DA: Federated Mixture of Experts via Domain Aware Fine-grained Aggregation

- **Authors:** Ziwei Zhan, Wenkuan Zhao, Yuanqing Li, Weijie Liu, Xiaoxi Zhang, Chee Wei Tan, Chuan Wu, Deke Guo, Xu Chen.
- **Year / venue:** 2024. MSN 2024 (20th International Conference on Mobility, Sensing and Networking), per the arXiv comment.
- **arXiv:** 2411.02115. v1 4 Nov 2024, v2 27 Dec 2024. Read v2.
- **Link:** https://arxiv.org/abs/2411.02115. DOI not checked.
- **Code:** none found.
- **Read status:** full text (8 pages).
- **Setting:**
  - Small CNN: the first conv layer is a shared "embedding model"; the remaining layers form K_i = 4 private experts per client, top-1.
  - N = 50 clients with 500 samples each; E = 5 local epochs; 1000 rounds.
  - MNIST, EMNIST, CIFAR-10, SVHN; homogeneous, pathological and Dirichlet splits.
- **Method:**
  - Gates and experts are private. The server compares clients' gate columns ("proxies", one per expert) by cosine similarity.
  - Each expert is averaged peer-to-peer with its P most similar experts on other clients, using softmax weights over the similarities (Eq 8-11).
- **Findings** (prose; Table II and III extractions are garbled, so no cells are used):
  - FedMoE-DA "does not achieve the highest accuracy in most distributions" but is close to the best across all of them.
  - Scaffold is best on the homogeneous split.
  - P = 0 (no expert aggregation) gives significantly lower accuracy, and P = all also degrades (Fig 3; figure only).
- **Tags:**
  - [REMEDY | similarity-based expert merging, using router columns as the expert's identity | expert mismatch across clients | small CNN, 50 clients | from scratch | figure only | Fig 3]
- **Bears on:** Q5 (router rows as a signature of expert identity: a variant of "router rows that travel with their expert").
- **Differences from ours:** a tiny vision CNN, personalized evaluation, no shared expert indices.
- **Question for us:** could the cosine between holders' copies of an expert's router row predict how much that expert gains or loses from averaging?

### 8. HFedMoE: Resource-aware Heterogeneous Federated Learning with Mixture-of-Experts

- **Authors:** Zihan Fang, Zheng Lin, Senkang Hu, Yanan Ma, Yihang Tao, Yiqin Deng, Xianhao Chen, Yuguang Fang. Same group as FedAlign-MoE.
- **Year / venue:** 2026, preprint.
- **arXiv:** 2601.00583. Only v1, 2 Jan 2026. Read v1.
- **Link:** https://arxiv.org/abs/2601.00583
- **Code:** none found.
- **Read status:** sections read: Abstract, I, II (motivation), III-A/B, III-E (aggregation), IV (setup), V-C3 (aggregation ablation, prose).
- **Setting:**
  - Fine-tuning Switch-base-64 (top-1) and DeepSeek-MoE-16B (QLoRA rank 8).
  - **C = 4 clients**, batch size 8, learning rate 1e-4.
  - Compute budgets of 12-32 GB force about half the clients to train an expert subset.
  - **Data partition not stated** in the sections read; the system model says only that each client's data comes from a distinct distribution.
- **Findings:**
  - Sec II-C (Fig 4; Switch-8, AGNews): about 25% of experts are never activated on any client, over 20% are chosen by different clients, and local accuracy falls after FedAvg aggregation (figure only).
  - Remedy: average only actively trained experts (usage above a threshold), and average gates with client weights from dominant-expert overlap times expert importance (Eq 17-21).
  - Ablation (Fig 16; prose only): the full method beats selective expert aggregation without gate weighting, which beats plain FedAvg. No numbers in the text.
  - Headline (prose): accuracy above 94%, 81%, 72% and 45% on AGNews, PIQA, HellaSwag and MMLU.
- **Tags:**
  - [REMEDY | sparsity-aware aggregation (only active experts) plus importance-weighted gate averaging | partial expert updates and inconsistent gates | Switch-64 / DeepSeek-MoE-16B, 4 clients | fine-tuning | figure only | Fig 16]
- **Bears on:** Q2 ("client-specific expert subsets" from resource limits, the closest motivation to our capacity-driven slices), Q5.
- **Differences from ours:** fine-tuning, top-1, undisclosed data split, no centralized baseline.
- **Question for us:** does our holder-only averaging already do what their "only active experts" rule does? Yes for experts; not for gate weighting (inference).

### 9. FLEx: Personalized Federated Learning for Mixture-of-Experts LLMs via Expert Grafting

- **Authors:** Fan Liu, Bikang Pan, Zhongyi Wang, Xi Yao, Zhichao Sheng, Jingya Wang, Xiaoying Tang, Ye Shi.
- **Year / venue:** 2025, preprint ("Preprint. Under review." in v2).
- **arXiv:** 2506.00965. v1 1 Jun 2025, titled "Unlocking Personalized Knowledge in Federated Large Language Model: The Power of Mixture of Experts". v2 7 Oct 2025, retitled. Read v2.
- **Link:** https://arxiv.org/abs/2506.00965
- **Code:** anonymous.4open.science/r/FLEx-8F12 (not opened; no licence known).
- **Read status:** sections read: Abstract, 1, 4 (4.1-4.3), 5 (5.1-5.3).
- **Setting:**
  - Fine-tuning Qwen1.5-MoE-A2.7B with LoRA (rank 32), Databricks-dolly-15k.
  - Pathological non-IID: one task per client (4 tasks). Dirichlet α = 0.1 and 1.0 with 10 clients. An IID Vicuna evaluation with 20 clients.
  - 100 rounds, **5 local steps** per round, OpenFedLLM framework.
- **Method:** pretrained experts and the original router are frozen; only non-expert parameters are averaged; each client grafts one pretrained expert as a personal expert with a sigmoid gate.
- **Key numbers** (ROUGE-L):
  - Table 4 (pathological non-IID):
    - Train all experts, share everything: 41.17. Train activated experts, share everything: 40.75.
    - Train all experts, share only non-experts: 41.40. Train activated experts, share only non-experts: 41.30. The assignment of these two rows was inferred from the cost columns; the prose confirms "row 1 vs. 3 and 2 vs. 4".
    - FLEx: 43.13.
    - Authors: "naively aggregating all client experts induces destructive interference".
    - My arithmetic: not averaging experts gains +0.23 to +0.55.
  - Table 2:
    - α = 0.1: FedAvg 35.29, FLEx 37.30, FedAvgM 37.41, local training only 35.18.
    - α = 1.0: FedAvg 37.51, FLEx 37.54, local only 36.88.
    - The method's advantage vanishes as heterogeneity drops.
  - Table 3: inserting the grafted expert without the gate collapses ROUGE-L to 5.16 and 7.06.
- **Tags:**
  - [REMEDY | freeze pretrained experts and average only the shared non-expert parameters | expert interference under averaging | Qwen1.5-MoE-A2.7B, 4-10 clients, 5 local steps | fine-tuning | +0.23 to +0.55 ROUGE-L vs averaging experts (pathological non-IID); gap about 0 at α = 1.0 | Tables 2 and 4]
- **Bears on:** Q2 (non-IID dependence), Q5 (frozen experts as an anchor).
- **Differences from ours:** pretrained experts exist; we train from scratch, so experts cannot be frozen.
- **Question for us:** none directly. Its IID-direction result (α = 1.0, gap about 0) suggests our IID setting removes this failure mode (inference).

### 10. BAR: Train Separately, Merge Together: Modular Post-Training with Mixture-of-Experts

- **Authors:** Jacob Morrison, Sanjay Adhikesaven, Akshita Bhagia, Matei Zaharia, Noah A. Smith, Sewon Min.
- **Year / venue:** 2026, preprint.
- **arXiv:** 2604.18473. Only v1, 20 Apr 2026. Read v1.
- **Link:** https://arxiv.org/abs/2604.18473
- **Code:** no link found in the text.
- **Read status:** sections read: Abstract, 1, 2, 3, 4, 5 (5.1-5.3), 6. Likely a FlexOlmo citer, so it may overlap with the FlexOlmo citation chase.
- **Setting:**
  - Post-training (mid-training, SFT, RLVR) of a 7B OLMo-2 model.
  - Four domain experts (math, code, tool use, safety), each trained as a 2-expert MoE (frozen anchor FFN plus domain FFN), merged into a 5-expert MoE.
  - Shared layers that diverged are **averaged** across the domain models. **Router-only training** follows on a stratified 5% of the SFT data.
- **Key numbers:**
  - Table 1: BAR 49.1 overall; BTX 46.7; dense merging 6.5 (with mid-training) and 36.9 (without); re-training 47.8 (post-train only) and 50.5 (mid+post).
  - Sec 3.3: averaging the diverged shared layers "introduces little to no measurable performance loss".
  - Table 5 (active experts out of 5): 1 → 31.1, 2 → 38.8, 3 → 36.8, 4 → 48.2, 5 → 49.1.
  - Sec 5.3: freezing shared layers (the FlexOlmo recipe) fails for post-training. Tool use reaches 20.3 frozen vs 46.4 unfrozen.
  - No ablation of the router-only step itself.
- **Tags:**
  - [REMEDY | router-only training after merging, all other weights frozen | misrouting at merge | 7B, 5 experts | post-training | not ablated; method total +2.4 over BTX | Table 1, Sec 3.3]
  - [REMEDY (negative) | frozen shared layers during expert training | n/a | 7B | post-training | hurts: 20.3 vs 46.4 on tool use | Sec 5.3]
- **Bears on:** Q5 (router-only refit, averaging shared parts after independent training).
- **Differences from ours:** one-shot, post-training, a large pretrained base, domain experts.
- **Question for us:** BAR's anchor is a frozen *expert*, not frozen shared layers. Would one always-held, centrally trained shared expert anchor our routers (inference)?

### 11. Router KD: Is Retraining-Free Enough? The Necessity of Router Calibration for Efficient MoE Compression

- **Authors:** Sieun Hyeon, Jaeyoung Do.
- **Year / venue:** 2026, preprint (the PDF says "Preprint. March 4, 2026").
- **arXiv:** 2603.02217. Only v1, 10 Feb 2026. Read v1.
- **Link:** https://arxiv.org/abs/2603.02217
- **Code:** none found.
- **Read status:** sections read: Abstract, 1, 3.4 (summary), 4 (setup and results prose), 4.x on coarse-grained experts and collapse, 5. Appendix G numeric tables **not read**.
- **Setting:**
  - Expert pruning, editing and **merging** (M-SMoE among others) of Qwen3-30B-A3B (128 experts) and Mixtral-8x7B (8 experts, top-2).
  - Then router-only distillation from the original model's next-token distribution on unlabeled calibration data.
- **Findings** (prose):
  - Router KD improved scores for Qwen3 across all six compression methods, "the performance gains were relatively marginal for Mixtral".
  - The authors attribute this to the small top-k routing space with 8 experts and to near-hard teacher routing.
  - Router KD gives **no** recovery when compression causes catastrophic collapse.
- **Tags:**
  - [REMEDY | router-only knowledge distillation after expert merging, pruning or editing | router-expert mismatch | Qwen3-30B-A3B (fine-grained) vs Mixtral-8x7B (coarse, 8 experts) | post-hoc on pretrained models | consistent gains on 128-expert MoE; marginal on 8-expert MoE | Sec 4 prose, Fig 3]
- **Bears on:** Q5. (inference) Our model is coarse-grained (8 experts, top-2), so this predicts a small ceiling for a central router-only refit.
- **Differences from ours:** compression of a pretrained model, not training.
- **Question for us:** if a router-only refit after our final merge recovers little, that would point the masked-routing cost at the experts, not the gate.

### 12. FedCoE: Bridging Generalization and Personalization via Federated Coordinated Dual-level MoEs

- **Authors:** Penglin Dai, Fulian Li, Xincao Xu, Junhua Wang, Lixin Duan, Xiao Wu.
- **Year / venue:** 2026, preprint.
- **arXiv:** 2605.21264. Only v1, 20 May 2026. Read v1.
- **Link:** https://arxiv.org/abs/2605.21264
- **Code:** none found.
- **Read status:** sections read: Abstract, I, III (motivation and preliminary experiment), V-A setup.
- **Setting:** ResNet-18-MoE (K = 2 experts per residual block), CIFAR-10. Main experiments: N = 10 clients, 1000 rounds. The preliminary experiment's client count is not stated in what I read.
- **Findings** (Sec III, Observations 1-2; clients hold all experts, FedAvg):
  - IID: ResNet-MoE 81.51% vs dense ResNet 78.93%.
  - Non-IID (α = 0.1): ResNet-MoE 50.60% vs dense 55.78%.
  - The authors attribute the non-IID loss to "Expert Drift" and "Gating Inconsistency".
  - Remedy: a server-side shared gate pre-trained on public data (an anchor) and correlation-weighted expert aggregation. Not evaluated here.
- **Tags:** none (no ablation numbers recorded).
- **Bears on:** Q2, as the clearest IID-vs-non-IID contrast for averaged MoE: the MoE gains over dense under IID and loses under skew.
- **Differences from ours:** vision, 2 experts per block, all experts held by every client.
- **Question for us:** our IID full-averaging arm already gives +6.1%. Does the sliced arm's extra +3.2% behave like "IID with structural heterogeneity", a case no paper covers?

### 13. MedMix: Specialization-Consistent Federated Sparse MoEs under Modality Heterogeneity

- **Authors:** Adiba Orzikulova, Dong Min Kim, Jaehong Yoon, Sung-Ju Lee.
- **Year / venue:** 2026, preprint.
- **arXiv:** 2608.13911. Only v1, 14 Aug 2026. Read v1.
- **Link:** https://arxiv.org/abs/2608.13911
- **Code:** none found.
- **Read status:** sections read: Abstract, 1, 2 (fragility analysis), experiments prose (setup, cross-client analysis, ablation).
- **Setting:** multimodal medical classification (ADNI, MIMIC-IV) with modality heterogeneity across clients; 150 rounds, one local epoch, Adam, load-balancing loss.
- **Findings:**
  - Routing divergence measured as support-weighted **Jensen-Shannon divergence** between clients' routing distributions (Fig 2a). Their modality-context routing cuts it "by more than an order of magnitude".
  - Expert drift measured as prototype-weighted **cosine drift** between local and aggregated experts (Fig 2b).
  - Ablation (Table 3, ADNI, prose): average F1 0.523 (base) → 0.530 (full). Modality-exclusive setting: 0.446 → 0.481.
- **Tags:**
  - [REMEDY | consensus routing anchors plus prototype-matched expert aggregation | routing divergence and expert drift | multimodal medical, small | from scratch / supervised | +0.007 average F1; +0.035 in the hardest setting | Table 3]
- **Bears on:** Q2 (gives two **metrics** we could log: JS divergence of per-worker routing and cosine drift of same-index experts).
- **Differences from ours:** modality heterogeneity, classification.

### 14. Symphony-MoE: Harmonizing Disparate Pre-trained Models into a Coherent Mixture-of-Experts

- **Authors:** Qi Wang, Hanyang Peng, Yue Yu.
- **Year / venue:** 2025, preprint (venue not stated in the parts read).
- **arXiv:** 2509.18542. v1 23 Sep 2025, v2 12 Nov 2025. Read v2.
- **Link:** https://arxiv.org/abs/2509.18542
- **Code:** none found.
- **Read status:** sections read: Abstract, 4.6 (CKA analysis), 4.7 (ablation), 5.
- **Setting:** upcycling an MoE from **different** pretrained dense models (Qwen2/2.5 0.5B and 1.5B, Llama 3.2 1B), with permutation (functional) alignment of FFN neurons before merging, then router training.
- **Findings:**
  - Table 3 (1.5B × 4): in-distribution average 44.07 with alignment vs 33.94 without; out-of-distribution 35.26 vs 26.92.
  - Sec 4.6: naive merging inflates inter-expert CKA to about 0.65-0.75, "blurred into a redundant subspace".
- **Tags:**
  - [REMEDY | neuron permutation alignment before merging | expert redundancy and blurring when merging unaligned experts | 0.5-1.5B × 4 | upcycling / fine-tuning | in-distribution +10.1 pts | Table 3]
- **Bears on:** Q5 (permutation alignment).
- **Difference from ours** (inference): our copies of an expert share an initialization and are re-averaged every 125 steps, so their neurons should stay aligned. Permutation alignment is probably irrelevant to our cost.

### 15. Briefly opened, no numbers recorded

- **FC-MoE: Conflict-Aware Federated Fine-Tuning of Large Language Models with Mixture-of-Experts.**
  - Yijun Lu, Zihan Fang, Pengpeng Qiao, Zheng Lin, Jing Yang, Yuxin Zhang, Por Lip Yee, Zhe Chen, Jun Luo. arXiv 2606.15625, only v1, 14 Jun 2026.
  - Abstract, introduction and setup read: 10 clients, one epoch per round, Dirichlet non-IID, importance-weighted expert averaging with gradient consensus projection.
  - Same group as FedAlign-MoE and HFedMoE. Non-IID fine-tuning, so of low relevance to us.
- **NMoE: Towards Efficient Federated Learning of Networked Mixture-of-Experts for Mobile Edge Computing.**
  - Song Gao et al. arXiv 2511.01743. v1 3 Nov 2025, v2 8 Mar 2026. Abstract only.
  - Clients act as whole-model experts for each other. Not relevant to FFN-expert slicing.

## Synthesis for question 2 (federated and merged MoE) and router remedies

### How much each paper's failure depends on non-IID data (our runs are IID)

| Paper | Data regime | Failure shown under IID? | Verdict for our IID case (inference unless stated) |
|---|---|---|---|
| FedAlign-MoE 2603.21276 v2 | Dirichlet α = 0.1 (main); α = 0.5 and 1.0; IID column | Yes, partly. Switch AGNews: remedy gain over FedAvg is +1.6 pts IID vs +7.8 at α = 0.1; MMLU +4.9 IID (Table I). Authors call IID methods "comparable". | Mostly a non-IID effect. A residual gap remains under IID on harder tasks. |
| FedCoE 2605.21264 | IID and α = 0.1 | No: averaged MoE beats dense under IID (81.51 vs 78.93) and loses under α = 0.1 (50.60 vs 55.78). | Averaging full MoEs is not harmful under IID. Silent on subsets. |
| FLEx 2506.00965 | Pathological; α = 0.1 and 1.0; IID Vicuna | Shrinks to about 0: FLEx vs FedAvg 37.54 vs 37.51 at α = 1.0 (Table 2). | Expert interference from averaging is a non-IID effect. |
| FLEX-MoE 2512.23070 v2 | IID, α = 0.8, severe skew | Assignment matters under IID (random vs fitness-based: −7 to −11 pts on CIFAR-10). No full-model or centralized baseline. | The only IID evidence on expert subsets. Cannot size the subset cost itself. |
| HARC 2606.03391 | Task-split fine-tunes (math vs code) | Not tested. | Fully heterogeneous sources. Mechanism (softmax/top-k sensitivity) is data-independent; magnitude is not transferable. |
| FlexOlmo 2507.07024; BAR 2604.18473; Symphony-MoE 2509.18542 | Domain-split, one-shot merges | Not tested. | Strongly non-IID. Only mechanisms transfer. |
| FedMoE 2408.11304; FedMoE-DA 2411.02115; DDOME 2306.08586; MedMix 2608.13911; FC-MoE 2606.15625 | Task, label, class or modality skew | Not tested. FedMoE-DA has a homogeneous split, where its own method is not best (prose). DDOME's specialization is driven by the skew itself. | Non-IID only. |
| HFedMoE 2601.00583 | Not stated in the sections read | Unknown. | Cannot judge. |

### What the literature measures

1. **Two named failure modes, both defined under non-IID data.**
   - "Gating (preference) misalignment" (FedAlign-MoE Sec II-A; HFedMoE Sec II-A/C; FedCoE "Gating Inconsistency"; MedMix routing divergence). Clients' gates learn different preferences from different data, and the averaged gate fits none of them.
   - "Expert semantic blurring" or "expert drift" (FedAlign-MoE Sec II-B; FedCoE; MedMix). Same-index experts trained on different data learn different functions, and averaging blurs them.
   - Every paper demonstrates these with Dirichlet α = 0.1, task-level or modality splits. The demonstrations are figures: t-SNE plots and before/after-aggregation accuracy bars. **No paper in this strand reports a numeric divergence metric for these failure modes in its main text, except MedMix** (JS divergence and cosine drift, plotted only).
2. **The failures shrink sharply when data move toward IID** (direct evidence, four papers):
   - FedAlign-MoE (Switch AGNews): the remedy's gain over FedAvg is +7.8 points at α = 0.1, +3.8 at α = 1.0 and +1.6 under IID (Table I, Table II). The authors say IID methods are "comparable".
   - The IID MMLU gap is still +4.9 points (0.4641 vs 0.5131), so "comparable" does not hold on every task.
   - FedCoE: averaged MoE beats dense under IID (81.51 vs 78.93) and loses under α = 0.1 (50.60 vs 55.78).
   - FLEx: its advantage over FedAvg is 2.0 ROUGE-L at α = 0.1 and 0.03 at α = 1.0 (Table 2).
   - (inference) Blurring requires same-index experts to *diverge* during local training. With IID data and H = 125, our copies of an expert see the same distribution, so this mechanism should be weak. It probably does not explain Task A's generalist experts.
3. **Routing breakdown after merging is real and large at the decision level, but recovery is modest.**
   - HARC: 50.11% of expert selections deviate, 99.98% of tokens are affected somewhere, and the deviation concentrates in deep layers.
   - Its calibration recovers about 9% of the weight-averaging gap and about 45% of the WUDI gap on OLMoE (my arithmetic from Table 1). At Qwen3-30B-A3B scale the whole merging gap is under 1 point.
   - (inference) The proposed mechanism (softmax of averaged logits is not the average of softmaxes, and top-k turns small shifts into different selections) applies to us whenever router rows are averaged. In our case the bigger change is structural: local top-2 over 4 experts becomes top-2 over 8 after the merge.
4. **Subset (slice) training under IID**: the only direct evidence is FLEX-MoE Table I.
   - Random per-round expert subsets lose 7-11 points on CIFAR-10 (and up to 41 on GTSRB) to fitness-based subsets.
   - There is no full-model or centralized baseline, private routers are never averaged, and the model is vision. **It cannot size the cost of subset training itself.**
   - FedMoE's randomMoE (non-IID, task-level) also trails informed subsets, by +3.1 TC accuracy points and by 54 points under label skew.

### Direct evidence that a restricted per-worker router yields generalist or redundant experts

**Not found in this search.** No paper in this strand measures expert interchangeability (accuracy under random routing, or per-expert ablation) after training under a restricted per-worker router. The search covered:

- The federated-MoE papers listed above, read in the text.
- Web searches on federated, decentralized and merged MoE, gating misalignment, expert redundancy, router calibration and expert-subset training (query log below).

The closest items:

- **DDOME** Theorem 1: decoupled gate-then-expert training cannot specialize in a linear-Gaussian toy. Sec 4 names the risk that wrong subset selection misaligns experts. App E: without pinned anchor clients, expert updates become inconsistent (figure only).
- **FlexOlmo** Sec 5.1: router rows trained in isolation from a random initialization end up "very similar to each other". Removing coordinated (anchored) training costs 7.9 points.
- **Symphony-MoE**: merging unaligned experts inflates inter-expert CKA ("redundant subspace"). But its experts come from different pretrained bases.

(inference) The FlexOlmo observation is the closest mechanism to Task A. A router row trained only against a fixed subset of companions, on data that offer no reason to separate experts (IID), may converge toward similar directions. Averaging then yields near-uniform gates and interchangeable experts. This is a hypothesis to test, not a finding.

### Where papers disagree

- **Freezing shared layers during independent expert training.**
  - FlexOlmo: essential (pretraining; −7.9 without).
  - BAR: harmful for post-training (20.3 vs 46.4 on tool use). BAR keeps a frozen anchor *expert* but unfreezes shared layers and averages them afterwards.
  - FLEx: freezing pretrained experts and averaging only non-expert parameters beats averaging experts by a small margin (non-IID fine-tuning).
- **Should routers be averaged at all?**
  - FLEX-MoE and FedMoE-DA keep routers private (sidestepping the problem).
  - FedMoE averages router columns over holders (our rule).
  - FedAlign-MoE and HFedMoE use weighted or regularized routers.
  - FlexOlmo concatenates per-expert rows (no averaging).
  - None compares these head to head in the same setting.
- **Post-merge router fixes.**
  - HARC: full SFT barely fixes routing (+0.27) and raises routing KL; targeted calibration does better (+0.88).
  - FlexOlmo: router-only tuning +1.1. BAR relies on router-only training without ablating it.
  - Router KD: router-only recovery is marginal for coarse 8-expert MoEs.

### Remedies with evidence (strength of evidence in this strand; not a recommendation)

1. **Frozen anchor or coordinated training.** FlexOlmo, −7.9 points without it (7B continued pretraining, one-shot); DDOME's common-expert breakpoint; FedCoE's shared gate (not ablated). One clear ablation, at a scale and in a setting far from ours. Contradicted for post-training by BAR.
2. **Post-merge router recalibration or refit.**
   - HARC: +0.17 to +0.88 (OLMoE), +0.27 to +0.64 (Qwen3).
   - FlexOlmo router tuning: +1.1.
   - Router KD: marginal on 8-expert models.
   - Effects are consistent but small. The coarse-MoE caveat applies to us.
3. **Router rows that travel with their expert.** FlexOlmo: domain-embedding initialization +1.4, bias +0.9. FedMoE uses holder-only router columns (not ablated). FedMoE-DA uses router columns as the expert's identity for merging (figure only).
4. **Informed or balanced assignment of expert subsets.** FLEX-MoE (+7 to +11 points over random under IID, vision); FedMoE (vs randomMoE). Our harness already supports assignment policies.
5. **Similarity- or semantics-gated expert aggregation.** FedAlign-MoE (figure only); FedMoE-DA (figure only); MedMix (+0.007 F1). Weak evidence, all non-IID.
6. **Permutation alignment.** Symphony-MoE (+10.1 points, but with different base models). Probably irrelevant to shared-initialization averaging (inference).
7. **Routing a fraction of tokens to non-held experts.** No paper in this strand (SPES, which does this with frozen copies, is excluded).
8. **Knowledge distillation.** Only Router KD (compression setting). No federated-MoE distillation paper was read.

### Unknown or silent

- Every paper here fine-tunes a pretrained model, or trains a vision or classification model, except FlexOlmo and BAR (continued pretraining and post-training at 7B). **None pretrains a language MoE from scratch with expert subsets per worker and iterative averaging.**
- None compares against a centralized baseline at equal compute. They compare against FedAvg variants.
- None separates "data heterogeneity" from "structural heterogeneity" (different held subsets on IID data), which is our case.
- None measures expert interchangeability.
- No paper here reports how the routing failure scales with local steps H.

## Candidates for the joint reading list

1. **HARC (arXiv 2606.03391, ICML 2026).** The clearest quantified account of why averaged routers misroute (softmax/top-k nonlinearity, deep-layer accumulation), with a post-merge remedy and a measured comparison against SFT. *Foundational for the router mechanism; read early.*
2. **FlexOlmo (arXiv 2507.07024).** The only paper here where each expert's router row is trained under a restricted router and the consequences are ablated (anchor −7.9, router initialization, bias, router tuning +1.1). *Foundational; read early.* Its citations are covered by another researcher.
3. **FedAlign-MoE (arXiv 2603.21276 v2).** Names "gating misalignment" and "expert semantic blurring" and includes an IID column showing how much of the failure depends on non-IID data. *Specific; read later.* Cite v2: v1 numbers and caption differ, and the title and authors changed.
4. **DDOME / FedJETs / Fed-ZERO (arXiv 2306.08586 v3).** Theory that specialization needs joint gate-expert training, and anchor clients as a fix for inconsistent expert updates when clients see expert subsets. *Foundational for the "why specialize at all" question; read early, mainly Sec 3-4 and App E.*
5. **Router KD (arXiv 2603.02217).** Router-only calibration helps fine-grained MoEs but only marginally 8-expert ones; a direct caveat for a central router refit at our scale. *Specific; read later.* Alternate: FLEX-MoE (2512.23070), the only expert-subset paper with an IID condition.

## Gaps

These are questions no paper answers. Items 1-5 and 7-8 are measurements on runs the harness can already do (other H, Nesterov outer momentum, slice sizes, worker counts, assignment policies, partial/full/sliced modes, skewed data, worker dropout). Item 6 and the router remedies need new code; their logging needs only a small hook.

1. **IID vs skewed data across the three arms.** FedAlign-MoE and FedCoE predict that gating misalignment and expert blurring grow with skew. Does our masked-routing cost (sliced vs partial) grow under skew? Or is it mainly structural, and so present under IID? This is the strongest use of the harness, because no paper separates the two.
2. **Masked-routing cost vs H.** HARC ties breakdown to the size of the parameter perturbation. Does the sliced-minus-partial gap grow with H at fixed total compute?
3. **Slice size curve.** Vary the number of held experts (for example 2, 4 or 6 of 8) to interpolate between sliced and partial. No paper gives this curve.
4. **Assignment policy.** Fixed coverage (pinned, like DDOME's anchor clients) vs rotating vs random redraw per round (FLEX-MoE's weak baseline). Measure the effect on interchangeability (random-routing accuracy, expert ablation) as well as on loss.
5. **Worker count and number of holders per expert,** at fixed slice size. Is blurring tied to the number of holders averaged?
6. **Logging hooks the papers suggest:**
   - per-merge cosine of same-index expert updates across holders (FedAlign-MoE Eq 13);
   - JS divergence between workers' routing distributions (MedMix);
   - HARC-style decision mismatch between local top-2 over 4 and merged top-2 over 8;
   - cosine similarity among router rows, a test of FlexOlmo's "very similar rows".
7. **Nesterov outer momentum applied to router rows.** Does it change routing mismatch? No federated-MoE paper here tests an outer optimizer.
8. **Worker dropout:** experts that temporarily have one holder. No paper here measures this for routing.

## Could not verify

- **MergeME** (arXiv 2502.00997, NAACL 2025 per arXiv comment). Metadata only (API); not read. Router heuristics vs post-merge fine-tuning when merging dense experts into an MoE.
- **"Flexible and Effective Mixing of Large Language Models into a Mixture of Domain Experts"** (arXiv 2408.17280). Metadata only; router-training ablation not read.
- **Seen only in search results or reference lists, not opened:**
  - EMO (arXiv 2605.06663; centralized, per its listing title only); FFT-MoE (arXiv 2508.18663); pFedMoE (arXiv 2402.01350).
  - dFLMoE (CVPR 2025); PM-MoE (WWW 2025); FedVLA (arXiv 2508.02190); IJCAI 2025 server-side MoE federated paper.
  - "FedMoE: Efficient Federated Fine-Tuning for MoE-Based Large Language Models" (ICWS 2026; a different paper from 2408.11304).
  - Fed-MoE via Empirical Pruning (Springer); "Revisiting sparse mixture of experts for resource-adaptive federated fine-tuning foundation models" (ICLR 2025 workshop, cited by FLEX-MoE ref [15]).
  - Grouter (arXiv 2603.06626); M-SMoE / MC-SMoE (ICLR 2024); REAM (2026); FURINA (arXiv 2509.14900); TT-LoRA MoE (arXiv 2504.21190).
  - Connito whitepaper (a company page, not a paper); Mosaic (arXiv 2505.19699).
- **FedMix** (arXiv 2107.06724): search snippet only (the prior survey had it at abstract level).
- **Tables used only through prose** (cells garbled in extraction):
  - FedMoE-DA Tables II-III; DDOME Table 1.
  - HARC Table 1 rows for TIES, DARE and Fisher (by row order only).
  - FedAlign-MoE v2 Table II MMLU columns; FlexOlmo Table 1 individual-expert rows and the 1× FLOPs MoE row (split across lines).
- **Figure-only effects** (no numbers taken): FedAlign-MoE Fig 3b, 4d, 16, 17; HFedMoE Fig 4b, 16; DDOME Fig 8; FedMoE Fig 2; FedMoE-DA Fig 3.
- **Router KD** numeric tables (Appendix G) not read; only the prose conclusions are used.
- **Licences not established:** HARC repository (API licence null); FLEx anonymous code link not opened; no code found for FedAlign-MoE, HFedMoE, FLEX-MoE, FedMoE, FedMoE-DA, DDOME, BAR, FedCoE, MedMix, Symphony-MoE.

## Query log

All times are TST (UTC+3) on 2026-10-11, from the `date` command. Individual search timestamps were not captured one by one; they fall in the windows shown.

| Time | Tool / site | Query or request |
|---|---|---|
| 10:28:49 | Bash `date` | session start |
| 10:29:00 | export.arxiv.org API | id_list = 2603.21276, 2606.03391, 2512.23070, 2306.08586, 2408.11304, 2507.07024, 2411.02115, 2601.00583, 2506.00965 |
| 10:29-10:31 | arxiv.org/pdf (sleep 3 between requests) | PDFs of the 9 IDs above |
| 10:33:44-10:34:50 | WebSearch (extended) | `federated mixture of experts pretraining clients hold subset of experts language model 2026` |
| same window | WebSearch | `decentralized MoE training expert subsets per node routing masked merge` |
| same window | WebSearch | `MoE model merging router fine-tuning expert alignment arXiv 2025` |
| same window | WebSearch | `"expert specialization" federated MoE IID versus non-IID experts redundant after aggregation` |
| same window | WebSearch (extended) | `decentralized mixture-of-experts language model pretraining heterogeneous GPUs each worker trains experts local steps 2025 2026 arXiv` |
| same window | WebSearch | `"gating misalignment" OR "routing misalignment" federated mixture of experts aggregation` |
| same window | WebSearch | `merging mixture-of-experts models expert permutation alignment router merging` |
| same window | WebSearch | `independently trained experts merged into MoE router-only fine-tuning recovers performance ablation` |
| same window | WebSearch (extended) | `federated MoE language model training from scratch expert sharding clients local SGD routing restricted to local experts` |
| same window | WebSearch | `MoE training experts dropped or unavailable routing restricted subset experts generalist experts specialization lost` |
| same window | WebSearch | `federated mixture of experts knowledge distillation router server-side calibration proxy data 2025` |
| 10:34:50 | export.arxiv.org API | id_list = 2604.18473, 2605.21264, 2608.13911, 2603.02217, 2606.15625, 2509.18542, 2502.00997, 2511.01743, 2408.17280 |
| 10:35-10:36 | arxiv.org/pdf (sleep 3) | 2604.18473, 2605.21264, 2608.13911, 2603.02217, 2606.15625, 2509.18542, 2511.01743 |
| 10:36:56 | api.github.com | repos/huangcb01/HARC, repos/allenai/FlexOlmo |
| about 10:37-10:39 | WebSearch | `DiLoCo mixture-of-experts local updates router drift expert specialization outer optimizer MoE` |
| about 10:39-10:41 | arxiv.org/abs (sleep 3) | 2306.08586, 2507.07024, 2603.21276 (version histories); 2306.08586v1, 2306.08586v2, 2603.21276v1 (earlier titles and authors); arxiv.org/pdf/2603.21276v1 |
| 10:42:46 | arxiv.org/abs (sleep 3) | 2506.00965v1, 2512.23070v1 (earlier titles) |
| 10:44:11 | Bash `date` | writing notes |

No HTTP 429 or 503 responses were observed. Status codes were captured only for the PDF downloads, all 200. Semantic Scholar and OpenAlex were not used.

**Not covered:**

- No citation chasing on HARC, FedAlign-MoE or DDOME.
- No GitHub code search (the GitHub MCP connector failed to connect).
- No Chinese-language venues.
- Not opened: MergeME, the "mixture of domain experts" router ablation (2408.17280), PHATGOOSE-style per-expert gates, M-SMoE and other expert-merging compression papers.
- No federated-MoE knowledge-distillation paper read.
- Appendix numeric tables of Router KD not read.
- Generic MoE-mechanism papers that appeared in searches (load balancing vs specialization, router drift by depth) were left to the researcher covering MoE mechanisms.
