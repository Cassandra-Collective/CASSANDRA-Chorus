# Q2 (mechanism half): how MoE experts come to specialize, and what destroys specialization
> Correction (2026-10-11, coordinator): our experts are SwiGLU with three matrices, so expert parameters are 42.47M of 46.05M (92%), about 14.2M are active per token, and a partial-arm worker trains about 54%. Figures in this file based on two-matrix experts (about 10M active, about 28M expert parameters, about 61% or 70%) are wrong; see the report's header.

| | |
|---|---|
| Date | 2026-10-11 (work done 10:28 to about 11:00 TST) |
| Scope | Question 2 of `docs/research/2026-10-11-deep-research-prompt.md`, mechanism side only: router-expert co-adaptation, collapse, load balancing, expert or routing dropout, stochastic and restricted routing, random or hash routing, z-loss. Federated, decentralized and merged MoE papers are out of scope (another researcher). |
| Method | Every paper below was downloaded from arxiv.org (or the ACL Anthology for one paper) with `curl`, converted with `pdftotext -layout`, and read in the raw text. WebSearch was used only to discover papers. No number or quotation below comes from a search snippet or WebFetch (WebFetch was not used). |
| Task A, for comparison | 3.42M parameters, 4 layers, synthetic lookup maps, **no balance loss**, 10 rounds. Sliced experts became interchangeable (random routing kept 95% accuracy vs about 48% centralized). |
| Our setting (Task B), for comparison | 46.05M total parameters, about 10-11M active per token (our estimate), 6 layers, width 384, 8 experts (hidden 768) per layer, top-2 with softmax renormalized over the 2 chosen (the same gate form as Mixtral), character vocabulary, text8, 20,000 steps x 32 x 256 = 163.8M characters, so about 15-16 characters per active parameter. Switch balance loss 0.01. fp32. Sliced arm: 4 workers, each routes over its 4 held experts, 125 local steps per round, 40 rounds. |
| Caveat on tables | pdftotext scrambles some tables. Where I reconstructed a table, the block says so and names the cross-check used. |

Abbreviations: LBL = load-balancing loss (Switch/GShard form `N * sum_i f_i * P_i`); PPL = perplexity; bpc = bits per character.

## Papers

The papers are grouped by theme. Within each block, "Bears on" uses the brief's labels (Q1-Q6; costs: local averaging +6.1%, partial updates +1.4%, masked routing +3.2%).

### A. What trained experts specialize in

#### A1. ST-MoE: Designing Stable and Transferable Sparse Expert Models

- **Authors:** Barret Zoph, Irwan Bello, Sameer Kumar, Nan Du, Yanping Huang, Jeff Dean, Noam Shazeer, William Fedus. **Year:** 2022. **Venue:** preprint (abs page comment: "25 pages main text, 39 pages overall"; no venue stated).
- **arXiv:** 2202.08906; v1 2022-02-17, v2 2022-04-29. **Read:** v2. **Link:** https://arxiv.org/abs/2202.08906. DOI: none on abs page. **Code:** paper points to Mesh TensorFlow generally; no paper-specific repository found.
- **Read status:** sections read: 3 (stability study set-up, 3.1-3.3 including router z-loss and Table 4), 4.1 (fine-tuning, expert dropout Figure 4 caption and text), 7 (tracing tokens: 7.1-7.3, Tables 13-15), and the closing remark of 7 on learned versus random routing; the top-2 recommendation in 5 and the routing statement in 4 by grep only. Not read: the rest of 5, 6, appendices except headings.
- **Setting and scale:** encoder-decoder (T5-style) sparse models, top-2 (the paper recommends "top-2 routing with 1.25 capacity factor", §5; a token "will see at most two experts per layer", §4), 32 experts, one MoE layer every fourth FFN; stability study on models FLOP-matched to T5-XL, pre-trained 20k steps on mC4 (masked LM), bfloat16 mixed precision; specialization analysis on ST-MoE models (span-corruption objective).
- **Key findings:**
  - Router z-loss `L_z = (1/B) sum_i (log sum_j exp(x_j^(i)))^2` (Eq. 5) with coefficient 0.001 (chosen by sweep, §3.3). Table 4 (v2): baseline stable in 4/6 seeds, quality (negative log perplexity) -1.755 +/- 0.02; router z-loss stable 3/3, -1.741 +/- 0.02; update clipping stable 3/3 but -4.206 +/- 0.17. The authors call the quality change "a slight quality boost" (Table 4 caption). Its stated motivation is bfloat16 round-off in the exponential (§3.4, Figure 2).
  - Encoder experts specialize in token types: punctuation, conjunctions and articles, verbs, proper names, numbers, and at least one expert per layer in sentinel tokens (§7.1, Table 13).
  - Decoder experts show far less specialization; routing entropy of sentinel tokens is 3.4 in every decoder layer against 3.5 for uniform over 32 experts, while encoder layers are 1.2-2.2 (Table 14). The authors' hypothesis: decoder routing groups are smaller (456 vs 2048 tokens) and dominated by sentinel tokens (§7.2).
  - Multilingual model: "Experts trained on multilingual mixtures do not exhibit language specialization" (Table 15 caption). Their explanation: tokens are load-balanced within a group of 2-4 sequences, so "all experts are encouraged to handle tokens from all languages"; a global balance loss they tried gave worse balance and worse quality (§7.3).
  - The authors flag as future work "an extensive study of the scaling properties of learned versus random routing" (§7, end).
  - Expert dropout (Figure 4): an independent dropout rate on the expert hidden activation during fine-tuning gave modest gains; this is activation dropout, not dropping experts from routing.
- **REMEDY tags:**
  - [REMEDY | router z-loss, c_z = 0.001 | instability; no specialization cost targeted | T5-XL-FLOP-matched sparse, 32 experts | pretraining (20k steps) | stability 3/3 vs 4/6; quality -1.741 vs -1.755 (difference within one std of 0.02) | §3.3, Table 4, v2]
  - [REMEDY | global (rather than per-group) balance loss | lack of language specialization | multilingual ST-MoE | pretraining | "usually results in worse load-balance and worse model performance" (no numbers) | §7.3, v2]
- **Bears on:** Q2 (what experts specialize in; balance scope as a driver of uniformity), Q5 (z-loss). Masked routing +3.2% only indirectly.
- **Differs from ours:** encoder-decoder, subword tokens, 32 experts, billions of parameters, bfloat16. Our model is decoder-only, character-level, 8 experts, fp32, so the z-loss stability motivation (bfloat16 round-off) is largely absent for us (inference).
- **Question for us:** does our Task B centralized model show token-type specialization (vowels, spaces, word starts) in some layers and near-uniform routing in others, as ST-MoE's encoder vs decoder?

#### A2. OLMoE: Open Mixture-of-Experts Language Models

- **Authors:** Niklas Muennighoff, Luca Soldaini, Dirk Groeneveld, Kyle Lo, Jacob Morrison, Sewon Min, Weijia Shi, Pete Walsh, Oyvind Tafjord, Nathan Lambert, Yuling Gu, Shane Arora, and others. **Year:** 2024. **Venue:** preprint (no venue stated in v2 text or abs page).
- **arXiv:** 2409.02060; v1 2024-09-03, v2 2025-03-03. **Read:** v2. **Link:** https://arxiv.org/abs/2409.02060. **Code:** https://github.com/allenai/OLMoE (GitHub API 2026-10-11: Apache-2.0, last push 2025-09-23, not archived).
- **Read status:** sections read: 4.1.1-4.1.7 (MoE vs dense, granularity, shared experts, expert vs token choice, upcycling, load-balancing loss, router z-loss) and 5.1-5.3 (router saturation, co-activation, domain specialization); 5.4 skimmed (definition only). Figures were read only through captions and text, because plotted values are not recoverable from pdftotext.
- **Setting and scale:** decoder-only; final model 6.9B total / 1.3B active, 64 experts, 8 active, 5T tokens. Ablations (§4) use smaller OLMoE-family configurations that vary per experiment (for example Figure 7 and Figure 10 use 8-expert MoEs); the paper warns models are not comparable across experiments.
- **Key findings:**
  - Shared expert (1 shared + 3 of 31 routed vs 4 of 32 routed, same compute): "sharing an expert performs slightly worse" (§4.1.3, Figure 6). The authors attribute this to fewer expert combinations.
  - Load-balancing loss (weight 0.01): better training and validation loss than no LBL "even after only a few billion tokens"; without it, the first MoE layer sends initially all tokens to one expert and most experts stay "dead weights" (§4.1.6, Figures 9-10). The authors add that the LBL "could prevent the experts from specializing in certain data domains" (§4.1.6), stated as a hypothesis.
  - Router z-loss (weight 0.001): improves stability and quality across training loss, validation loss and downstream metrics, at 2% throughput cost (§4.1.7, Figure 11; values only in the figure).
  - Router saturation (§5.1, Figure 20): after 1% of pretraining (5,000 steps, 20B tokens) up to 60% of top-8 routing already matches the final checkpoint; up to 80% at 40%. Later layers saturate earlier; layer 0 saturates "significantly more slowly". Random routing would give 12.5% for top-8.
  - Co-activation is low within a layer, which the authors read as little redundancy (§5.2, Figure 21).
  - Domain specialization (§5.3, Figure 22): OLMoE experts deviate strongly from uniform for specific domains (arXiv nearly 100% to one layer-0 expert), but are balanced on generic web text (C4). Mixtral-8x7B routing is close to uniform for all domains and layers; the authors hypothesize this is because Mixtral was upcycled from a dense model, so experts "start from the same local optimum".
- **REMEDY tags:**
  - [REMEDY | shared expert | expert redundancy | OLMoE ablation (1B-active family) | pretraining | slightly worse than all-routed at equal compute | §4.1.3, Figure 6, v2]
  - [REMEDY | router z-loss 0.001 | instability, quality | OLMoE ablation | pretraining | better stability and loss (figure only) | §4.1.7, Figure 11, v2]
  - [REMEDY | Switch LBL 0.01 vs none | routing collapse | 8-expert OLMoE ablation | pretraining | LBL better on all losses; no LBL collapses layer 0 onto one or two experts | §4.1.6, Figures 9-10, v2]
- **Bears on:** Q2 (specialization exists at scale; early router saturation; LBL vs specialization tension; layer 0 is special), masked routing +3.2% (inference: a router that keeps seeing new expert subsets cannot saturate).
- **Differs from ours:** 1B-active scale, subword tokens, 64 experts, top-8, trained for trillions of tokens.
- **Question for us:** what is router saturation (same metric) between consecutive rounds in our centralized vs sliced arms, and is our layer 0 also the slowest to settle? (Our sliced seed-11 run starved a layer-0 expert to 0.011 of tokens.)

#### A3. Mixtral of Experts

- **Authors:** Albert Q. Jiang, Alexandre Sablayrolles, Antoine Roux, Arthur Mensch, Blanche Savary, and others (Mistral AI). **Year:** 2024. **Venue:** preprint.
- **arXiv:** 2401.04088; v1 2024-01-08 only. **Read:** v1. **Link:** https://arxiv.org/abs/2401.04088. **Code:** https://github.com/mistralai/mistral-src cited for inference code; licence not checked.
- **Read status:** sections read: 2.1 (gate definition, by grep) and 5 (routing analysis) including Table 5 and Figure 7 caption.
- **Setting and scale:** Mixtral 8x7B, 8 experts, top-2 with softmax over the two chosen logits, `G(x) := Softmax(TopK(x · W_g))` (§2.1), the same gate form as ours; 32 layers. Training data and whether it was upcycled are not stated in what I read.
- **Key findings:**
  - No obvious topic specialization on The Pile validation subsets at layers 0, 15, 31; only DM Mathematics differs slightly (§5, Figure 7).
  - Syntactic regularities: for example the token "self" in Python and indentation tokens are routed consistently (§5, Figure 8).
  - Temporal locality: the same first-choice expert for consecutive tokens occurs about 14% of the time at layer 0 (random 12.5%) but 24.6% to 28.4% at layer 15 across Pile domains (Table 5; pdftotext scrambled one row, Wikipedia, so I cite the range from the other seven rows).
- **Bears on:** Q2 (what experts learn). Caution: OLMoE (A2) and Lo et al. (A6) both suggest Mixtral's experts are unusually similar, possibly from upcycling, so Mixtral is weak evidence about experts trained from scratch.
- **Differs from ours:** 47B total, subword, unknown initialization.
- **Question for us:** do our centralized Task B experts show more consecutive-character repetition in higher layers than in layer 0?

#### A4. DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models

- **Authors:** Damai Dai, Chengqi Deng, Chenggang Zhao, R. X. Xu, Huazuo Gao, Deli Chen, Jiashi Li, Wangding Zeng, Xingkai Yu, Y. Wu, Zhenda Xie, Y. K. Li, and others. **Year:** 2024. **Venue:** preprint per the arXiv record; another paper in this set cites it as ACL 2024 (62nd Annual Meeting), not confirmed at source.
- **arXiv:** 2401.06066; v1 2024-01-11 only. **Read:** v1. **Link:** https://arxiv.org/abs/2401.06066. **Code:** https://github.com/deepseek-ai/DeepSeek-MoE (GitHub API: MIT, last push 2024-01-16, not archived).
- **Read status:** sections read: 1 (motivation: knowledge hybridity and redundancy), 3.2 (shared expert isolation), 3.3 balance losses (definition and factor 0.01), 4.4 ablations (shared experts, granularity, shared/routed ratio), 4.5 (analysis on expert specialization).
- **Setting and scale:** DeepSeekMoE 2B (2.0B total; 1 shared + 7 of 63 routed active), 100B tokens, 8K BPE vocabulary, expert-level balance factor 0.01; compared with GShard x1.5 (same Pile loss).
- **Key findings:**
  - Redundancy test: for each token, mask a ratio of its top-routed experts and route to the next best. DeepSeekMoE's Pile loss rises faster than GShard's, which the authors read as lower redundancy, "each routed expert is more irreplaceable" (§4.5, Figure 4; values only in the figure).
  - Disabling the shared expert and activating one more routed expert raises Pile loss from 1.808 to 2.414 (§4.5).
  - 1, 2 or 4 shared experts out of 64 give Pile loss 1.808, 1.806, 1.811 (§4.4).
  - Isolating one shared expert in GShard improves most benchmarks (Figure 3, normalized plot only).
  - The first layer's load balance "converges especially slower", so DeepSeekMoE 16B uses a dense FFN there (§5, line read in passing).
- **REMEDY tags:**
  - [REMEDY | shared expert isolation | expert redundancy | 2B total, 100B tokens | pretraining | improves most benchmarks vs GShard (normalized figure); removing it at inference: Pile loss 1.808 to 2.414 | §4.4 Figure 3, §4.5, v1]
- **Bears on:** Q2 (redundancy as a measurable property; the "disable top experts" probe is the published analogue of our expert-removal probe), Q5 (shared experts).
- **Differs from ours:** fine-grained experts (64 per layer), subword, 2B.
- **Question for us:** if we run DeepSeekMoE's "disable the top-1 routed expert per token" probe on Task B, is the sliced model's loss curve flatter than centralized, as GShard's is flatter than DeepSeekMoE's?

#### A5. Towards an Empirical Understanding of MoE Design Choices (Fan, Messmer, Jaggi)

- **Authors:** Dongyang Fan, Bettina Messmer, Martin Jaggi (EPFL). **Year:** 2024. **Venue:** preprint per arXiv and PDF; a search result pointed to an ICLR 2024 virtual page (probably a workshop), not opened, so unverified.
- **arXiv:** 2402.13089; v1 2024-02-20 only. **Read:** v1. **Link:** https://arxiv.org/abs/2402.13089. **Code:** built on nanoGPT and a LoRA fork (named in the paper); no own repository given.
- **Read status:** full text (4 pages plus appendix).
- **Setting and scale:** GPT-2 small (124M) with an MoE in every FFN, 4 experts, top-1 or top-2, token- or sequence-level routing; about 6B tokens (6K iterations of about 1M tokens); multilingual Wikipedia (17B-token corpus) and OpenWebText; GPT-2 tokenizer; optional LBL 0.01; results averaged over the last 100 iterations, single runs (no seeds).
- **Key findings:**
  - **Frozen vs learned vs re-randomized router (Table 3, my reconstruction).** pdftotext scrambled Table 3; I mapped values to rows by cross-checking the learned-router values against Table 1 (token top-2 layer-wise 9.907 and 22.632; sequence top-2 layer-wise 10.667 and 24.980). Validation perplexity, layer-wise top-2:
    - Multilingual Wikipedia, token-level: frozen 9.810, learned 9.907, re-randomized every iteration 11.752.
    - Multilingual Wikipedia, sequence-level: frozen 10.601, learned 10.666, re-randomized 11.685.
    - OpenWebText, token-level: frozen 22.687, learned 22.632, re-randomized 26.879.
    - OpenWebText, sequence-level: frozen 24.590, learned 24.980, re-randomized 26.429.
    - Dense baselines (Table 1): 124M (same active as top-1) 11.815 / 26.195; 182M (same active as top-2) 10.831 / 24.387.
    - So a router frozen at its random initialization matches a learned one, while re-drawing the random routing every iteration loses most of the MoE gain. The authors explain that specialization can still be learned by "letting embedding layers adapt to a frozen router head" (§3.2.1).
    - Small inconsistency: learned sequence-level is 10.667 in Table 1 and 10.666 in Table 3.
  - Collapse without the LBL does not hurt: sequence-level top-2 without LBL 10.674, with LBL 0.01 10.667 (Figure 1 caption); experts can "recover from collapsing", and early and late layers collapse more (Appendix A.4).
  - Token-level routing gave no topic specialization; sequence-level gave weak topic specialization; routing patterns were language-independent (§3.2.2, Appendix A.3).
- **Bears on:** Q2 (d) directly: a consistent but non-learned mapping is enough at this scale; a mapping that changes every step is not. Masked routing +3.2% (inference below).
- **Differs from ours:** subword tokens, 124M base, 4 experts, single seeds, about 6B tokens (far more tokens per parameter than us).
- **Question for us:** our Task A random-routing probe randomizes at inference only. What happens to Task B if training itself uses a frozen random router (consistent mapping) versus per-step random routing? That separates "routing must be learned" from "routing must be consistent".

#### A6. A Closer Look into Mixture-of-Experts in Large Language Models

- **Authors:** Ka Man Lo, Zeyu Huang, Zihan Qiu, Zili Wang, Jie Fu. **Year:** 2024-2025. **Venue:** NAACL 2025 Findings (arXiv comment).
- **arXiv:** 2406.18219; v1 2024-06-26, v2 2024-10-20, v3 2025-06-21. **Read:** v3. **Link:** https://arxiv.org/abs/2406.18219. **Code:** https://github.com/kamanphoebe/Look-into-MoEs (GitHub API: MIT, last push 2025-02-07, not archived).
- **Read status:** sections read: abstract, 1 (list of observations), 3 overview, 4.1 opening (matrix-level similarity) and the start of 4.1.2. Behavioural sections (5) not read.
- **Setting and scale:** static and dynamic analysis of trained Mixtral 8x7B, Mixtral 8x22B, DeepSeekMoE 16B, Grok-1.
- **Key findings:** cosine similarity between expert weight matrices is near zero for DeepSeekMoE routed experts and Grok, but clearly non-zero for Mixtral; the authors infer Mixtral was trained with "special schemes" and that "training MoE from scratch promotes greater expert diversity than specific initialization schemes" (§1 list, §4.1). Expert diversity increases with depth, the last layer being an outlier (abstract). Neuron-order permutation makes weight similarity a lower bound (§4.1.2).
- **Bears on:** Q2 (b): shared initialization as a driver of expert similarity.
- **Differs from ours:** inference-time analysis of very large models.
- **Question for us:** our experts all start each round from the same merged weights; is the cosine similarity between our sliced experts after the merge higher than between centralized experts?

### B. Collapse and routing fluctuation

#### B1. On the Representation Collapse of Sparse Mixture of Experts (X-MoE)

- **Authors:** Zewen Chi, Li Dong, Shaohan Huang, Damai Dai, Shuming Ma, Barun Patra, Saksham Singhal, Payal Bajaj, Xia Song, Xian-Ling Mao, Heyan Huang, Furu Wei. **Year:** 2022. **Venue:** NeurIPS 2022 (PDF footer and arXiv comment).
- **arXiv:** 2204.09179; v1 2022-04-20, v2 2022-05-20, v3 2022-10-12. **Read:** v3. **Link:** https://arxiv.org/abs/2204.09179. **Code:** the paper gives https://aka.ms/msragi (not resolved).
- **Read status:** sections read: abstract, 1, 2.2 (collapse derivation), 3.3 (frozen routing in fine-tuning), 4 (set-up, results, ablations, analysis).
- **Setting and scale:** multilingual masked LM; 12-layer encoder, hidden 768, one 32-expert sparse layer after layer 6, top-1 (top-2 also tested), 125K steps at batch 2,048, 94 languages.
- **Key findings:**
  - Mechanism (§2.2, Eq. 4-6): the gradient through the gate score pushes a token's hidden state toward a linear combination of the expert (router) embeddings, so tokens routed to the same expert are pulled together and representations tend to collapse into an N-dimensional subspace. The derivation is stated for top-1 and top-K softmax gating.
  - Remedy: route on a low-dimensional hypersphere (project to dimension 16, L2-normalize tokens and expert embeddings, learnable temperature).
  - Upstream MLM perplexity (Table 2, my mapping checked against the text's statement that sigmoid X-MoE is worse than softmax SMoE): dense 23.51; softmax SMoE 19.02, softmax X-MoE 18.72; sigmoid SMoE 19.59, sigmoid X-MoE 19.12.
  - Collapse metric RC = Tr(W B^+) (within-class over between-class covariance) declines during SMoE pretraining but rises for X-MoE (Figure 2c). Routing-fluctuation ratio is lower for X-MoE after 15K steps (Figure 3a). Fine-tuning runs with different seeds converge to different routings for SMoE but nearly the same for X-MoE (Figure 3b).
  - Load-balancing weight during fine-tuning (0 to 0.1) changes XNLI by at most about 0.25 points (Table 6).
- **REMEDY tags:** [REMEDY | hypersphere low-dimensional routing (router variant) | representation collapse, routing fluctuation | 12-layer encoder, 1 x 32-expert layer | pretraining + fine-tuning | MLM PPL 19.02 to 18.72 (softmax); XTREME avg 63.8 to 65.3 | Tables 1-2, v3]
- **Bears on:** Q2 (a) and (b): router and representation co-adapt; this is the mechanism by which the router's rows and the shared trunk shape each other.
- **Differs from ours:** encoder MLM, one MoE layer, 32 experts, top-1.
- **Question for us:** in the sliced arm, router row j is updated only on workers holding expert j, but the shared trunk is averaged over all workers. Do the trunk representations drift toward the held experts' rows on each worker (Eq. 5), producing four incompatible pulls that average out?

#### B2. StableMoE: Stable Routing Strategy for Mixture of Experts

- **Authors:** Damai Dai, Li Dong, Shuming Ma, Bo Zheng, Zhifang Sui, Baobao Chang, Furu Wei. **Year:** 2022. **Venue:** ACL 2022 (arXiv comment).
- **arXiv:** 2204.08396; v1 2022-04-18 only. **Read:** v1. **Link:** https://arxiv.org/abs/2204.08396. **Code:** https://github.com/Hunter-DDM/stablemoe (GitHub API: MIT, last push 2022-07-17, not archived).
- **Read status:** sections read: abstract, 1, 3 (method, two stages), 4.1-4.4 (set-up, results, analysis including Tables 2-6 and Figure 7).
- **Setting and scale:** decoder LM on RoBERTa corpora plus CC100-en (about 100B tokens), GPT-2 BPE; base: 124M shared + 454M expert parameters, one MoE layer (3 stacked sublayers) in the middle, 60K steps; large: 355M shared + 3.22B expert. Also multilingual MT (WMT, 480M).
- **Key findings:**
  - Routing fluctuation (BASE Layer baseline): 40.9% of validation tokens still change their target expert after 20% of training, 29.1% after 50%, 15.4% after 80% (Figure 2). Stated harm: "the same input updates different experts but only one is finally used" (abstract).
  - Two stages: learn routing with a balance loss and distil it into a lightweight word-embedding router (first 10% of steps), then freeze that router (§3).
  - Base LM validation PPL (Table 2): Switch 19.79, BASE 20.04, Hash 19.63, StableMoE 19.28; dense 124M 23.02. Large: Switch 16.62, BASE 16.36, Hash 16.37, StableMoE 16.22.
  - Freezing a distilled router after 6K of 60K steps lowers BASE Layer's PPL by 0.63 (20.04 to 19.41); removing stage 2 from StableMoE raises PPL by 0.20 (Table 5). Longer stage 1 (15K, 30K steps) is slightly worse: 19.34, 19.41 vs 19.28 (Table 6).
- **REMEDY tags:** [REMEDY | freeze a distilled router after a short learned-routing phase | routing fluctuation | 124M shared + 454M expert LM | pretraining | -0.63 PPL for BASE Layer; -0.20 for StableMoE | Tables 5-6, v1]
- **Bears on:** masked routing +3.2% (inference: masking is routing fluctuation by construction), Q5 (a fixed router after a central warm-up is one of the brief's untested remedies).
- **Differs from ours:** top-1, single MoE layer, subword tokens with a word-embedding router; router distilled on token identity, which is far less informative for 27 characters (inference).
- **Question for us:** what fraction of characters in a fixed validation set change their top-1 expert between consecutive rounds, per arm? That is StableMoE's metric and would quantify how much more fluctuation masking causes.

#### B3. MaskMoE: Boosting Token-Level Learning via Routing Mask in Mixture-of-Experts

- **Authors:** Zhenpeng Su, Zijia Lin, Xue Bai, Xing Wu, Yizhe Xiong, Haoran Lian, Guangyuan Ma, Hui Chen, Guiguang Ding, Wei Zhou, Songlin Hu. **Year:** 2024. **Venue:** preprint ("Work in progress").
- **arXiv:** 2407.09816; v1 2024-07-13, v2 2024-07-28, v3 2024-08-19, v4 2024-08-29. **Read:** v4. **Link:** https://arxiv.org/abs/2407.09816. **Code:** none found in the text.
- **Read status:** sections read: abstract, 1, 3.3-3.4 (routing mask, balance loss), 4 (set-up, Tables 1-2), 5.1-5.4 (shared experts, mask hyperparameters, expert count, top-2).
- **Setting and scale:** LLaMA-style 24 layers, hidden 1024, 468M active; single MoE layer (1.3B total) or 12 MoE layers (10B total); 64 experts top-1 (or 128 half-size with a shared expert); Pile, 100B tokens, 32K vocabulary.
- **Key findings:**
  - Method: before training, each vocabulary item gets a fixed random mask of visible experts: infrequent tokens (outside the top 40% of token mass) see 1 expert, frequent tokens see 8 (§3.3, §4.3). So the restriction is per token type and fixed for all of training.
  - Main PPL (Table 1, my mapping checked against the text's stated differences): single-layer: SMoE 6.62, Hash 6.56, Share-MoE 6.72, MaskMoE 6.48; 12-layer: SMoE 6.18, Hash 6.16, Share-MoE 6.15, MaskMoE 6.11; dense 6.95.
  - Visible-expert ablation without shared expert (Table 5): all tokens see all 64 (= SMoE) 6.618; all see 8 random experts 6.566; all see 4: 6.551; all see 1 (= hash) 6.558; frequent 8 / infrequent 1: 6.506.
  - Motivation: dynamic routing "disperses" a token's occurrences across experts (routing fluctuation), so each expert sees too few occurrences of infrequent tokens (§1). With 128 experts, SMoE and Share-MoE get worse than with 64, while Hash and MaskMoE keep improving (§5.3, Figure 2).
  - Shared expert: 6.51 without vs 6.48 with (Table 3).
- **REMEDY tags:** [REMEDY | fixed per-token restriction of visible experts | routing fluctuation, under-training of rare tokens | 468M active, 1.3B-10B total | pretraining | Pile PPL 6.618 (all 64 visible) to 6.551 (4 visible) and 6.506 (8/1 by frequency) | Table 5, v4]
- **Bears on:** Q2 (c) by contrast: a *restricted* router helped here because the restriction is consistent per token type. Ours is consistent per worker, so the same character meets different subsets on different workers in the same round (inference).
- **Differs from ours:** subword vocabulary with a long tail; our 27-symbol vocabulary has no rare-token problem.
- **Question for us:** would masking by character identity (consistent) instead of by worker (inconsistent) remove the masked-routing cost? The harness's assignment policies may make a "same subset for all workers" control possible.

### C. Load balancing as a driver of uniformity

#### C1. Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts

- **Authors:** Lean Wang, Huazuo Gao, Chenggang Zhao, Xu Sun, Damai Dai (DeepSeek-AI, Peking University). **Year:** 2024. **Venue:** preprint.
- **arXiv:** 2408.15664; v1 2024-08-28 only. **Read:** v1. **Link:** https://arxiv.org/abs/2408.15664. **Code:** none found.
- **Read status:** sections read: abstract, 1, 2.2 (dilemma), 3 (method, Algorithm 1), 4.1-4.2 (set-up, Table 2), 4.3 bias-update ablations (Tables 3-4), Appendix C (softmax gate, Table 6).
- **Setting and scale:** DeepSeekMoE architecture with sigmoid gate; 1B total on 100B tokens and 3B total on 200B tokens; 32K BPE.
- **Key findings:**
  - "Dilemma" (§2.2, Figure 2): sweeping the auxiliary coefficient over 1e-2, 1e-3, 1e-4, 0, small values cause routing collapse while large values "notably degrade" perplexity (values only in the figure). The baseline uses 1e-3.
  - Method: an expert-wise bias added to routing scores only for top-K selection, updated by `b_i += u * sign(mean_load - load_i)` with u = 0.001; no gradient interference (§3).
  - Table 2 (mapping by row order): 1B: loss-controlled PPL 9.56, MaxVio 0.72; loss-free 9.50, 0.04. 3B: 7.97, 0.52 vs 7.92, 0.04.
  - Softmax gate (Appendix C): softmax is "more sensitive to load imbalance" than sigmoid (Figure 7); best softmax aux coefficient 0.0003; loss-free 9.599 vs 9.604 (Table 6).
  - The paper does **not** measure specialization; the "better specialization" claim often attributed to aux-loss-free balancing comes from elsewhere (DeepSeek-V3, not read) and from Demons (C2).
- **REMEDY tags:** [REMEDY | auxiliary-loss-free bias balancing | interference gradients from LBL | 1B / 3B DeepSeekMoE | pretraining | PPL 9.56 to 9.50 (1B), 7.97 to 7.92 (3B); softmax gate 9.604 to 9.599 | Table 2, Table 6, v1]
- **Bears on:** Q2 (b), Q5 (balance-loss variants). Note our coefficient 0.01 is the largest in their sweep, and they found 0.0003 best for a softmax gate (inference: our balance loss may be stronger than optimal, though at 8 experts and a different scale).
- **Differs from ours:** fine-grained experts with shared experts, sigmoid gate, 1-3B.
- **Question for us:** does lowering our balance coefficient (0.01 to 0.001) change the centralized-vs-sliced gap? Without any balance loss our routing collapsed onto 3-5 experts, so there is a usable range to test.

#### C2. Demons in the Detail: On Implementing Load Balancing Loss for Training Specialized Mixture-of-Expert Models

- **Authors:** Zihan Qiu, Zeyu Huang, Bo Zheng, Kaiyue Wen, Zekun Wang, Rui Men, Ivan Titov, Dayiheng Liu, Jingren Zhou, Junyang Lin (Qwen team and others). **Year:** 2025. **Venue:** preprint.
- **arXiv:** 2501.11873; v1 2025-01-21, v2 2025-02-04. **Read:** v2. **Link:** https://arxiv.org/abs/2501.11873. **Code:** none found.
- **Read status:** sections read: abstract, 1, 2, 4.1-4.2 (set-up, Table 1, Figure 2), 5 (token-number vs distribution ablation Table 2, switching Table 3, LBL weight Table 4).
- **Setting and scale:** fine-grained MoEs with 4 shared experts: 3.4B total / 0.6B active (64 experts, top-4), 15B / 2.54B and 43B / 6.6B (160 experts, top-4); 120B or 400B tokens, sequence 4,096; softmax gating, z-loss, dropless. "Balance BSZ" = number of sequences over which expert frequency f_i is computed.
- **Key findings:**
  - Computing f_i per micro-batch makes the LBL "almost at the sequence level", so "even tokens from a domain-specific sequence (e.g., code) are uniformly routed to all experts" (abstract).
  - 3.4B, 120B tokens (Table 1): Balance BSZ 4: PPL 8.167; 32: 8.062; 512: 8.038. Aux-free at BSZ 4: 8.521; at 512: 8.080.
  - 3.4B, 400B tokens (Figure 2, Table 3): BSZ 2: 7.383; 512: 7.198. Going from top-4 to top-6 experts (50% more expert FLOPs) gains less than going from BSZ 2 to 8.
  - Not just more tokens: a shuffled micro-batch with the same size but global token distribution performs like global balance (8.041 vs 8.038; 7.214 vs 7.198; Table 2).
  - Switching from micro to global balance at 10K, 30K, 50K of 100K steps: 7.283, 7.297, 7.322, all worse than global from scratch (7.199); switching global to micro at 50K: 7.373 (Table 3). The authors connect this to router choices becoming "fixed early in training".
  - Domain specialization: with micro-batch balance, no expert exceeds 0.15 selection frequency on code or math; with global balance many math experts exceed 0.2 (§4.2, Figure 1b).
  - LBL weight at micro-batch balance (Table 4): 0.008: 8.167; 0.004: 8.154; 0.001: 8.159; global balance at 0.008: 8.038.
- **REMEDY tags:**
  - [REMEDY | compute LBL frequencies over the global batch (or a buffer) | over-uniform routing within sequences | 3.4B-43B | pretraining | PPL 8.167 to 8.038 (3.4B, 120B tok); 7.383 to 7.198 (3.4B, 400B tok); 5.778 to 5.603 (15B) | Tables 1, 3, v2]
  - [REMEDY | lower LBL weight (0.008 to 0.004) | over-uniform routing | 3.4B | pretraining | 8.167 to 8.154 | Table 4, v2]
- **Bears on:** Q2 (b) centrally: the scope of the balance constraint, not just its weight, controls specialization. Masked routing +3.2% (inference: in our sliced arm each worker computes the LBL over its own batch and its own 4 experts, which is both a narrow scope and a different target).
- **Differs from ours:** 0.6B active and up, subword, multi-domain corpus. text8 is a single-domain corpus (Wikipedia), so domain specialization has little room (inference).
- **Question for us:** in the sliced arm, the balance loss pushes each held expert toward 1/4 of a worker's routed slots, versus 1/8 centrally. Is the masked-routing cost smaller if the sliced workers' balance loss is dropped or weakened?

#### C3. Advancing Expert Specialization for Better MoE

- **Authors:** Hongcan Guo, Haolang Lu, Guoshun Nan, Bolun Chu, Jialin Zhuang, Yuan Yang, Wenhao Che, Xinye Cao, Sicong Leng, Qimei Cui, Xudong Jiang. **Year:** 2025. **Venue:** NeurIPS 2025 (oral, per arXiv comment and PDF footer).
- **arXiv:** 2505.22323; v1 2025-05-28, v2 2025-09-24, v3 2025-11-03, v4 2025-12-26, v5 2026-01-25. **Read:** v5. **Link:** https://arxiv.org/abs/2505.22323. **Code:** "this link" in the abstract; URL not recoverable from text; not verified.
- **Read status:** sections read: abstract, 1, 2.2 (observations I-III with gradient argument), 4.1-4.5 (set-up, results, load balance, behaviours, ablation). Method details in 3.1-3.2 skimmed.
- **Setting and scale:** **fine-tuning only**, with LoRA (rank 32) on router and experts, 6,000 examples per benchmark, 3 epochs (550 steps); models DeepSeek-MoE-16B, DeepSeek-V2-Lite, Moonlight-16B-A3B.
- **Key findings:**
  - Argument (§2.2): the auxiliary loss assigns tokens to experts with no affinity for them, sending them "unintended" gradients (Obs. I); routing scores drift toward uniform (Obs. II); similar experts give the router fewer cues, so routing gets more uniform (Obs. III, a feedback loop).
  - Adds an orthogonality loss on expert outputs and a variance loss on routing scores; reports up to 23.79% improvement over aux-loss baselines (abstract).
  - "Aux only" vs "no losses": silhouette coefficient over 0.05 higher and routing variance 0.0045 higher with the aux loss, yet the text concludes the no-loss model is *more* orthogonal (§4.4). The direction of the silhouette statement is inconsistent with its conclusion; I could not resolve this.
  - I do not cite Table 1 values: the row labels were scrambled by pdftotext and could not be mapped reliably.
- **REMEDY tags:** [REMEDY | orthogonality + routing-variance losses | expert overlap from LBL | 16B-class MoEs | fine-tuning (LoRA, 550 steps) | up to 23.79% over aux-loss baselines (abstract) | abstract, §4, v5]
- **Bears on:** Q2 (b): a stated mechanism linking LBL to expert overlap. Evidence is from short fine-tuning, so transfer to 46M pretraining is weak.
- **Differs from ours:** fine-tuning, 16B models, LoRA.
- **Question for us:** is expert-output similarity (their "expert overlap") higher in our sliced experts than centralized ones on the same inputs?

#### C4. Load Balancing Mixture of Experts with Similarity Preserving Routers (SimBal)

- **Authors:** Nabil Omi, Siddhartha Sen, Ali Farhadi. **Year:** 2025. **Venue:** preprint (PDF says "Preprint").
- **arXiv:** 2506.14038; v1 2025-06-16, v2 2025-10-11. **Read:** v2. **Link:** https://arxiv.org/abs/2506.14038. **Code:** none found.
- **Read status:** sections read: abstract, 1, set-up lines of §4 (model sizes, data). Results sections not read.
- **Setting and scale:** MoE-M (230M active / 627M total) on 19.9B tokens and MoE-L (762M / 3.14B) on 78.6B tokens, DCLM data, bfloat16.
- **Key findings (abstract and intro only):** standard balancing pushes toward a roughly uniform distribution per token, which "can result in inconsistent routing behavior" and redundant knowledge; an orthogonality-promoting router loss gives "36% faster convergence and lower redundancy" (abstract).
- **REMEDY tags:** [REMEDY | similarity-preserving (orthogonal router) balance loss | redundancy from uniform balancing | 230M-762M active | pretraining | 36% faster convergence (abstract only; not checked in results) | abstract, v2]
- **Bears on:** Q2 (b), Q5 (balance-loss variants). Weak: abstract-level claim.
- **Differs from ours:** 230M-762M active, subword, bfloat16, results not read.
- **Question for us:** do similar characters in similar contexts get routed to the same experts more consistently in our centralized arm than in the sliced arm (their "consistent expert choices for similar inputs")?

### D. Expert dropout, routing dropout, stochastic and restricted routing

#### D1. Gating Dropout: Communication-efficient Regularization for Sparsely Activated Transformers

- **Authors:** Rui Liu, Young Jin Kim, Alexandre Muzio, Hany Hassan Awadalla (Microsoft, University of Michigan). **Year:** 2022. **Venue:** ICML 2022, PMLR 162 (PDF footer).
- **arXiv:** 2205.14336; v1 2022-05-28, v2 2022-07-04. **Read:** v2. **Link:** https://arxiv.org/abs/2205.14336. **Code:** the paper says it "will be available at" https://aka.ms/gating_dropout (not resolved).
- **Read status:** full text of the main paper (sections 1-6).
- **Setting and scale:** multilingual MT with Z-code M3 MoE (DeepSpeed); WMT-10: Transformer-base 12+6 layers, 128 experts per MoE layer, about 5.6B parameters, 16 GPUs; Web-50: Transformer-big 24+12 layers, 64 experts, about 10B, 64 GPUs; top-1, capacity factor 1.0 train / 2.0 test, balance loss 0.01, input jitter in the baseline.
- **Key findings:**
  - Method: at each iteration, with probability p all machines keep their tokens on local experts (no all-to-all); otherwise normal routing (§3). Gate-Expert-Drop instead skips the local experts entirely when on.
  - Authors' reasoning: forcing tokens to local, possibly non-optimal, experts means "we encourage the experts to learn a general ability" (§1); they frame it as breaking co-training of gate and experts and as epsilon-greedy exploration (§3).
  - WMT-10 (Table 2): baseline BLEU 24.60 at convergence; Gate-Drop (p = 0.3) 25.06; Gate-Expert-Drop (p = 0.2) 25.12; a hash layer 23.06 and never reaches the baseline's BLEU.
  - Web-50 (Table 4): average BLEU 28.63 baseline, 29.22 Gate-Drop, 28.85 Gate-Expert-Drop.
  - Dose-response (Figure 6, Gate-Expert-Drop on WMT-10 after 35k steps): best at p = 0.2, decreasing beyond; at p = 0.5 BLEU is 0.23 below baseline. The authors note p = 1 is not workable because the model "will not be able to learn any gating".
- **REMEDY tags:** [REMEDY | route all tokens to machine-local experts with probability p per step | co-adaptation / overfitting (regularizer); communication | 5.6B (128 experts) and 10B (64 experts) MT MoE | pretraining (MT training) | +0.46 / +0.52 BLEU at p = 0.3 / 0.2 (WMT-10); +0.59 / +0.22 (Web-50); -0.23 at p = 0.5 | Tables 2, 4, Figure 6, v2]
- **Bears on:** Q2 (c): this is the closest published analogue to masked routing. Our sliced arm forces local-only routing on every step of a round (p = 1 within a round), and without synchronous data parallelism between rounds (inference).
- **Differs from ours:** synchronous training (every step averaged across machines), so local-only steps still update one shared model; top-1; 64-128 experts; MT.
- **Question for us:** what is the masked-routing cost as a function of the fraction of steps (or tokens) that are masked? Gating Dropout's curve suggests small fractions help and large ones hurt; we have only measured the endpoint.

#### D2. Taming Sparsely Activated Transformer with Stochastic Experts (THOR)

- **Authors:** Simiao Zuo, Xiaodong Liu, Jian Jiao, Young Jin Kim, Hany Hassan, Ruofei Zhang, Tuo Zhao, Jianfeng Gao. **Year:** 2021-2022. **Venue:** ICLR 2022 (PDF header).
- **arXiv:** 2110.04260; v1 2021-10-08, v2 2021-10-12, v3 2022-02-03. **Read:** v3. **Link:** https://arxiv.org/abs/2110.04260. **Code:** https://github.com/microsoft/Stochastic-Mixture-of-Experts (GitHub API: MIT, last push 2021-10-07, **archived**).
- **Read status:** sections read: 1-4, 5.5 (ablations), Appendix A (analysis set-up and Switch gate behaviour). Main result tables 5.2-5.4 skimmed.
- **Setting and scale:** analysis (§3): MT on IWSLT De/Vi to En, BPE, **2 experts**, comparison with a Transformer of the same size; THOR experiments: low-resource and rich-resource MT and multilingual MT up to 300M parameters; scale-up appendix: 48M Transformer vs 55M, 143M, 456M with 2, 16, 64 experts.
- **Key findings:**
  - Claim: gating-based routing does "not work better than randomly routing inputs to experts" (abstract). With 2 experts, one gate collapses to one expert after about 200 iterations; another gate's confidence converges to about 0.55-0.60, i.e. near-random, with or without the balance loss (§3, Appendix A.2).
  - Removing the trained router from a Switch Transformer at inference (random experts): BLEU 20.6 to 20.4 on Cs-En (§5.5).
  - THOR: a random pair of experts per layer per batch, with a symmetric-KL consistency regularizer between the two experts' predictions. Without the regularizer BLEU drops from 22.4 to 20.8 (Table 4).
  - The authors say the consistency loss trains experts toward "making the same predictions as much as possible" (§4): it deliberately makes experts interchangeable.
- **REMEDY tags:** [REMEDY | random expert pair per batch + consistency regularizer | parameter inefficiency of gated MoE | small MT models, 2-64 experts | training from scratch | Cs-En BLEU 22.4 with CR vs 20.8 without; ties a 5.5B Z-code MoE with 300M parameters (abstract) | Table 4, v3]
- **Bears on:** Q2 (c) and (d). THOR produces interchangeable experts on purpose; SMoE-Dropout (D3) later blames THOR's consistency regularizer for redundancy.
- **Differs from ours:** MT encoder-decoder, 2 experts in the analysis, small data.
- **Question for us:** is our sliced Task A result (random routing keeps 95% accuracy) the THOR outcome reached without a consistency loss, through the averaging step instead (inference)?

#### D3. Sparse MoE as the New Dropout: Scaling Dense and Self-Slimmable Transformers (SMoE-Dropout)

- **Authors:** Tianlong Chen, Zhenyu Zhang, Ajay Jaiswal, Shiwei Liu, Zhangyang Wang (UT Austin). **Year:** 2023. **Venue:** not stated in v1 text or abs page (see Could not verify).
- **arXiv:** 2303.01610; v1 2023-03-02 only. **Read:** v1. **Link:** https://arxiv.org/abs/2303.01610. **Code:** https://github.com/VITA-Group/Random-MoE-as-Dropout (GitHub API: Apache-2.0, last push 2023-02-28, not archived).
- **Read status:** sections read: 1, 3.1-3.2, 4.1-4.4 (set-up, Table 1, Figure 3 and 5 descriptions, ablations).
- **Setting and scale:** **character-level enwik8** with a reduced Transformer-XL (4 layers, d = 256, FFN 8,192 split into experts, 8 heads), batch 22, 400K iterations; also BERT and RoBERTa on BooksCorpus (bpc on MLM).
- **Key findings:**
  - Method: split each FFN into experts, route with a **fixed randomly initialized router**, and linearly increase k during training ("self-slimmable").
  - enwik8 test bpc (Table 1, parameter-matched): dense with dropout 1.1623; THOR 1.3110; learned SMoE 1.1896; SMoE-Dropout 1.1776 (k = N/2) and 1.1486 (k = N).
  - Width (§4.4, Figure 5b, enwik8): dense with dropout beats SMoE-based training at 8 or fewer experts; learned routing beats their random routing at 8 or fewer experts; random routing wins at 16.
  - Depth (Figure 5a): dense is best at 2 layers; SMoE-Dropout wins at 4 or more; the learned-vs-random gap grows with depth.
  - Random-policy ablation (Figure 5c): the fixed random router beats THOR-style fully random assignment and a random hash, by 2.96 to 170.11 x 10^-2 bpc across sizes.
  - Their reading of THOR's and learned SMoE's saturation as experts are added: "expert redundancy (or representation collapse)" (§4.2), stated as an implication, not measured.
- **REMEDY tags:** [REMEDY | fixed random router + growing k | representation collapse / redundancy | 4-layer Transformer-XL on enwik8 (character level) | pretraining | bpc 1.1896 (learned SMoE) to 1.1486 (k = N) | Table 1, v1]
- **Bears on:** Q2 (d) at character level and small scale: with 8 experts, learned routing still beat random routing, and dense beat both.
- **Differs from ours:** experts are slices of one FFN (smaller experts), top-k grows during training, enwik8 not text8; model about 4 layers.
- **Question for us:** at our 8 experts, is a dense model of equal active compute competitive with our centralized MoE on text8? (Also raised by G2.)

#### D4. Approximating Two-Layer Feedforward Networks for Efficient Transformers (sigma-MoE)

- **Authors:** Róbert Csordás, Kazuki Irie, Jürgen Schmidhuber. **Year:** 2023. **Venue:** Findings of EMNLP 2023 (arXiv comment).
- **arXiv:** 2310.10837; v1 2023-10-16, v2 2023-10-23, v3 2023-11-21. **Read:** v3. **Link:** https://arxiv.org/abs/2310.10837. **Code:** https://github.com/robertcsordas/moe (MIT, last push 2025-06-11) and https://github.com/robertcsordas/moe_layer (MIT, last push 2024-01-05); both not archived (GitHub API).
- **Read status:** sections read: 4 (existing MoE variants, including the softmax-top-K collapse remark), 5 (sigma-MoE: selection function, initialization, entropy regularization, expert dropout), 6.1-6.3 (Tables 1, 3, 4, 5; expert-utilization analysis), Appendix tables 8-9 (partly garbled).
- **Setting and scale:** parameter-matched Transformer-XL; **enwik8 character-level 41M** (d = 512, 12 layers, 16 experts of size 128, K = 4); WikiText-103 47M and 262M; C4 and peS2o; 100K steps; every FFN replaced by an MoE.
- **Key findings:**
  - "Expert dropout" here means dropping whole experts from selection during training (Eq. 22); removing a popular expert "forces the less popular ones to take over" (§5).
  - On enwik8 41M almost every variant gives 1.08 bpc: dense 1.08, sigma-MoE 1.08, Switch 1.08, with standard dropout instead of expert dropout 1.08, no regularization 1.08, standard init 1.08; softmax variants 1.09; S-BASE 1.17; K = 1, G = 512 1.32 (Tables 3-4).
  - On WikiText-103 47M, design choices matter more: sigma-MoE 11.59; standard dropout instead of expert dropout 12.01; softmax with renormalization 11.89; standard init 11.80; no regularization 11.83 (Table 4).
  - Collapse: "Softmax combined with top-K can also encourage expert collapsing" (§5); the softmax-with-renormalization variant and Switch "severely suffer from the expert collapse problem" at 128 experts (§6.3, Figure 3). Removing all regularization "does not entail catastrophic collapse" (§6.3).
  - The authors "do not consider uniform expert activation to be optimal" (§6.3).
  - Router (W3) initialization: rows rescaled to equal norm so only the angle to x matters initially (§5).
- **REMEDY tags:**
  - [REMEDY | expert dropout (drop whole experts from selection) | collapse, under-used experts | 47M WikiText-103 / 41M enwik8 | pretraining | WT-S 12.01 (standard dropout) to 11.59; enwik8 1.08 both | Table 4, v3]
  - [REMEDY | equal-norm router-row initialization (with dense-style expert init) | collapse / poor initial routing | same | pretraining | WT-S 11.80 (standard init) to 11.59; enwik8 1.08 both | Table 4, v3]
- **Bears on:** Q2 at our scale and token type: at 41M on characters, routing design barely moves bpc; Q6 (dense baseline equals MoE at 1.08 bpc with 25% of FLOPs).
- **Differs from ours:** many small experts (G = 128), K = 4, sigmoid gate, Transformer-XL; enwik8 vs text8. I could not reliably extract the enwik8 expert-dropout rate from the garbled Table 9.
- **Question for us:** is our top-2-of-8 softmax-renormalized gate (sigma-MoE's "softmax (renorm.)" family) part of why routing collapsed without the balance loss?

#### D5. Switch Transformers (expert dropout and initialization only)

- **Authors:** William Fedus, Barret Zoph, Noam Shazeer. **Year:** 2021-2022. **Venue:** JMLR (arXiv comment).
- **arXiv:** 2101.03961; v1 2021-01-11, v2 2022-04-30, v3 2022-06-16. **Read:** v3. **Link:** https://arxiv.org/abs/2101.03961. **Code:** Mesh TensorFlow (general).
- **Read status:** sections read: 2.2 (balance-loss coefficient), 2.4 (selective precision, initialization scale, Table 3; expert dropout, Table 4).
- **Key findings:**
  - Balance coefficient: swept 1e-1 to 1e-5; 1e-2 "balanced load quickly without interfering with training loss" (§2.2; no numbers).
  - Initialization: all weights from truncated normal with scale s = 0.1 instead of 1.0: quality -2.72 +/- 0.01 vs -3.60 +/- 0.68 (negative log perplexity, 32 experts, 3.5k steps, 3 seeds; Table 3, row values reordered by pdftotext and mapped using the text).
  - **"Expert dropout" in Switch is a higher dropout rate on the activations inside expert FFNs during fine-tuning** (0.4 inside experts, 0.1 elsewhere): GLUE 85.2 vs 84.7 (Table 4). It does not drop experts from routing.
- **REMEDY tags:**
  - [REMEDY | 0.1x weight initialization (all weights, not router-only) | instability | Switch-Base 32 experts | pretraining (3.5k steps) | -3.60 +/- 0.68 to -2.72 +/- 0.01 | Table 3, v3]
  - [REMEDY | expert (activation) dropout 0.4 | overfitting | Switch-Base, 34B-token pretrain | fine-tuning | GLUE 84.7 to 85.2 | Table 4, v3]
- **Bears on:** terminology for Q2 (b) and Q5; not evidence about routing dropout.
- **Differs from ours:** top-1, T5-style encoder-decoder, bfloat16, Mesh TensorFlow; the initialization result concerns all weights and early-training stability, not routing.
- **Question for us:** what initialization scale do our router rows use, and does a smaller router-row scale (more uniform early routing, as in Chen et al.'s exploration stage, F1) change the centralized arm's specialization?

### E. Random, hash and frozen routing

#### E1. Hash Layers For Large Sparse Models

- **Authors:** Stephen Roller, Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston. **Year:** 2021. **Venue:** v3 PDF says "Preprint. Under review."; Fan et al. (A5) cite it as NeurIPS 34 (2021), not confirmed at source.
- **arXiv:** 2106.04426; v1 2021-06-08, v2 2021-06-16, v3 2021-07-20. **Read:** v3. **Link:** https://arxiv.org/abs/2106.04426. **Code:** none found in the text.
- **Read status:** sections read: 5 (experiments: set-up, 5.3.1-5.3.4, Tables 1-6).
- **Setting and scale:** encoder-decoder (2 enc + 11 dec layers, d = 1024) on pushshift.io Reddit, 8,008-token BPE, 100K updates; one sparse layer of 16-128 experts (751M-1.28B total) or 5 x 16; BASE comparison at 4.5B on RoBERTa+CC100 (40K steps); WikiText-103 with 8K vs 267K vocabularies. Hashing is on the **current token ID**, so it is deterministic per token type.
- **Key findings:**
  - 64 experts: Switch 23.65 vs Hash 23.16 valid PPL; 128 experts: 23.52 vs 22.89 (Table 1). For 16 and 32 experts "Hash and Switch perform similarly", and the gap grows with expert count (Figure 3). The authors hypothesize "learning to route" matters more with few experts.
  - 5 x 16 experts: Switch with balance 0.1 beats Hash (23.00 vs 23.21); with 0.01 they tie (23.19) (§5.3.1). Switch varies over about 1 PPL across balance coefficients (§5.3.3).
  - Fixed random vs balanced hash: 23.22 vs 23.16; clustering-based hash is worse (23.90); hashing on position is no better than dense (25.07); oracle future-token hash gives 1.97 (Table 3).
  - WikiText-103: with the 8K vocabulary Hash slightly beats Switch (11.58 vs 11.67); with the 267K vocabulary Hash is worse (32.32 vs 31.76) (Table 4; values mapped to rows using the text, since pdftotext dropped the baseline row's numbers).
  - Hash beats BASE at 4.5B throughout training; the authors attribute BASE's late instability to shifting expert assignments (§5.3.4).
  - A deeper dense model (755M) beats both sparse models of similar size (Table 1).
- **Bears on:** Q2 (d). With 27 characters, token-ID hashing would give each of 8 experts about 3-4 characters and no context (inference), so hash results do not transfer directly to character-level routing.
- **Differs from ours:** subword, one sparse layer, top-1, dialogue data.
- **Question for us:** what does a character-hash router (fixed per character) cost on Task B relative to learned routing? It is cheap to try if the harness supports a fixed routing function.

#### E2. Unified Scaling Laws for Routed Language Models

- **Authors:** Aidan Clark, Diego de las Casas, Aurelia Guy, Arthur Mensch, Michela Paganini, Jordan Hoffmann, and others (DeepMind). **Year:** 2022. **Venue:** not stated in the PDF text I read; search results point to ICML 2022 (PMLR 162), not confirmed at source.
- **arXiv:** 2202.01169; v1 2022-02-02, v2 2022-02-09. **Read:** v2. **Link:** https://arxiv.org/abs/2202.01169. **Code:** none found.
- **Read status:** sections read: 2-3 (set-up, routing techniques), 4.2 interpretation, 4.3 opening, 5.3 (comparative analysis and recommendations), Appendix A table of model sizes, B.4 (HASH implementation), seed-variance paragraph.
- **Setting and scale:** decoder LMs, dense base sizes 15M, 25M, 55M, 130M, 370M, 870M, 1.3B; experts E from 1 to 512; K = 1; 250K steps, 130B tokens (MassiveText), 32K SentencePiece. HASH = token ID modulo E. Seed spread at 130M: at most 0.01 loss before 100K steps.
- **Key findings:**
  - "All routing techniques suffer from reducing efficacy as N increases" (§5.3); all three predict diminishing improvements from routing at larger N (§4.2).
  - S-BASE (learned, Sinkhorn-balanced) is best at all sizes and scales best (lowest c); RL-R is "very competitive at smaller N"; for small N, RL-R and S-BASE scale better with expert count than HASH; HASH has the largest initial overhead, visible at small E (§5.3).
  - Recommendation 1 reads "Use routing when training any model with N [symbol] 1.3B" (§5.3): pdftotext dropped the comparison symbol, so I do not state its direction. Results at single sizes "cannot be extrapolated" (§5.3).
- **Bears on:** Q2 (d): learned routing does beat token-hash routing across 15M-1.3B, and the routing benefit itself shrinks with model size. Our 10M-active model sits at the bottom of their range.
- **Differs from ours:** top-1, subword, 130B tokens (far more tokens per parameter than our 164M characters).
- **Question for us:** at our token budget, which is far below theirs, is any routing benefit over dense left to lose (see E6)?

#### E3. On the Benefits of Learning to Route in Mixture-of-Experts Models

- **Authors:** Nishanth Dikkala, Nikhil Ghosh, Raghu Meka, Rina Panigrahy, Nikhil Vyas, Xin Wang. **Year:** 2023. **Venue:** EMNLP 2023 (Proceedings pages 9376-9396, from the PDF footer).
- **arXiv:** none found (see Could not verify). **Read:** ACL Anthology PDF, https://aclanthology.org/2023.emnlp-main.583.pdf; DOI 10.18653/v1/2023.emnlp-main.583 (confirmed with the Crossref API on 2026-10-11: title and EMNLP 2023 proceedings match). **Code:** none found.
- **Read status:** sections read: abstract, 1 (empirical and theoretical summary), 3.7 (language modeling on mC4), Appendix C.4 paragraph on the T5 frozen-router experiment, 4.1-4.2 statements.
- **Setting and scale:** synthetic clustered data (mixtures of Gaussians, subspaces, dictionary learning, CIFAR-100 clusters) and T5 MoE pretraining on mC4 (12 layers, 3 sparse layers, top-2, 500K steps).
- **Key findings:**
  - Theory: routers can learn to ignore noise directions and to recover latent clusters (§4).
  - Dictionary-learning data (clusters combined): "a frozen router performs just as well as learnable router" (§1.1).
  - T5 Base-sized MoE: freezing the router at initialization barely changes pre-training accuracy (70.34% vs 70.27%), because earlier layers can learn to route implicitly; only after shrinking model dimension to 32 (hidden 256) does the trainable router win consistently (Appendix, §3.7, Figure 7).
- **Bears on:** Q2 (a) and (d): upstream layers adapt to a fixed router, so "learned routing" can live in the trunk rather than the router weights. In our sliced arm the trunk is averaged across all workers while each router row sees only its holders (inference).
- **Differs from ours:** T5 span corruption, subword; synthetic theory.
- **Question for us:** with a router frozen at initialization in all arms, does the sliced-vs-partial gap (+3.2%) shrink? That isolates router-row averaging from trunk effects.

#### E4. A Declarative-Procedural Perspective on Expert Routing in Bilingual Mixture-of-Experts Language Models

- **Authors:** Amrit Gopinath, Raghul, Durairaj Thenmozhi. **Year:** 2026. **Venue:** preprint.
- **arXiv:** 2608.15102; v1 2026-08-15, v2 2026-08-28. **Read:** v2. **Link:** https://arxiv.org/abs/2608.15102. **Code:** "Github link" in the abstract; URL not recoverable.
- **Read status:** sections read: abstract, 3 (framework), 4.4 (set-up), 5.1-5.2, Appendix G (routing controls, Table 9).
- **Setting and scale:** decoder-only English-German MoE, 86.4M parameters, 8 layers with MoE in layers 1, 3, 5, 7, 8 experts, top-3, LBL 0.01, mBERT tokenizer; metric: mutual information (MI) between routing and linguistic category of probe tokens. Single main run per condition plus one replication seed.
- **Key findings (MI at layer 5, Table 9 and §5.2):** learned routing 0.1148; frozen (untrained) router 0.0274; random routing 0.0018; LBL coefficient 0.005 instead of 0.01: 0.1482; top-2: 0.1100; top-4: 0.2382.
- **Bears on:** Q2 (b) (weaker balance, more specialization at 86M) and (d) (random routing removes specialization; a frozen router keeps about a quarter of it).
- **Differs from ours:** subword, probe-category MI rather than loss; very few seeds.
- **Question for us:** a routing-category MI (characters grouped as vowels, consonants, space) would be a cheap specialization metric for our three arms.

#### E5. UniPool: Learning Expert-to-Layer Ownership from Brief Global Access

- **Authors:** Minbin Huang, Han Shi, Chuanyang Zheng, Yimeng Wu, Guoxuan Chen, Xingtong Yu, Yichun Yin, Hong Cheng. **Year:** 2026. **Venue:** preprint. Note: v1 had a different title ("UniPool: A Globally Shared Expert Pool for Mixture-of-Experts", per a search result); I read only v2.
- **arXiv:** 2605.06665; v1 2026-05-07, v2 2026-09-27. **Read:** v2. **Link:** https://arxiv.org/abs/2605.06665. **Code:** https://github.com/Centaurus-Alpha/UniPool (GitHub API: licence NOASSERTION, last push 2026-09-27, not archived).
- **Read status:** sections read: abstract, 1, 3 (routing-randomization probe, Table 1), 5.4 paragraph and Table 7.
- **Setting and scale:** probe on production MoEs (Qwen1.5-MoE, DeepSeek-V2-Lite, Qwen3-30B-A3B) and on their own 182M-1.5B dense-equivalent models.
- **Key findings:**
  - Replacing the learned top-k router of one deep-half layer with uniform random assignment, averaged over deep-half layers, costs 1.6, 1.2 and 1.0 downstream accuracy points on the three production models (Table 1; values mapped by matching the reported differences). The authors: the learned choice "adds little over a random one" (§3).
  - On their 469M models the same probe costs 1.3 points for vanilla MoE, 3.3 and 4.1 for their variants with learned layer ownership (Table 7), which they read as stronger specialization.
- **Bears on:** Q2 (d): even large production MoEs show substantial within-layer substitutability, measured with the same kind of inference-time random-routing probe as our Task A probe.
- **Differs from ours:** one layer randomized at a time; downstream accuracy, not loss.
- **Question for us:** in Task B, what does randomizing one layer at a time cost in each arm (bpc), so our numbers are comparable to this probe?

#### E6. Slicing and Dicing: Configuring Optimal Mixtures of Experts

- **Authors:** Margaret Li, Sneha Kudugunta, Danielle Rothermel, Luke Zettlemoyer. **Year:** 2026. **Venue:** preprint (PDF says "Preprint").
- **arXiv:** 2605.11689; v1 2026-05-12 only. **Read:** v1. **Link:** https://arxiv.org/abs/2605.11689. **Code:** https://github.com/hadasah/slicing_and_dicing (GitHub API: no licence field, last push 2026-05-12, not archived).
- **Read status:** sections read: abstract, 1, 3.1 paragraph "MoEs outperform dense models (above some compute minimum)", 3.2 generalists paragraph, 3.3 ablations (dropless, load balancing), Appendix A hyperparameter table, Appendix C.3 (10M and 20M results).
- **Setting and scale:** over 2,000 pretraining runs, active sizes 10M, 20M, 50M, 80M, 110M, 200M, 300M, up to 6.6B total; token choice; z-loss 1e-3; LBL weight 1e-2 or 1e-4; loss-free bias 0 or 1e-3; dropless or default routing.
- **Key findings:**
  - "At 10M and 20M scales, MoEs consistently fail to outperform dense baselines" (§3.1), across all expert counts, granularities, generalists and balance settings (Appendix C.3). With more data, so that tokens are roughly 100x and 400x the active parameter count, MoEs outperform dense again (Appendix C.3). The main text and appendix state the 5x / 20x data multipliers in opposite order for the 10M and 20M models.
  - A shared "generalist" expert "consistently results in performance that is comparable to or slightly degraded" relative to none (§3.2, Figure 5).
  - Balance: the worst setting at every scale is the weak LBL (1e-4) with no loss-free bias; otherwise no setting dominates at 128 or fewer experts (§3.3).
- **REMEDY tags:** [REMEDY | shared generalist expert | redundancy | 10M-300M active, up to 6.6B total | pretraining | comparable or slightly worse | §3.2, Figure 5, v1]
- **Bears on:** Q2 (d) and Q6: at our active size and our data budget (about 15-16 characters per active parameter), this study finds MoE gives no gain over dense, so expert specialization may have little room to pay off. Characters carry less information per token than subwords, which makes our effective budget smaller still (inference).
- **Differs from ours:** subword tokens; the paper uses a fixed recipe per scale; our model has 8 coarse experts.
- **Question for us:** what does a dense model with our active parameter count reach on text8 at 20,000 steps? If it matches the centralized MoE, the masked-routing cost is a loss of a gain that is small to begin with.

### F. Theory and router-expert coupling

#### F1. Towards Understanding Mixture of Experts in Deep Learning

- **Authors:** Zixiang Chen, Yihe Deng, Yue Wu, Quanquan Gu, Yuanzhi Li. **Year:** 2022. **Venue:** not stated in v1 (see Could not verify).
- **arXiv:** 2208.02813; v1 2022-08-04 only. **Read:** v1. **Link:** https://arxiv.org/abs/2208.02813. **Code:** none found.
- **Read status:** sections read: abstract, 1 (contributions), 5 (proof sketch: Key Techniques 1-2, Main Difficulties 2-3). Theorems and proofs not read.
- **Setting:** theory: mixture-of-classification data with cluster structure; MoE of two-layer CNN experts (cubic activation), top-1 router with noise, zero-initialized gate, normalized gradients; plus synthetic and small real experiments.
- **Key findings:** a single expert cannot exceed 87.5% test accuracy on their distribution; the MoE reaches nearly 100%. Training has an exploration stage during which the router routes almost uniformly and each expert becomes specialized to a cluster "determined by the initialization"; the router then learns cluster-centre features. If the router errs early, "the experts may amplify the mistake". Linear experts fail to diversify (§1, §5).
- **Bears on:** Q2 (a): the canonical account of co-adaptation (uniform exploration, initialization breaks symmetry, router follows experts).
- **Differs from ours:** idealized data, top-1, theory.
- **Question for us:** each round, our sliced workers restart from the same merged weights with a fresh optimizer; does that repeatedly reset the symmetry-breaking that Chen et al. say drives specialization (inference)?

#### F2. Coupling Experts and Routers in Mixture-of-Experts via an Auxiliary Loss (ERC loss)

- **Authors:** Ang Lv, Jin Ma, Yiyuan Ma, Siyuan Qiao (ByteDance Seed, Renmin University). **Year:** 2025-2026. **Venue:** ICLR 2026 (oral, per arXiv comment).
- **arXiv:** 2512.23447; v1 2025-12-29, v2 2026-02-24. **Read:** v2. **Link:** https://arxiv.org/abs/2512.23447. **Code:** none found in text.
- **Read status:** sections read: abstract and 1 only.
- **Setting and scale:** MoE LLMs 3B to 15B, pretraining on trillions of tokens (abstract).
- **Key findings (abstract and intro):** without explicit constraints, routers learn by "trial-and-error" and misrouted tokens' gradients "interfere with expert specialization" (§1). The ERC loss treats each router row as a cluster centre, feeds perturbed rows through all experts, and requires each expert to respond most to its own row and each row to elicit most from its own expert.
- **Bears on:** Q2 (a): router rows as cluster centres for their experts. In our holder-only router averaging, row j is averaged with expert j, which keeps that pairing (inference).
- **Differs from ours:** 3B-15B, trillions of tokens; results not read.
- **Question for us:** after a sliced merge, does each router row still select the inputs on which its own expert has the largest activation norm (ERC's coupling test), compared with the centralized model?

#### F3. Grouter: Decoupling Routing from Representation for Accelerated MoE Training

- **Authors:** Yuqi Xu, Rizhen Hu, Zihan Liu, Mou Sun, Kun Yuan. **Year:** 2026. **Venue:** ICML 2026, PMLR 306 (v2 PDF footer).
- **arXiv:** 2603.06626; v1 2026-02-22, v2 2026-05-24. **Read:** v2. **Link:** https://arxiv.org/abs/2603.06626. **Code:** https://github.com/JimmyAwoe/Grouter (GitHub API: Apache-2.0, last push 2026-05-04, not archived).
- **Read status:** sections read: abstract, 1, 2.2 (routing-perturbation study, Figure 1 caption).
- **Key findings:** joint router-expert training forces experts to "chase a 'moving target'" (§1). Randomizing the router's outputs early in training (around 1K steps) causes no collapse, while later perturbations cause loss and gradient-norm spikes; the authors read this as specialization deepening as the router stabilizes (§2.2, Figure 1b; qualitative, figure only).
- **Bears on:** Q2 (a): specialization grows after routing stabilizes. Masked routing prevents stabilization (inference).
- **Differs from ours:** the perturbation study's model size is not stated in the sections I read; Grouter itself distils a router from a trained Qwen3-30B-A3B, which has no analogue in our setting.
- **Question for us:** if we randomize routing for a few steps at different points of centralized Task B training, does sensitivity rise over training as Grouter reports, and when?

## Synthesis for question 2 (mechanisms)

Scale reminder: almost every finding below comes from models of 124M parameters or more on subword tokens. The only character-level evidence is sigma-MoE at 41M on enwik8 (D4) and SMoE-Dropout's small Transformer-XL on enwik8 (D3). The only evidence at our active size (10-20M) is Slicing and Dicing (E6), on subword tokens.

### (a) How specialization arises: router-expert co-adaptation

What the papers show:

- **Symmetry is broken by initialization, then reinforced.** In Chen et al.'s theory, the router starts near-uniform (zero-initialized gate plus noise), each expert drifts toward the cluster its random initialization favours, and the router then learns the cluster centres; early router mistakes are amplified by the experts (F1, §5). X-MoE gives the matching gradient argument for real models: the gate-score gradient pulls each token's representation toward the router row (expert embedding) it was sent to (B1, Eq. 5). So router rows and trunk representations co-adapt.
- **Routing settles early, then specialization deepens.** OLMoE: up to 60% of top-8 routing is already final after 1% of training and up to 80% after 40%; layer 0 is slowest (A2, §5.1). Demons: router choices "fixed early", so changing the balance scope late recovers only part of the gain (C2, Table 3). Grouter: random routing perturbations are harmless around 1K steps but cause spikes later (F3, qualitative). StableMoE: even so, a learned-routing baseline (BASE) still changed the expert of 15.4% of tokens after 80% of training (B2, Figure 2), and freezing the router after 10% of training improved PPL by 0.63 (B2, Table 5).
- **What experts specialize in.** Token types and syntax rather than topics: punctuation, verbs, names and numbers in ST-MoE's encoder, with near-uniform decoder routing (A1, Tables 13-14); syntax and strong temporal locality but no topic structure in Mixtral (A3); syntax with token-level routing and weak topics only with sequence-level routing (A5). Domain specialization appears in OLMoE (64 experts, trained from scratch) and in Demons only when the balance loss is computed over a large, diverse batch (A2 §5.3; C2 §4.2).
- **Routing knowledge can live in the trunk.** A router frozen at random initialization matches a learned router at GPT-2-small scale (A5: 9.810 vs 9.907 and 22.687 vs 22.632 PPL) and at T5-Base scale (E3: 70.34% vs 70.27% accuracy), because upstream layers learn to route implicitly; the learned router wins only when the trunk is crippled (d = 32, E3).

Inference for our case (not shown by any paper): in the sliced arm, router row j learns only on workers holding expert j, but the trunk is averaged over all workers, and each worker's trunk is pulled toward the rows of its own four experts (X-MoE mechanism). Each round restarts from merged weights with a fresh optimizer. The consistent token-to-expert mapping that A5 and E3 say is needed has little opportunity to form.

### (b) What drives experts toward uniformity or redundancy

What the papers show, roughly in order of strength of evidence:

1. **Inconsistent routing (fluctuation) disperses a token's training signal across experts.** StableMoE (B2) and MaskMoE (B3) both argue this and both gain by making routing consistent (frozen distilled router; fixed per-token visible subsets). Fan et al. give the cleanest contrast: a fixed random mapping keeps the MoE gain, a mapping redrawn every iteration loses most of it (A5: 11.752 vs 9.810 PPL, close to the 124M dense baseline's 11.815).
2. **Balance loss over a narrow scope.** Per-micro-batch balance makes routing nearly uniform within each sequence and suppresses domain specialization; widening the scope helps at 3.4B-43B (C2). ST-MoE gives the same explanation for the lack of language specialization (A1, §7.3). A weaker balance coefficient raised routing-category mutual information at 86M (E4: 0.1482 at 0.005 vs 0.1148 at 0.01). Advancing Expert Specialization argues the balance loss sends tokens to mismatched experts and creates a feedback loop toward uniformity, but its evidence is from short LoRA fine-tuning (C3).
3. **Shared initialization.** Mixtral's experts are similar and its routing near-uniform by domain; two independent papers attribute this to probable upcycling from a dense model (A2 §5.3; A6 §4.1).
4. **Deliberately stochastic or forced routing.** Gating Dropout's authors intend forced local routing to give experts "a general ability" (D1, §1); THOR's consistency loss makes experts agree on purpose (D2); SMoE-Dropout attributes THOR's saturation to that redundancy (D3, §4.2, an implication, not a measurement).
5. **Representation collapse** toward the span of the router rows (B1), measured as a falling within/between-class variance ratio during SMoE pretraining (B1, Figure 2c).

Collapse in the other direction (all tokens to few experts) is the classic failure that the balance loss prevents: it happened in OLMoE without the LBL (A2, Figure 10), in Fan et al. (A5, Figure 1), in THOR's 2-expert analysis (D2, §3), and in our own Task B without the balance loss (3-5 of 8 experts used). Softmax followed by top-K is said to encourage it (D4, §5), and softmax gates are "more sensitive to load imbalance" than sigmoid gates (C1, Appendix C).

### (c) Is there direct evidence that training under a restricted or masked router produces generalist or redundant experts?

**Not found in this search.** No paper I opened trains a learned router that, for many consecutive steps, can see only a worker-specific subset of experts and is then merged with routers that saw other subsets, and then measures expert specialization or redundancy. The search covered: the 13 WebSearch queries in the query log (expert specialization, expert redundancy, routing collapse, random routing, expert dropout, gating dropout, restricted or masked routing, router initialization, training dynamics, 2024-2026), the papers named in the brief, and the related-work sections of the papers read. Federated, decentralized and merged MoE papers were excluded by scope and may contain such evidence (see the other researcher's notes).

The closest analogues, ordered from nearest to farthest:

1. **Gating Dropout (D1):** tokens forced to machine-local experts for whole steps, with probability p. p = 0.2-0.3 improved BLEU by about 0.5 at 5.6B and 10B; p = 0.5 fell 0.23 below the baseline; the authors say p = 1 cannot learn any gating. They predict, but do not measure, more general experts. Our sliced arm is local-only for all 125 steps of a round, without per-step synchronization (inference: it sits beyond the end of their dose-response curve).
2. **THOR (D2) and SMoE-Dropout (D3):** random expert subsets per batch. With THOR's consistency loss the experts are made to agree; SMoE-Dropout's authors attribute the resulting saturation to redundancy (implication only).
3. **MaskMoE (B3):** the opposite result. A *fixed* per-token restriction (each token type sees the same 4 or 8 of 64 experts for all of training) improved PPL over full routing (6.551 and 6.566 vs 6.618). The difference from ours is consistency: their restriction depends on the token, ours on the worker (inference).
4. **sigma-MoE expert dropout (D4):** whole experts dropped from selection at random; it helped on WikiText-103 47M (11.59 vs 12.01 with standard dropout) and made no difference on enwik8 41M (1.08 both). No specialization was measured.

(Inference) A concrete mechanism consistent with these papers, in two parts:

- **Routing share, present in both tasks.** On a sliced worker, top-2 routing over 4 held experts sends each held expert on average half of the tokens (a quarter of the routed slots); centrally, top-2 over 8 gives each expert about a quarter of the tokens (an eighth of the slots). Each held expert therefore trains on twice the share of every input type, alongside a different set of competitors each round, and the four holders' versions are then averaged. This needs no balance loss. Task A had **no balance loss** and its sliced experts still became interchangeable, so on Task A this part alone (masking plus averaging) must carry the explanation. It also fits the comparison arms: the partial-update arm, which routes over all 8 experts, kept most of the specialization.
- **Balance scope, present only in Task B.** With the Switch balance loss computed per worker over its 4 held experts, the loss actively pushes the 4 held experts toward equal shares within each local batch. This is an additional uniformity pressure, matching Demons' finding that a narrow balance scope forces near-uniform use (C2). It may add to the Task B masked-routing cost but cannot be the whole story, given Task A.

### (d) Does random or hash routing work nearly as well as learned routing, and does that depend on scale?

The literature uses three different notions of "random routing", and they behave differently:

| Notion | Examples | Result |
|---|---|---|
| (i) Hash of the token ID (fixed, token-consistent, no context) | Hash Layers (E1); Clark HASH (E2); MaskMoE V = 1 (B3); Gating Dropout's hash baseline (D1) | Ties or beats Switch with 16-128 experts on an 8K vocabulary (E1); worse than Switch with a 267K vocabulary (E1); worst of three routers across 15M-1.3B, largest overhead at small expert counts (E2); far worse in MT at 128 experts (D1: 23.06 vs 24.60 BLEU) |
| (ii) Router frozen at random initialization (embedding-dependent; the trunk can adapt to it) | Fan et al. (A5); Dikkala et al. (E3); SMoE-Dropout (D3); bilingual MI (E4) | Matches learned routing at 124M-295M and T5-Base (A5, E3); loses to learned routing only with a crippled trunk (E3) or with 8 or fewer experts on enwik8 (D3); keeps about a quarter of the learned specialization signal at 86M (E4) |
| (iii) Re-drawn random assignment per step or per token | THOR (D2); Fan et al. "Random" (A5); inference-time probes in UniPool (E5) and THOR's router removal (D2) | Training with it loses most of the MoE gain (A5); THOR recovers only by adding a consistency loss; at inference, randomizing one deep layer of production MoEs costs 1.0-1.6 accuracy points (E5); removing a Switch router costs 0.2 BLEU in small MT (D2) |

Our Task A probe is notion (iii) applied at inference to models trained with learned routing. The published inference-time probes (E5, D2) show modest drops even in large learned-routing models, so some substitutability is normal; our centralized Task A model losing about half its accuracy shows our centralized experts were far more specialized than that, and the sliced experts far less.

Scale dependence, as reported:

- The benefit of any routing shrinks as the dense base grows from 15M to 1.3B (E2), but learned S-BASE keeps the lowest scaling penalty, so learned routing stays ahead of hash at every size they test (E2).
- In Hash Layers the hash advantage over Switch *grows* with expert count (E1, Figure 3); in SMoE-Dropout the fixed random router overtakes learned routing at 16 experts and with depth (D3). So with many experts, consistency matters more than learning; with few experts (our 8), learned routing has its best case (E1 hypothesis, D3 Figure 5b).
- At 10-20M active parameters and about 20 tokens per active parameter, MoEs do not beat dense models at all (E6). Our budget is about 15-16 characters per active parameter.

(Inference) At our scale, with 8 experts on characters, the literature predicts that learned routing matters somewhat (few experts) but that the total MoE gain over dense is small (E6, D3, D4). Both predictions are testable with our harness.

### z-loss as a remedy candidate

- Measured effects are on **stability** at large scale in bfloat16: ST-MoE stable in 3/3 seeds vs 4/6, with quality -1.741 vs -1.755 (within one standard deviation; A1 Table 4); OLMoE reports better stability and loss (figure only; A2 §4.1.7). Slicing and Dicing used 1e-3 throughout (E6, Appendix A) and Demons used it by default (C2).
- **Silent:** no paper I read measures z-loss's effect on expert specialization, on redundancy, or under restricted routing. Its stated mechanism (bfloat16 round-off in large logits) does not apply to our fp32 runs (inference). Mechanically it keeps router logits small, i.e. softer routing probabilities (inference); whether that helps or hurts specialization is unmeasured.

### Where the papers disagree

- **Shared experts:** help (DeepSeekMoE 2B, A4; MaskMoE 6.51 to 6.48, B3) vs slightly hurt (OLMoE, A2) vs "comparable to or slightly degraded" across over 2,000 runs (E6).
- **Does collapse without a balance loss hurt?** Not at 124M-295M with 4 experts and sequence-level routing (A5: 10.674 vs 10.667); yes at 1B+ (A2 Figure 9; C1 Figure 2); "does not entail catastrophic collapse" at 47M with sigmoid routing (D4).
- **Global vs local balance scope:** global helped at 3.4B-43B (C2); ST-MoE found global balance gave "worse load-balance and worse model performance" (A1 §7.3, no numbers).
- **Hash vs learned:** hash ahead in Hash Layers and StableMoE's base setting (E1; B2: 19.63 vs 19.79), behind in Clark et al., in Gating Dropout's MT and in large-vocabulary WikiText-103 (E2, D1, E1).
- **Balance coefficient:** 0.01 is the Switch/OLMoE default (D5, A2) but the largest value in the aux-loss-free sweep, where 1e-3 (sigmoid) or 3e-4 (softmax) was best (C1); weak balance (1e-4) was the worst setting in E6.

### What is unknown or silent

- No measurement of expert specialization or redundancy after training under a worker-specific restricted router (section (c)).
- No study of router saturation or fluctuation under periodic averaging.
- No measurement of z-loss on specialization.
- No character-level study of what experts specialize in.
- No controlled comparison of learned vs frozen vs hash routing at 10-50M on characters with 8 experts.
- How large the MoE gain over dense is at our exact budget (E6 suggests near zero, but on subwords).

## Candidates for the joint reading list

1. **Liu et al., Gating Dropout (ICML 2022, arXiv 2205.14336).** The closest published analogue to masked routing, with a dose-response (p) and a stated "general ability" hypothesis. Specific (read after the basics).
2. **Dai et al., StableMoE (ACL 2022, arXiv 2204.08396).** Defines and measures routing fluctuation and shows a frozen-router remedy; the mechanism vocabulary for (a) and (b). Foundational (read early).
3. **Qiu et al., Demons in the Detail (preprint 2025, arXiv 2501.11873).** Shows the scope of the balance loss controls specialization and quality, with clean ablations. Foundational (read early).
4. **Fan, Messmer, Jaggi, Towards an Empirical Understanding of MoE Design Choices (preprint 2024, arXiv 2402.13089).** Four pages; frozen vs learned vs re-randomized routers at GPT-2-small scale, the clearest evidence that consistency, not learning, is what matters there. Specific.
5. **Li et al., Slicing and Dicing (preprint 2026, arXiv 2605.11689).** At 10-20M active, MoE does not beat dense; bears on whether specialization can matter at our scale and on Q6. Specific.

Alternates if the list has room: ST-MoE (foundational for z-loss and token-type specialization), SMoE-Dropout (character-level, small scale), Clark et al. (scale dependence of routing).

## Gaps

Questions no paper answers that the existing harness could answer (it supports other H, Nesterov outer momentum, slice sizes, worker counts, assignment policies, partial/full/sliced modes, skewed data, worker dropout, random-routing and expert-removal probes):

1. **Masked-routing cost vs slice size.** Sliced runs with 4, 5, 6 and 7 of 8 experts per worker (8 of 8 is the full-model averaging arm) would give a dose-response analogous to Gating Dropout's p, which no paper has for periodic averaging. Comparing each with a partial-update run of the same slice size isolates the masking share at each size.
2. **Masked-routing cost vs H.** Shorter rounds mean more frequent re-synchronization of router rows; does the +3.2% shrink with H, as routing fluctuation papers would predict (inference)?
3. **Task B random-routing and expert-removal probes in all four arms**, including one-layer-at-a-time randomization (comparable to UniPool, E5) and DeepSeekMoE's "disable top-k routed experts" curve (A4).
4. **Router saturation and fluctuation per round** (OLMoE's and StableMoE's metrics) in each arm, to test whether masking prevents the early routing commitment that A2 and C2 describe.
5. **Assignment policy as consistency.** A policy that gives every worker the same experts for a round, versus the coverage policy, separates "restricted" from "inconsistent across workers" (the MaskMoE contrast).
6. **Skewed data.** With worker-specific data, does sliced training become more or less specialized than centralized? No paper covers restricted routing with skewed shards in the mechanism literature.
7. Items that need small code changes rather than existing options (stated so they are not mistaken for supported features): balance-loss coefficient or scope per arm (0.01 vs 0.001; local vs global frequencies), a frozen-at-initialization router in all arms (A5, E3), a character-hash router (E1), z-loss, and a dense baseline at equal active parameters (E6).

## Could not verify

- **Dikkala et al. arXiv ID:** none found by one WebSearch; read from the ACL Anthology PDF instead (DOI confirmed via Crossref).
- **Venues not stated at source:** Hash Layers (PDF v3 says "Preprint. Under review"; Fan et al. cite NeurIPS 34); Clark et al. (ICML 2022 per search results only); DeepSeekMoE (ACL 2024 per another paper's references only); SMoE-Dropout and Chen et al. (no venue in v1); Fan et al. (an ICLR 2024 virtual page appeared in search results, not opened).
- **Code links not resolved:** Gating Dropout (https://aka.ms/gating_dropout), X-MoE (https://aka.ms/msragi), Advancing Expert Specialization ("this link"), bilingual MoE paper ("Github link"); Hash Layers, aux-loss-free, Demons, Clark, ERC and SimBal give no code link in the text I read.
- **Garbled tables:** sigma-MoE Table 9 (enwik8 expert-dropout rate and balance weight); Advancing Expert Specialization Table 1 (row labels); Mixtral Table 5 Wikipedia row. Values from these were not used.
- **Internal inconsistencies noted, not resolved:** Fan et al. learned sequence-level PPL 10.667 (Table 1) vs 10.666 (Table 3); Slicing and Dicing's 5x/20x data multipliers given in opposite order in §3.1 and Appendix C.3; Advancing Expert Specialization's silhouette statement in §4.4 contradicts its own conclusion.
- **UniPool v1** had a different title per a search result; only v2 was read, and v1 content may differ.
- **Leads seen in search results but not opened (no claims made from them):** DeepSeek-V3 technical report (claimed aux-loss-free specialization), "Finding Fantastic Experts in MoEs" (2504.05586), "Brain-Like Processing Pathways Form in Models With Heterogeneous Experts" (2506.02813, expert dropout at small scale), "Exploiting Mixture-of-Experts Redundancy Unlocks Multimodal Generative Abilities" (2503.22517), "From Observation to Intervention: A Causal Audit of Expert Importance" (2606.10703), "Depth-Aware Sensitivity Analysis of MoE" (2608.13565), Motif 3 technical report (2608.09119, decaying router noise), LibMoE (2411.00918, router initialization), Cluster-aware upcycling (CVPR 2026, router init from centroids), HyperRouter (EMNLP 2023), V-MoE random-router swap (2106.05974), STAR (2606.08814), ProbMoE (2606.01509), Mixture-of-Clustered-Experts (2509.10513), Robustness of MoE to Feature Noise (2601.14792).

## Query log

All times TST (UTC+3), 2026-10-11. `date` was run at 10:28:49, 10:45:09 and 10:48:21; download times come from the fetch script's own timestamps. WebSearch calls are bracketed by these times rather than individually timed.

WebSearch (discovery only; no results used as evidence):

- Between 10:28:49 and 10:31:08 (before the first download):
  1. `expert specialization mixture of experts load balancing loss harms specialization 2025 arXiv`
  2. `random routing mixture of experts nearly as good as learned routing`
  3. `gating dropout sparsely activated transformers route tokens to local experts`
  4. `expert redundancy similarity homogeneity mixture of experts analysis 2025 2026 arXiv`
  5. `training MoE with subset of experts per step stochastic expert dropout generalist experts specialization`
  6. `Csordás approximating two-layer feedforward networks efficient transformers sigma-MoE expert dropout enwik8`
  7. `router initialization mixture of experts effect on specialization ablation`
  8. `Unified Scaling Laws for Routed Language Models hash routing RL routing S-BASE Clark`
  9. `expert dropout mixture of experts robustness missing experts pretraining 2025`
  10. `MoE training dynamics when does expert specialization emerge routing stabilizes early in training`
  11. `router trained on subset of experts masked gating expert subsets specialization lost generalist experts`
- Between 10:35 and 10:43:41:
  12. `Dikkala "On the Benefits of Learning to Route in Mixture-of-Experts Models" arXiv`
  13. `mixture of experts pretraining randomly drop experts from router during training redundancy generalist experts 2025 2026 arXiv`

Downloads (arxiv.org abs page then PDF, `sleep 3` between requests, all HTTP 200, no 429s):

- 10:31:17-10:32:58: 2202.08906, 2409.02060, 2401.06066, 2204.09179, 2204.08396, 2408.15664, 2501.11873, 2110.04260, 2407.09816, 2303.01610, 2106.04426, 2202.01169.
- 10:33:11-10:34:55: 2402.13089, 2205.14336, 2310.10837, 2505.22323, 2401.04088, 2101.03961, 2608.15102, 2603.06626, 2512.23447, 2208.02813, 2406.18219, 2506.14038.
- 10:43:50-10:44: 2605.11689, 2605.06665; ACL Anthology PDF 2023.emnlp-main.583.

Other APIs: GitHub REST `repos/{owner}/{repo}` for 11 repositories (finished 10:48:21); Crossref `works/10.18653/v1/2023.emnlp-main.583` (between 10:48:21 and 10:56:27).

Not covered:

- DeepSeek-V3 report and its aux-loss-free specialization claim; GShard; Shazeer et al. 2017; BASE layers; expert-choice routing (Zhou et al.); dense-gradient router methods; V-MoE and other vision MoE routing studies.
- Citation chasing (Semantic Scholar, OpenAlex, Google Scholar) on Gating Dropout, StableMoE, THOR or MaskMoE; a forward-citation search on Gating Dropout is the most likely place to find a closer analogue to masked routing.
- OpenReview, NeurIPS 2025/2026 and ICLR 2026 proceedings scans, workshops, Chinese-language venues.
- GitHub code search (the GitHub MCP connector failed to connect in this session).
- Full results sections of SimBal, ERC loss and Grouter; DeepSeekMoE 16B and 145B sections; OLMoE vocabulary specialization (§5.4) and appendix analyses.
