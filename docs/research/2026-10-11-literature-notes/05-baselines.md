# Question 6: is our centralized text8 baseline, and the 5% criterion, sensible?
> Correction (2026-10-11, coordinator): our experts are SwiGLU with three matrices, so expert parameters are 42.47M of 46.05M (92%), about 14.2M are active per token, and a partial-arm worker trains about 54%. Figures in this file based on two-matrix experts (about 10M active, about 28M expert parameters, about 61% or 70%) are wrong; see the report's header.

Research notes for question 6 of `docs/research/2026-10-11-deep-research-prompt.md`. Written 2026-10-11 by a research agent. Every number below comes from raw paper text that I read myself: arXiv PDFs converted with `pdftotext`, plus the arXiv abs pages for version histories. Nothing comes from a search snippet or a leaderboard. Anything I computed myself is marked **(inference)**, with the arithmetic shown.

**Our setup, for reference** (from `docs/stage0-report.md` §2 and §3.3, and the brief):

- Model: top-2 of 8 experts, 6 layers, width 384, expert hidden size 768, context 256, 27-symbol vocabulary. 46.05M parameters in total, about 10-11M active per token (the project's own estimate).
- Training: 20,000 AdamW steps at 32 × 256 = 163.84M characters. Over the 90M-character training split that is **1.82 passes** (inference: 163.84M / 90M).
- Optimizer and schedule: 100 warm-up steps, constant 1e-3, then linear decay to 1e-4 over the last 4,000 steps; β = (0.9, 0.95); no weight decay; gradient clipping 1.0; fp32. Switch balance loss 0.01.
- Test bits per character: 1.4388, 1.4386 and 1.4353 (mean **1.4376**). Scored over the whole 5M-character test split in non-overlapping 256-character windows.
- What 5% means here: 5% of 1.4376 is **0.072 bits per character** (inference). The full-averaging gap of +6.1% is about 0.088 bits per character, and the sliced gap of +10.8% is about 0.155.

---

## Papers

### P1. Character-Level Language Modeling with Deeper Self-Attention

- **Authors:** Rami Al-Rfou, Dokook Choe, Noah Constant, Mandy Guo, Llion Jones (Google AI Language).
- **Year and venue:** 2018. The PDF carries an AAAI 2019 copyright line.
- **arXiv:** 1808.04444. v1 9 Aug 2018; v2 10 Dec 2018. **Read v2.**
- **Link:** https://arxiv.org/abs/1808.04444. DOI 10.48550/arXiv.1808.04444 (arXiv-issued).
- **Read status:** full text.
- **Setting and scale:**
  - Model: a non-recurrent causal transformer on text8 (90M/5M/5M split) and enwik8.
  - T64: 64 layers, width 512, filter size 2048, 2 heads, context 512, 235M training / 219M inference parameters, dropout 0.55.
  - T12: 12 layers, 44M training / 41M inference parameters, dropout 0.2.
  - Output is a 256-way byte softmax, even on text8.
  - Auxiliary losses: every sequence position, intermediate layers, and a second target character.
  - Optimizer: momentum 0.99, fixed learning rate 0.003, batch 16 × 512.
  - Training length: T64 for 4M steps, with the best checkpoint at about 2.5M steps; T12 for 8M steps ("Training", "Results").
- **Evaluation protocol:** each character is predicted from a fresh forward pass over the preceding 512 characters, so this is a sliding window with stride 1 ("Evaluation" section).
- **Key findings:**
  - text8 test bits per character (Table 1): **T12 (41M inference) 1.18**; **T64 1.13**.
    - The table also cites earlier work: LSTM 1.43; BN-LSTM 1.36; HM-LSTM (35M) 1.29; RHN (45M) 1.27; mLSTM (45M) 1.27; mLSTM with dynamic evaluation (45M) 1.19.
  - enwik8 test (Table 3): T12 1.11; T64 1.06. The paper notes that these are really bits per byte.
  - **Context-length ablation of T64 (Table 2)**, text8 dev / test bits per character:

    | Evaluation context (characters) | Dev | Test |
    |---|---|---|
    | 32 | 1.25 | 1.34 |
    | 64 | 1.17 | 1.26 |
    | 128 | 1.12 | 1.20 |
    | 256 | 1.09 | 1.16 |
    | 512 | 1.06 | 1.13 |

    The text says the trend "levels off after 512 characters"; 1024 gave no gain.
  - Ablation (Table 4, text8 dev): removing the loss at every position raises dev bits per character from 1.062 to 2.482.
- **Bears on:** the comparison table; how model size relates to bits per character; the context and evaluation-protocol effect (the only text8 table of bits per character against evaluation context that I found).
- **How it differs from ours:**
  - dense, not a mixture of experts;
  - 125 to 400 times more training characters (inference: T64 2.5M × 16 × 512 = 20.5B; T12 8M × 16 × 512 = 65.5B, against our 0.164B);
  - stride-1 evaluation with 512 characters of context;
  - heavy dropout.
- **Question for us:** how much of the 0.26 bits per character between our 1.44 and T12's 1.18 is evaluation protocol, and how much is training budget?

### P2. Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context

- **Authors:** Zihang Dai, Zhilin Yang, Yiming Yang, Jaime Carbonell, Quoc V. Le, Ruslan Salakhutdinov.
- **Year and venue:** 2019. The abs page says "ACL 2019 long paper".
- **arXiv:** 1901.02860. v1 9 Jan 2019; v2 18 Jan 2019; v3 2 Jun 2019. **Read v3.**
- **Link:** https://arxiv.org/abs/1901.02860. DOI 10.48550/arXiv.1901.02860 (arXiv-issued).
- **Read status:** sections read: §3.1 (vanilla model and its evaluation), §4.1 (main results, Tables 1-3), §4.2 (ablation, Table 6), §4.3 (Table 8), §4.5 (evaluation speed, Table 9).
- **Setting and scale:** a transformer with segment-level recurrence (a cached memory of earlier segments) and relative position encodings.
- **Key findings:**
  - enwik8 test (Table 2): 12-layer Transformer-XL **41M 1.06**; 18 layers, 88M, 1.03; 24 layers, 277M, 0.99.
  - text8 test (Table 3): 24 layers, **277M, 1.08**.
  - The 18- and 24-layer models used "attention length 784 during training and 3,800 during evaluation" (§4.1). The 12-layer model's evaluation length is not stated in the sections I read.
  - The 12-layer Transformer-XL beats Al-Rfou's 12-layer model by 0.05 on enwik8 (§4.1).
  - text8 reused the enwik8 hyperparameters without further tuning (§4.1).
  - The vanilla model's evaluation shifts the segment one position at a time; the paper calls it "extremely expensive" (§3.1). Al-Rfou-style evaluation is up to 1,874 times slower (Table 9).
- **Training length:** not stated in the text I read (the paper points to released code, which I did not read).
- **Bears on:** the size calibration (41M versus 277M) and long-context evaluation.
- **How it differs from ours:** dense; a recurrent memory with evaluation contexts of thousands of characters; unknown budget.
- **Question for us:** none beyond P1. It shows how much of the published gap long-context evaluation buys.

### P3. Adaptive Attention Span in Transformers

- **Authors:** Sainbayar Sukhbaatar, Edouard Grave, Piotr Bojanowski, Armand Joulin (Facebook AI Research).
- **Year and venue:** 2019. The abs page says "Accepted to ACL 2019".
- **arXiv:** 1905.07799. v1 19 May 2019; v2 8 Aug 2019. **Read v2.**
- **Link:** https://arxiv.org/abs/1905.07799. DOI 10.48550/arXiv.1905.07799 (arXiv-issued).
- **Read status:** sections read: abstract, §1, §2.1, §3 (all, with Tables 1-3 and the figure captions), §4. §2.2-2.3 (the span mechanism) not read.
- **Setting and scale:**
  - Small model: 12 layers, width 512, ReLU layer 2048, 8 heads.
  - Large model: 24 layers, width 768, ReLU layer 4096.
  - Uses Transformer-XL-style caching in training and test (§2.1).
  - Adagrad, batch 64, learning rate 0.07, 32k warm-up steps, 512-character training blocks.
  - Small models: dropout 0.3, 600K steps (900K when the span limit S = 8192).
  - Large models: dropout 0.4, trained until validation stopped improving (250K steps on text8), then 20K more steps at the learning rate divided by 10 (§3).
- **Key findings:**
  - text8 (Table 1): small adaptive span (S = 8192, average span 314), **38M, dev 1.05, test 1.11**. Large, 209M, test 1.07.
  - enwik8 (Table 2): small 39M, 1.02; large 209M, 0.98.
  - The text says small models beat other transformers by "0.07 bcp" [sic].
  - Figure 3: dev bits per character improve as the span limit rises from 256 to 4096. The values are in the plot only, so I did not record them.
- **Training characters (inference):** small, S = 8192: 900K × 64 × 512 = 29.5B (328 passes). Large: 270K × 64 × 512 = 8.8B (98 passes).
- **Bears on:** the size calibration at 38M versus 209M; the value of context.
- **How it differs from ours:** dense; spans of up to 8,192 characters through caching; 180 times our characters.
- **Question for us:** at our budget, does context beyond 256 even matter? (Its Figure 3 measures this only at convergence.)

### P4. Longformer: The Long-Document Transformer

- **Authors:** Iz Beltagy, Matthew E. Peters, Arman Cohan.
- **Year and venue:** 2020. Preprint; no venue is stated in the version I read.
- **arXiv:** 2004.05150. v1 10 Apr 2020; v2 2 Dec 2020. **Read v2.**
- **Link:** https://arxiv.org/abs/2004.05150. DOI 10.48550/arXiv.2004.05150 (arXiv-issued).
- **Read status:** sections read: §4.2 (character-level setup: training, evaluation, Tables 2-3) and part of Appendix B (Table 12, compute).
- **Setting and scale:**
  - Small model: 41M parameters, sliding-window attention, dropout 0.2.
  - Staged training in 5 phases: sequence length from 2,048 to 23,040; batch sizes 32, 32, 16, 16, 16; steps per phase 430K, 50K, 50K, 35K, 5K (Table 12).
  - Compute: 4 RTX8000 GPUs for 16 days (App. B).
- **Evaluation protocol:** overlapping windows of 32,256 characters, advanced by 512; only the last 512 are scored (§4.2).
- **Key findings (Table 2):** small model, **41M, text8 dev 1.04, test 1.10**; enwik8 dev 1.02, test 1.00.
- **Training characters (inference):** about 52.3B summed over the phases (581 passes). Caveat: Table 12 prints only the phase 1 (2,048) and phase 5 (23,040) sequence lengths. I took phases 2-4 as 4,096, 8,192 and 16,384 from the text's rule of doubling the sequence length each phase.
- **Bears on:** the comparison table at about our total size.
- **How it differs from ours:** dense; evaluation with 32k characters of context; 319 times our characters.
- **Question for us:** none specific.

### P5. Multiplicative LSTM for sequence modelling

- **Authors:** Ben Krause, Liang Lu, Iain Murray, Steve Renals.
- **Year and venue:** 2016-2017. The v3 PDF says "Previous version appeared in workshop track - ICLR 2017"; v3 itself states no venue.
- **arXiv:** 1609.07959. v1 26 Sep 2016; v2 25 Oct 2016; v3 12 Oct 2017. **Read v3.**
- **Link:** https://arxiv.org/abs/1609.07959. DOI 10.48550/arXiv.1609.07959 (arXiv-issued).
- **Read status:** sections read: abstract, §4.1 (methodology), §4.2 (Hutter Prize, Table 1), §4.3 (text8, Table 2).
- **Setting and scale:**
  - Recurrent models trained with truncated backpropagation through time (200-250 steps).
  - Follow-up experiments: Adam starting at 0.001, decayed linearly to 5e-5 to 1e-4 (§4.1).
  - Initial experiments: RMSprop.
- **Key findings (text8 test, Table 2):**
  - small LSTM (RMSprop, hidden 512): 1.64;
  - small mLSTM (RMSprop, hidden 450): 1.59;
  - unregularised mLSTM (RMSprop; hidden 1900 per §4.3): **1.40**;
  - large mLSTM with embedding, weight normalisation and variational dropout (about 45M per §4.3): **1.27**;
  - also cited: LSTM (Cooijmans) 1.43; MI-LSTM 1.44; mRNN 1.54.
- **Training length:** not stated for the text8 runs in the sections I read. (The "4 epochs" in §4.2 refers to Hutter Prize experiments and does not transfer.)
- **Bears on:** recurrent baselines at 10-45M; the size of the regularisation gain (unregularised 1.40 against regularised 1.27).
- **How it differs from ours:** recurrent, with state carried across the test sequence (not stated explicitly in the sections I read, which is standard for these models); much longer training with early stopping.
- **Question for us:** our model has no dropout. Would regularisation matter at 1.8 passes? (Inference: probably little; see the synthesis.)

### P6. Recurrent Batch Normalization

- **Authors:** Tim Cooijmans, Nicolas Ballas, César Laurent, Çağlar Gülçehre, Aaron Courville.
- **Year and venue:** 2016-2017. The PDF says "Published as a conference paper at ICLR 2017".
- **arXiv:** 1603.09025. v1 30 Mar 2016; v2 31 Mar 2016; v3 4 Apr 2016; v4 12 Apr 2016; v5 28 Feb 2017. **Read v5.**
- **Link:** https://arxiv.org/abs/1603.09025. DOI 10.48550/arXiv.1603.09025 (arXiv-issued).
- **Read status:** sections read: §5.3 (text8, Table 3) and the Penn Treebank setup paragraph.
- **Setting and scale:**
  - Both models are LSTMs with 2000 units.
  - Adam, learning rate 1e-3, batch 128, gradient clipping 1.0.
  - Trained on non-overlapping sequences of 180 characters, with early stopping on validation.
- **Key findings (Table 3, text8 test):** **LSTM 1.43**, **BN-LSTM 1.36**. Cited alongside: td-LSTM 1.63; HF-MRNN 1.54; skipping RNN 1.48; HM-LSTM 1.29.
- **Not stated in the section read:** the parameter count and the training length.
- **Parameter estimate (inference):** about 16.3M for one 2000-unit layer with 27-symbol one-hot input and a 27-way softmax, computed as 4 × 2000 × (2000 + 27 + 1) + 2000 × 27 + 27. This assumes one layer and no embedding, neither of which the section states.
- **Bears on:** the nearest published model in *active* size to ours: about 1.43 for a plain LSTM.
- **How it differs from ours:** recurrent; the test sequence is evaluated continuously (state handling not stated in the section read); early-stopped, so probably many passes.
- **Question for us:** none specific.

### P7. Approximating Two-Layer Feedforward Networks for Efficient Transformers (σ-MoE)

- **Authors:** Róbert Csordás, Kazuki Irie, Jürgen Schmidhuber.
- **Year and venue:** 2023. The abs page says "Accepted to EMNLP 2023 Findings".
- **arXiv:** 2310.10837. v1 16 Oct 2023; v2 23 Oct 2023; v3 21 Nov 2023. **Read v3.**
- **Link:** https://arxiv.org/abs/2310.10837. DOI 10.48550/arXiv.2310.10837 (arXiv-issued).
- **Read status:** sections read: §6 setup, §6.1 (Table 1), §6.2 (Table 2), §6.3 (Tables 3-4), Table 10, the limitations paragraph, Appendix B (Tables 8-9).
- **Setting and scale (enwik8):**
  - A Transformer-XL-style model: **41M parameters**, width 512, feed-forward width 2053, 12 layers, 8 heads, context 512, batch 32, dropout 0.1.
  - 100k steps; Adam with learning rate 2.5e-4, cosine decay to 0; gradient clipping 0.25.
  - XL memory equal to the context in training; **4 times the context at evaluation** (App. B).
  - The mixture of experts sits in **every** layer, with 16 experts of group size 128 and K = 4 active. That is 25% of the feed-forward compute, the same fraction as our 2 of 8.
- **Key findings:**
  - Table 3: dense 41M **1.08** against σ-MoE 41M (25% of the feed-forward FLOPs) **1.08**. The MoE matched a dense model with the same *total* parameters.
  - Tables 4 and 10 (enwik8 bits per character):
    - Switch (K = 1, group size 512): 1.08; Switch without dropout: 1.10;
    - Switch variants in Table 10: K = 4, group size 128: 1.10; K = 1, group size 128: 1.11;
    - K = 2, group size 256: 1.09; K = 1, group size 512: 1.09; K = 8, group size 64: 1.08;
    - softmax gating variants: 1.09;
    - S-BASE (K = 4): 1.17; S-BASE (K = 1): 1.32.
  - Table 1: the dense top-K variants score 1.07 to 1.08.
  - The modified dense baseline "performs similarly to the original Transformer XL" (§6).
- **Training characters (inference):** 100k × 32 × 512 = 1.64B (18 passes over 90M enwik8 bytes).
- **Bears on:** whether a mixture of experts helps at small scale; what routing and balance choices cost at about 41M; character-level MoE evidence.
- **How it differs from ours:** enwik8, not text8; 10 times our characters; a different router (sigmoid gate with its own regularisers); K = 4 of 16; XL memory evaluation.
- **Question for us:** does our 46M-total MoE match a 46M dense model at 1.8 passes, as σ-MoE's did at 18 passes, or does it behave like a ~10M dense model?

### P8. Sparse MoE as the New Dropout: Scaling Dense and Self-Slimmable Transformers (SMoE-Dropout)

- **Authors:** Tianlong Chen, Zhenyu Zhang, Ajay Jaiswal, Shiwei Liu, Zhangyang Wang.
- **Year and venue:** 2023. Preprint; no venue is stated in the arXiv text or abs page I read.
- **arXiv:** 2303.01610. v1 2 Mar 2023 (only version). **Read v1.**
- **Link:** https://arxiv.org/abs/2303.01610. DOI 10.48550/arXiv.2303.01610 (arXiv-issued).
- **Read status:** sections read: §4.1 (implementation), §4.2 (Table 1), the depth and width study (text describing Figure 5).
- **Setting and scale:**
  - A reduced Transformer-XL: 4 layers, width 256, feed-forward 8192, 8 heads; enwik8.
  - Adam at 2.5e-4 with cosine decay; batch 22; 400K iterations (§4.1).
  - Not stated in the sections I read: the segment length and the parameter count.
- **Key findings:**
  - Table 1 (Transformer-XL bits per character; "all models are compared under the same number of parameter counts"):
    - dense with dropout **1.1623**;
    - dense with concrete dropout 1.3335; dense with DropBlock 1.2468;
    - THOR 1.3110;
    - **learnable SMoE 1.1896**;
    - SMoE-Dropout 1.1776 (half the experts) and 1.1486 (all experts).
    - Some k labels were partly lost in text extraction.
  - **Inconsistency:** §4.1 says bits per character are measured "on the hold-out validation set", but the Table 1 caption says "Testing performance".
  - Depth and width study: dense training with dropout was best at 2 layers. It beat SMoE-based training at small widths; the example given is 8 experts, but the comparison symbol was lost in extraction.
- **Bears on:** whether a mixture of experts helps at tiny scale. Here a learned SMoE trailed an equal-parameter dense model by **2.35%** (inference: (1.1896 − 1.1623) / 1.1623).
- **How it differs from ours:** enwik8; 4 layers; unknown size and segment length; Transformer-XL evaluation.
- **Question for us:** at our budget, is the MoE itself worth anything over dense? This paper hints it may not be at small width.

### P9. S2MoE: Robust Sparse Mixture of Experts via Stochastic Learning

- **Authors:** Giang Do, Hung Le, Truyen Tran.
- **Year and venue:** 2025. Preprint; the abs comment says "4 pages"; no venue stated.
- **arXiv:** 2503.23007. v1 29 Mar 2025 (only version). **Read v1.**
- **Link:** https://arxiv.org/abs/2503.23007. DOI 10.48550/arXiv.2503.23007 (arXiv-issued).
- **Read status:** sections read: §4.1 setup, §4.2 base results (Table 1), Appendix A.1-A.2 (Table 3).
- **Setting and scale:**
  - A base Transformer-XL of 4 layers, width 256, 8 heads.
  - The feed-forward layer (inner width 512) is divided into 16 experts.
  - Input length 512, batch 48, Adam at 2.5e-4, 100k iterations, on both text8 and enwik8.
  - Not stated in the sections I read: the parameter count and the evaluation protocol.
- **Key findings (Table 1, test bits per character, with k experts used at inference):**
  - text8: SMoE k = 1 gives 1.30 and **k = 2 gives 1.29**; S2MoE k = 2 gives 1.27.
  - enwik8: SMoE k = 2 gives 1.20.
  - There is **no dense baseline**.
- **Training characters (inference):** 100k × 48 × 512 = 2.46B (27 passes).
- **Bears on:** the only text8 MoE number I found. It comes from a tiny 4-layer model trained 15 times longer than ours.
- **How it differs from ours:** much smaller and shallower; 15 times the characters; unknown evaluation.
- **Question for us:** none specific.

### P10. Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity

- **Authors:** William Fedus, Barret Zoph, Noam Shazeer.
- **Year and venue:** 2021-2022. Journal of Machine Learning Research 23 (2022) (PDF header; the abs page says "JMLR").
- **arXiv:** 2101.03961. v1 11 Jan 2021; v2 30 Apr 2022; v3 16 Jun 2022. **Read v3.**
- **Link:** https://arxiv.org/abs/2101.03961. DOI 10.48550/arXiv.2101.03961 (arXiv-issued).
- **Read status:** sections read: §1 contributions, §2.2 (load-balancing loss), §3.1 (the Figure 4 caption and text), Appendix D (lower-compute regimes, Figure 12 caption).
- **Key findings:**
  - Balance coefficient α = 10⁻²: chosen after sweeping 10⁻¹ to 10⁻⁵, as it "balanced load quickly without interfering with training loss" (§2.2).
  - Its small-scale evidence is **few experts on T5-Base** (223M dense): "as few as 2 experts produce compelling gains" over a FLOP-matched dense model (App. D, Figure 12). Values are in the plot only, so I did not record them.
- **Bears on:** our balance coefficient (0.01 is the standard value); MoE gains at small scale.
- **How it differs from ours:** its smallest base is about 20 times our active size; span-corruption pre-training on C4.
- **Question for us:** none beyond confirming 0.01.

### P11. ST-MoE: Designing Stable and Transferable Sparse Expert Models

- **Authors:** Barret Zoph, Irwan Bello, Sameer Kumar, Nan Du, Yanping Huang, Jeff Dean, Noam Shazeer, William Fedus.
- **Year and venue:** 2022. Preprint; no venue stated in the version read.
- **arXiv:** 2202.08906. v1 17 Feb 2022; v2 29 Apr 2022. **Read v2.**
- **Link:** https://arxiv.org/abs/2202.08906. DOI 10.48550/arXiv.2202.08906 (arXiv-issued).
- **Read status:** sections read: §3 (router z-loss paragraph), Table 11 (model sizes), §7 (the paragraph on generalising from small to large scale), Appendix A/B (coefficient lines).
- **Key findings:**
  - Its smallest model in Table 11 is Dense-L (0.8B parameters).
  - Balance coefficient α = 10⁻² and z-loss coefficient c_z = 0.001, the latter chosen by a sweep (§3, App. B).
  - §7: architecture and routing improvements often "vanish, or even reverse, when models are trained for longer or made larger".
- **Bears on:** whether small-scale MoE findings transfer; our balance coefficient. (There are no small configurations to compare with.)
- **How it differs from ours:** 80 times or more our active size.
- **Question for us:** do our Stage 0 conclusions hold at another scale? The paper warns they may not.

### P12. Unified Scaling Laws for Routed Language Models

- **Authors:** Aidan Clark, Diego de las Casas, Aurelia Guy, Arthur Mensch, et al. (DeepMind).
- **Year and venue:** 2022. Preprint; no venue stated in the version read.
- **arXiv:** 2202.01169. v1 2 Feb 2022; v2 9 Feb 2022. **Read v2.**
- **Link:** https://arxiv.org/abs/2202.01169. DOI 10.48550/arXiv.2202.01169 (arXiv-issued).
- **Read status:** sections read: §1 (contributions), §2 (training details), §4 (interpretation paragraph), §5.2, Appendix A (model table), Appendix F.1 and the 15M longer-training paragraph.
- **Setting and scale:**
  - Dense base sizes from **15M** (width 512, 6 layers, 16.5M actual parameters) to 1.3B.
  - 1 to 512 experts; three routing methods: S-BASE, RL-R and Hash.
  - Every model trained for 130B tokens (sequence 2048, batch 256, 250k steps); subword tokens.
- **Key findings:**
  - Routing "improves the performance of language models across all sizes" tried (§1).
  - All three methods predict "diminishing improvements from routing when increasing scale" (§4). So the gain from routing is largest at small base size.
  - The size above which routing stops helping is 937B (S-BASE), 85B (RL-R) and 83B (Hash) parameters (§5.2).
  - App. F: the 15M dense model was not saturated even after 130B tokens. Training 4 times longer lowered validation loss by 0.05, and by 0.07 with 512 experts.
- **Bears on:** whether an MoE helps at about 10M active. It predicts yes, in a data-rich regime.
- **How it differs from ours:** 130B tokens against our 164M characters; subword tokens; the experts here have far more data each.
- **Question for us:** at 1.8 passes, does each expert see enough data for routing to pay off? (Inference: each expert sees about 2/8 of the 164M character positions, about 41M.)

### P13. Shortformer: Better Language Modeling using Shorter Inputs

- **Authors:** Ofir Press, Noah A. Smith, Mike Lewis.
- **Year and venue:** 2020-2021. The abs page says "To appear at ACL 2021".
- **arXiv:** 2012.15832. v1 31 Dec 2020; v2 3 Jun 2021. **Read v2.**
- **Link:** https://arxiv.org/abs/2012.15832. DOI 10.48550/arXiv.2012.15832 (arXiv-issued).
- **Read status:** sections read: §1 (the early-token curse), §2 (non-overlapping and sliding-window inference), §3 (Table 1 and its discussion).
- **Setting and scale:**
  - The Baevski and Auli model on WikiText-103 (word level), retrained at each subsequence length L with 9,216 tokens per batch.
  - Each model is evaluated two ways: non-overlapping windows of length L, and a sliding window with stride 1.
- **Key findings (Table 1, dev perplexity, non-overlapping against sliding):**

  | Subsequence length L | Non-overlapping | Sliding, stride 1 |
  |---|---|---|
  | 128 | 23.81 | 19.76 |
  | 256 | 21.45 | 18.86 |
  | 512 | 20.10 | 18.41 |
  | 3072 | 18.65 | 17.92 |

  §1: with inputs of 128, only about 50% of tokens see 64 or more tokens of history.
- **My conversion (inference):** the relative excess of the non-overlapping loss, (ln N − ln S) / ln S, is:
  - L = 128: (3.1701 − 2.9837) / 2.9837 = 6.25%;
  - L = 256: (3.0657 − 2.9370) / 2.9370 = **4.38%**;
  - L = 512: (3.0007 − 2.9129) / 2.9129 = 3.02%;
  - L = 3072: about 1.38%.
- **Bears on:** the size of the non-overlapping-window penalty. This is the only direct within-model measurement I found, and it is word level.
- **How it differs from ours:** words, not characters. A 256-word window holds far more text than our 256 characters, so the magnitudes do not transfer.
- **Question for us:** what is our own non-overlapping versus sliding penalty, and is it the same for every arm?

### P14. DiLoCo: Distributed Low-Communication Training of Language Models

- **Authors:** Arthur Douillard, Qixuan Feng, Andrei A. Rusu, Rachita Chhaparia, Yani Donchev, Adhiguna Kuncoro, Marc'Aurelio Ranzato, Arthur Szlam, Jiajun Shen.
- **Year and venue:** 2023-2024. Preprint; no venue stated in the version read.
- **arXiv:** 2311.08105. v1 14 Nov 2023; v2 2 Dec 2023; v3 23 Sep 2024. **Read v3.**
- **Link:** https://arxiv.org/abs/2311.08105. DOI 10.48550/arXiv.2311.08105 (arXiv-issued).
- **Read status:** sections read: §3 setup, Tables 2-4, the opening of the outer-optimizer paragraph. *Headline numbers only; local averaging is covered in depth by another researcher.*
- **Setting:**
  - 150M model on C4, starting from a checkpoint pretrained for 24,000 steps.
  - 8 workers, H = 500 inner steps, non-i.i.d. data shards, Nesterov outer optimizer.
- **Key findings:**
  - Table 2, at equal compute and data: the 8×-batch data-parallel baseline reaches perplexity **15.30**; DiLoCo reaches **15.02**.
  - Table 4 reports DiLoCo's improvement over a *single-worker* baseline that used 8 times less compute (60M: 4.33%; 150M: 7.45%; 400M: 7.49%). It is **not** a gap against equal compute.
  - Plain SGD (equivalent to FedAvg) and Adam as outer optimizers "performed poorly" (values only in Figure 6).
- **My conversion (inference):** (ln 15.02 − ln 15.30) / ln 15.30 = −0.68% in log-perplexity. That is, DiLoCo was slightly *better* than data parallelism, from a pretrained start.
- **Bears on:** calibrating the 5% criterion.
- **How it differs from ours:** pretrained start; outer momentum; H = 500; 150M; C4 subwords.
- **Question for us:** see question 1 of the brief.

### P15. Communication-Efficient Language Model Training Scales Reliably and Robustly: Scaling Laws for DiLoCo

- **Authors:** Zachary Charles, Gabriel Teston, Lucio Dery, Keith Rush, Nova Fallen, Zachary Garrett, Arthur Szlam, Arthur Douillard.
- **Year and venue:** 2025. Preprint; no venue stated in the version read.
- **arXiv:** 2503.09799. v1 12 Mar 2025 (only version listed on the abs page as fetched 2026-10-11). **Read v1.**
- **Link:** https://arxiv.org/abs/2503.09799. DOI 10.48550/arXiv.2503.09799 (arXiv-issued).
- **Read status:** sections read: §2.2, §3 (Table 3 and methodology), §4 Finding 1 (Tables 4-5). *Headline only.*
- **Setting:**
  - Chinchilla-style models of 35M to 2.4B parameters (plus 4B and 10B) on C4.
  - Token budgets Chinchilla-optimal. Table 3 prints 70M tokens for the 35M model; at 20 tokens per parameter that would be 700M, and I could not resolve which is right.
  - H = 30; Nesterov outer momentum 0.9; inner AdamW with β2 = 0.99 and weight decay 1/T; cosine decay to 5%; hyperparameters swept.
- **Key findings (Table 4, evaluation loss against data-parallel training):**
  - 35M: data-parallel 3.485; DiLoCo with M = 1 worker −0.1%; M = 2 +0.7%; **M = 4 +2.0%**; **M = 8 +3.9%**.
  - 2.4B: M = 4 +0.3%; M = 8 +1.1%.
  - The text says the M = 4 gap shrinks from 2% at 35M to 0.26% at 2.4B. Table 4 labels a row "335M" where Table 3 says 330M, a minor inconsistency in the paper.
- **Bears on:** calibrating the 5% criterion at our model size.
- **How it differs from ours:** tuned outer momentum; H = 30 rather than 125; subword C4; Chinchilla budgets.
- **Question for us:** see question 1 of the brief.

### P16. Structured Denoising Diffusion Models in Discrete State-Spaces (D3PM)

- **Authors:** Jacob Austin, Daniel D. Johnson, Jonathan Ho, Daniel Tarlow, Rianne van den Berg.
- **Year and venue:** 2021. The PDF header says NeurIPS 2021.
- **arXiv:** 2107.03006. v1 7 Jul 2021; v2 13 Jul 2021; v3 22 Feb 2023. **Read v3.**
- **Link:** https://arxiv.org/abs/2107.03006. DOI 10.48550/arXiv.2107.03006 (arXiv-issued).
- **Read status:** sections read: §5.1 (text8, Table 1), Appendix B.2 (experimental details; Tables 5-6).
- **Setting and scale:**
  - text8, trained and evaluated "in chunks of length 256", with negative log-likelihood "reported on the entire test set" (§5.1, Table 1 caption). The text does not say whether the chunks overlap; I read it as non-overlapping chunks.
  - Autoregressive baseline: a "standard transformer decoder" with the same parameter count as the 12-layer, **70M** encoder (12 heads, MLP 3072, query/key/value width 768).
  - 1M steps, batch 512; learning rate 5e-4 with 10k warm-up and inverse-square-root decay; random crops of the training text (App. B.2).
- **Key findings (Table 1):**
  - **Transformer decoder (ours) 1.23** bits per character.
  - The table also lists Al-Rfou's 1.18 and Transformer-XL's 1.08, copied from those papers, which used much longer evaluation contexts. **The table mixes evaluation protocols.**
  - The best diffusion model scores 1.44-1.45.
  - Results use two seeds.
- **Training characters (inference):** 1M × 512 × 256 = 131B (about 1,456 passes; 800 times ours).
- **Bears on:** **the closest published protocol match to ours**: a context of 256 with chunked evaluation.
- **How it differs from ours:** dense, about 70M; 800 times the characters.
- **Question for us:** with protocol and context matched, a dense 70M model reaches 1.23 at convergence. How much of our 0.21 gap closes with more data?

### P17. Argmax Flows and Multinomial Diffusion: Learning Categorical Distributions

- **Authors:** Emiel Hoogeboom, Didrik Nielsen, Priyank Jaini, Patrick Forré, Max Welling.
- **Year and venue:** 2021. NeurIPS 2021 (abs comment and PDF).
- **arXiv:** 2102.05379. v1 10 Feb 2021; v2 28 May 2021; v3 22 Oct 2021. **Read v3.**
- **Link:** https://arxiv.org/abs/2102.05379. DOI 10.48550/arXiv.2102.05379 (arXiv-issued).
- **Read status:** sections read: §6 (language modelling, Table 3), Appendix B.1 (Tables 6-7), Appendix C (Discrete Flows reproduction, Table 8).
- **Setting:**
  - text8 with sequence length 256 and the 90M/5M/5M split.
  - Argmax AR Flow: a 2-layer LSTM with 2048 hidden units, 40 epochs, batch 64, Adam at 1e-3, dropout 0.25.
- **Key findings:**
  - Table 3: Argmax Flow (AR) **1.39** bits per character on text8; multinomial text diffusion (12-layer transformer) 1.72. Internal discrepancy: Table 3 prints 1.39, but Table 8 (Appendix C) and a later appendix table print 1.38 for the same model.
  - The table also cites T64 at 1.13 and Transformer-XL at 1.08 (mixed protocols again).
  - Appendix C: the authors' reimplementation could not reproduce Discrete Flows' text8 language result. They state they currently assume those language experiments are not reproducible.
- **Bears on:** a 256-chunk text8 point (1.39 at 40 passes). It is a flow model, not a plain autoregressive language model, and I did not read how its reported likelihood relates to an exact one.
- **How it differs from ours:** a flow model; an LSTM; 40 passes.
- **Question for us:** none.

### P18. Discrete Flows: Invertible Generative Models of Discrete Data

- **Authors:** Dustin Tran, Keyon Vafa, Kumar Krishna Agrawal, Laurent Dinh, Ben Poole.
- **Year and venue:** 2019. Preprint; no venue stated in the version read.
- **arXiv:** 1905.10347. v1 24 May 2019 (only version). **Read v1.**
- **Link:** https://arxiv.org/abs/1905.10347. DOI 10.48550/arXiv.1905.10347 (arXiv-issued).
- **Read status:** sections read: §4.5 (text8, the Figure 3 table), §5.
- **Setting:** bipartite flows on text8 with sequence length 256, batch 128; each flow is a 2-3 layer transformer of width 512.
- **Key findings:** Figure 3 table: 8 flows with scale, **1.23**. It cites LSTM 1.43 and T64 1.13.
- **Caveat:** **P17's Appendix C disputes the reproducibility of this text8 result.**
- **Bears on:** listed only because D3PM's Table 1 cites it. Do not use it as a baseline.
- **Question for us:** none.

### P19. Simple and Effective Masked Diffusion Language Models (MDLM)

- **Authors:** Subham Sekhar Sahoo, Marianne Arriola, Yair Schiff, Aaron Gokaslan, Edgar Marroquin, Justin T. Chiu, et al.
- **Year and venue:** 2024. The abs page says "NeurIPS 2024".
- **arXiv:** 2406.07524. v1 11 Jun 2024; v2 10 Nov 2024. Opened v2.
- **Link:** https://arxiv.org/abs/2406.07524.
- **Read status:** opened only to look for a text8 table; a search for "text8" in the v2 text found no match. **Nothing recorded from this paper.**

---

## Comparison table

**text8** (bits per character on the standard 5M test split unless noted).

| Paper (locator, version) | Model | Parameters | Training budget (characters; passes over 90M) | Context and evaluation protocol | Test bpc |
|---|---|---|---|---|---|
| **Ours** (stage0-report §3.3) | top-2 of 8 MoE, 6 layers, width 384 | 46.05M total, ~10-11M active | 20k × 32 × 256 = 0.164B; **1.8** | context 256; **non-overlapping 256-character windows**, whole test split | **1.4353-1.4388** (mean 1.4376) |
| Cooijmans et al. (Table 3, v5) | LSTM, 2000 units | not stated (~16.3M, my estimate) | early-stopped; length not stated; batch 128 × 180 | recurrent, whole "test sequence" (state handling not stated) | 1.43 |
| Cooijmans et al. (Table 3, v5) | BN-LSTM, 2000 units | not stated | as above | as above | 1.36 |
| Krause et al. (Table 2, v3) | small LSTM / small mLSTM (hidden 512 / 450) | not stated | not stated | recurrent | 1.64 / 1.59 |
| Krause et al. (Table 2, v3) | unregularised mLSTM (hidden 1900) | not stated | not stated | recurrent | 1.40 |
| Krause et al. (Table 2, §4.3, v3) | large mLSTM with embedding, weight norm, variational dropout | ~45M | not stated | recurrent | 1.27 |
| Hoogeboom et al. (Table 3, App. B.1, v3) | Argmax AR Flow (2-layer LSTM, 2048) | not stated | 40 epochs; **40** | 256-character sequences; flow model | 1.39 (Table 8 prints 1.38) |
| **Austin et al., D3PM (Table 1, App. B.2, v3)** | **transformer decoder, 12 layers** | **~70M** | 1M × 512 × 256 = 131B; **~1,456** | **chunks of 256 (closest match to ours)**, entire test set | **1.23** |
| Tran et al. (Fig. 3, v1) | bipartite discrete flow | not stated | not stated | 256-character sequences | 1.23 (reproducibility disputed in P17 App. C) |
| Do et al., S2MoE (Tables 1 and 3, v1) | Transformer-XL, 4 layers, width 256, 16-expert SMoE, k = 2 | not stated | 100k × 48 × 512 = 2.46B; **27** | input 512; evaluation not stated | 1.29 |
| Al-Rfou et al. (Table 1, v2) | T12, vanilla transformer | 44M train / 41M inference | 8M × 16 × 512 = 65.5B; **728** | context 512, stride-1 sliding | 1.18 |
| Al-Rfou et al. (Table 2, v2) | T64, *evaluated* at context 32 / 64 / 128 / 256 / 512 | 235M / 219M | best at ~2.5M steps: 20.5B; **228** (4M steps = 32.8B) | stride-1 sliding at each context | 1.34 / 1.26 / 1.20 / 1.16 / 1.13 |
| Sukhbaatar et al. (Table 1, v2) | adaptive span, small, 12 layers | 38M | 900K × 64 × 512 = 29.5B; **328** | 512-character blocks with XL cache; span up to 8192 (mean 314) | 1.11 |
| Beltagy et al. (Tables 2 and 12, v2) | Longformer, small | 41M | 5 phases, ~52.3B; **581** | windows of 32,256 advanced by 512, last 512 scored | 1.10 |
| Sukhbaatar et al. (Table 1, v2) | adaptive span, large, 24 layers | 209M | 270K × 64 × 512 = 8.8B; **98** | as above | 1.07 |
| Dai et al. (Table 3, v3) | Transformer-XL, 24 layers | 277M | not stated in the paper text | memory; attention 784 in training, 3,800 in evaluation | 1.08 |

**enwik8** (bits per byte; for scale and MoE evidence only; different data).

| Paper (locator, version) | Model | Parameters | Training budget | Protocol | Test |
|---|---|---|---|---|---|
| Al-Rfou et al. (Table 3, v2) | T12 / T64 | 41M / 219M (inference) | as for text8 | stride-1, context 512 | 1.11 / 1.06 |
| Dai et al. (Table 2, v3) | Transformer-XL, 12 / 18 / 24 layers | 41M / 88M / 277M | not stated | memory (3,800 at evaluation for the 18 and 24-layer models) | 1.06 / 1.03 / 0.99 |
| Sukhbaatar et al. (Table 2, v2) | adaptive span, small / large | 39M / 209M | small 600K-900K steps; large 150K + 20K | XL cache | 1.02 / 0.98 |
| Beltagy et al. (Table 2, v2) | Longformer, small | 41M | ~52B | long windows | 1.00 |
| **Csordás et al., σ-MoE (Tables 3, 4 and 10, v3)** | dense / σ-MoE (K = 4 of 16, 25% of feed-forward FLOPs) / Switch | **41M each** | 100k × 32 × 512 = 1.64B; **18** | XL memory, 4 times the context at evaluation | **1.08 / 1.08** / 1.08 |
| Chen et al., SMoE-Dropout (Table 1, v1) | 4-layer Transformer-XL: dense with dropout / learned SMoE | "same parameter counts"; number not stated | 400K iterations, batch 22, segment length not stated | Transformer-XL; validation or test wording inconsistent | 1.1623 / 1.1896 |
| Do et al., S2MoE (Table 1, v1) | 4-layer SMoE, k = 2 | not stated | 2.46B; 27 | not stated | 1.20 |

---

## Synthesis for question 6

### A. Is about 1.44 bits per character plausible?

**What the papers show:**

- Every published **autoregressive transformer** text8 result I found lies between 1.07 and 1.29 (S2MoE's tiny 4-layer model gives the 1.29).
- Every one of them used **15 to 800 times more training characters** than our 0.164B, that is 27 to about 1,456 passes against our 1.8: S2MoE 27 passes; adaptive span 98-328; T12 728; Longformer 581; D3PM about 1,456 (P1, P3, P4, P9, P16).
- Most were also evaluated with **512 characters or more of context per prediction**: stride-1 sliding windows, XL memory, or 32k windows.
- The one transformer evaluated like ours, in **256-character chunks**, is D3PM's dense 12-layer, ~70M decoder: **1.23** after about 1,456 passes (P16).
- The published models closest to our **active** size are recurrent:
  - plain LSTM with 2000 units: **1.43** (P6);
  - unregularised mLSTM: **1.40** (P5).

  Both evaluate the test sequence continuously and train far longer (early stopping).
- I found **no published text8 or enwik8 result at about 2 passes or about 164M training characters**, and no published learning curve that reaches our budget.

**Inferences:**

- Our 1.4376 is 0.21 bits per character (16.9%) above D3PM's protocol-matched 1.23, computed as (1.4376 − 1.23) / 1.23. That model has about 7 times our active parameters and 800 times our data. A gap of that size is unsurprising, but no paper lets me predict the value expected at 164M characters.
- Our number sits beside the plain 16-20M recurrent baselines (1.40-1.43), and those had far more training and continuous context.
- **Overall (inference):** 1.44 is plausible for this budget and protocol. It is **not unusually strong**. It is weaker than the converged literature for reasons that are mostly budget and evaluation protocol, and nothing I read points to a defect. Equally, nothing I read can rule out a few hundredths of a bit of hyperparameter slack, because there is no published run at this budget.

### B. How much does non-overlapping 256-character evaluation raise bits per character?

**What the papers show:**

- **No direct measurement on text8 or enwik8 was found.**
- The only direct within-model measurement I found is Shortformer's Table 1 (P13), at word level on WikiText-103. At L = 256, non-overlapping evaluation gave perplexity 21.45 against 18.86 for a stride-1 sliding window.
- Al-Rfou's Table 2 (P1) gives the bits per character of one text8 model (T64) when every prediction gets a fixed context of 32, 64, 128, 256 or 512 characters. (My reading: "given different context sizes" with the stride-1 procedure of the Evaluation section.)

**Inferences, with arithmetic:**

- **Shortformer conversion:** a relative loss excess of (ln 21.45 − ln 18.86) / ln 18.86 = **4.38%** at L = 256 (6.25% at L = 128; 3.02% at L = 512). 256 words is far more text than 256 characters, so this magnitude **does not transfer** to us. It only shows that the penalty is real and grows as windows get shorter.
- **Character-level bound from Al-Rfou Table 2.** Let l(c) be the loss of a character predicted with c characters of context.
  - In a non-overlapping 256-character window, positions see c = 0 to 255, and the window score is the mean of l(c).
  - Assume l(c) falls as c grows (an assumption, not a measurement). Bounding each interval by the value at its right end gives a **lower bound**:

    (32 × 1.34 + 32 × 1.26 + 64 × 1.20 + 128 × 1.16) / 256 = **1.205**

    This uses the lowest known loss in each interval, and l(32) = 1.34 as a floor for c < 32.
  - That is **at least +0.045 bits per character (+3.9%)** over stride-1 evaluation at context 256 (1.16), and **at least +0.075 (+6.6%)** over context 512 (1.13), for a model of T64's quality.
  - The upper side depends on the unknown loss over the first 32 positions. If those average 1.6 to 2.0 bits per character, the non-overlapping average is about 1.28 to 1.33. That would be **+0.12 to +0.17 bits per character over stride-1 at 256**. These upper figures rest on an assumed number and are illustrative only.
- **Effect on our gaps (inference):** all arms were scored the same way. If the protocol penalty were the same absolute amount in every arm, sliding evaluation would lower the denominator and *raise* the relative gaps slightly. For example, the +6.1% gap is 0.0877 bits per character; over a denominator of 1.34-1.39 instead of 1.44 it becomes 6.3-6.5%. Whether the penalty really is equal across arms is untested.

### C. Is a 5% relative allowance large or small?

5% of 1.4376 is **0.072 bits per character** (inference).

**Published differences of about this size** (each relative change is my arithmetic, taken against the higher number):

| Comparison | Change | Relative | Source |
|---|---|---|---|
| T12 (41M) to T64 (219M), text8, 5.3× the parameters | 1.18 to 1.13 | 4.2% | P1 Table 1 |
| Transformer-XL 12 layers (41M) to 24 layers (277M), enwik8, 6.8× | 1.06 to 0.99 | 6.6% | P2 Table 2 |
| Al-Rfou T12 to Transformer-XL 12 layers, same size class, enwik8 | 1.11 to 1.06 | 4.5% | P2 Table 2 |
| T12 to adaptive span, small, text8, same size class | 1.18 to 1.11 | 5.9% | P3 Table 1 |
| Adaptive span small (38M) to large (209M), text8 | 1.11 to 1.07 | 3.6% | P3 Table 1 |
| LSTM to BN-LSTM, text8 | 1.43 to 1.36 | 4.9% | P6 Table 3 |
| Unregularised to regularised mLSTM, text8 | 1.40 to 1.27 | 9.3% | P5 Table 2 |
| T64 at evaluation context 128 to 512 | 1.20 to 1.13 | 5.8% | P1 Table 2 |
| T64 at evaluation context 256 to 512 | 1.16 to 1.13 | 2.6% | P1 Table 2 |
| enwik8 41M dense against σ-MoE | 1.08 against 1.08 | 0% | P7 Table 3 |
| enwik8 41M, Switch with and without dropout | 1.08 against 1.10 | 1.9% | P7 Table 4 |
| SMoE-Dropout paper, dense against learned SMoE (enwik8) | 1.1623 against 1.1896 | 2.35% | P8 Table 1 |

**Distributed training against centralized, headline numbers only** (local averaging is covered in depth by another researcher):

- DiLoCo scaling laws (P15, Table 4), at **35M** with tuned Nesterov outer momentum and H = 30 on C4: **+2.0%** evaluation loss with 4 workers and **+3.9%** with 8.
- Original DiLoCo (P14, Table 2), at 150M from a pretrained start, 8 workers, H = 500: slightly *better* than equal-compute data parallelism (perplexity 15.02 against 15.30, −0.68% in log-perplexity, my arithmetic). Its Table 4 is not an equal-compute gap and should not be quoted as one.
- Relative loss gaps do not depend on the unit (bits or nats). But a per-subword-token loss and a per-character loss are different quantities, so these comparisons are only rough.

**Inferences:**

- **By the standards of converged text8 and enwik8 tables, 5% is a generous allowance.** It equals roughly the gain from a 5-7 times larger model, or from one architecture generation at the same size (vanilla transformer to Transformer-XL or adaptive span; LSTM to BN-LSTM).
- **In our regime it may not be generous.** At 1.8 passes, bits per character are still falling steeply with data (P12 App. F: even a 15M model was unsaturated after 130B tokens). So 0.072 bits per character may correspond to a much smaller compute factor than in converged tables. The project's own validation curve can settle this (Gaps, item 3).
- **Against distributed methods:**
  - a tuned local-averaging method stays under 5% at 35M with 4 workers (+2.0%) and with 8 workers (+3.9%);
  - our plain-averaging arm (+6.1%: 4 workers, H = 125, no outer momentum, fresh AdamW) is about 3 times DiLoCo's 4-worker gap at 35M (6.1 / 2.0).
  - So the 5% criterion is **neither impossibly strict nor lax**: published tuned methods meet it at about our size, and our simplest arm does not.

### D. Does a mixture of experts help at about 10M active parameters?

**What the papers show:**

- **Clark et al. (P12):** routing helped at every size tried, down to a 15M dense base, with gains largest at small sizes. But that was at 130B tokens on subwords.
- **σ-MoE (P7):** at 41M on enwik8 (18 passes), a 25%-active MoE (our ratio) **matched, and did not beat**, a dense model with the same *total* parameters (1.08 against 1.08). Routing variants moved results by at most 0.03 (1.08 to 1.11), except S-BASE.
- **SMoE-Dropout (P8):** at 4 layers on enwik8, a learned SMoE trailed an equal-parameter dense model with dropout by 2.35%. Dense training beat SMoE training at small widths.
- **S2MoE (P9):** a tiny 4-layer text8 MoE reached 1.29 at 27 passes, with no dense baseline.
- **Switch (P10):** its "few experts" evidence is on a 223M dense base, so it says nothing about a ~10M model.
- **ST-MoE (P11):** warns that small-scale MoE findings can vanish or reverse at larger scale or longer training.

**Inferences:**

- Our 46M-total MoE should land somewhere between a ~10M dense and a ~46M dense model. σ-MoE suggests near the 46M end at 18 passes. At 1.8 passes, each expert sees only about 41M character positions (2/8 of 164M), and no paper tests that regime.
- So I cannot say from the literature whether the MoE helps our baseline. The comparison needs a dense run (Gaps, item 4).

### E. Reasons our baseline might be unusually strong or weak

| Choice | Likely direction | Evidence and reasoning |
|---|---|---|
| 1.8 passes (163.8M characters) | **weaker, by much the largest margin** | Every published transformer row with a stated budget used 15 to 800 times more characters, 27 to about 1,456 passes (table above). P12 App. F: small models stay unsaturated for a very long time. |
| Non-overlapping 256-character evaluation | **weaker**, by at least ~0.045 bits per character against stride-1 at the same context, and at least ~0.075 against context 512 | Al-Rfou Table 2 bound (inference, §B); Shortformer at word level. |
| Context 256 in training | slightly weaker than 512 | T64 evaluated at 256 against 512 is +0.03 (2.6%) at convergence (P1 Table 2); P3 Figure 3 shows gains up to 4096 (plot only). |
| No dropout, no weight decay | probably neutral at 1.8 passes (inference) | Converged models need regularisation (mLSTM 1.40 to 1.27; Al-Rfou used dropout 0.2-0.55). With each character seen fewer than twice, overfitting is unlikely. But σ-MoE's Switch was 0.02 worse *without* dropout at 18 passes (P7 Table 4), so neutral is a guess. |
| Constant 1e-3, then linear decay over the last 20% | no evidence either way | Adam at 1e-3 is the common choice in P5 and P6. No paper I read tests short-decay schedules at this scale. |
| Balance loss 0.01 | standard | α = 10⁻² in Switch (swept 10⁻¹ to 10⁻⁵) and in ST-MoE (P10, P11). |
| Top-2 of 8 experts at width 384 | likely second-order | σ-MoE's routing ablations at 41M moved results by ≤0.03 bits per character (1.08 to 1.11), except S-BASE (P7 Tables 4 and 10). SMoE-Dropout found dense beat SMoE at small width (P8). |
| Loss at every position; whole test split; seeds within 0.0035 | sound practice | P1 Table 4: dropping the loss at every position is catastrophic for vanilla transformers; ours keeps it. |

---

## Candidates for the joint reading list

1. **Al-Rfou et al. 2018, arXiv:1808.04444.** One short paper gives the text8 transformer anchor at our total size (T12, 41M, 1.18). It also has the only text8 table of bits per character against evaluation context, which bounds what our protocol costs.
2. **Csordás, Irie and Schmidhuber 2023, arXiv:2310.10837 (σ-MoE).** The only small-scale character-level MoE result I found with a parameter-matched dense baseline and routing and balance ablations at 41M (EMNLP 2023 Findings).
3. **Charles et al. 2025, arXiv:2503.09799 (DiLoCo scaling laws).** Its Table 4 shows what tuned local averaging costs at 35M (+2.0% with 4 workers, +3.9% with 8), which calibrates the 5% criterion. It overlaps question 1, so select it there if that researcher already lists it.

---

## Gaps (questions no paper answers that our existing harness could)

1. **Sliding-window re-evaluation of the saved Task B models.** Score each character with a full 256-character context, for example a 256-window advanced by 1 or by 32 characters. This measures our own protocol penalty in every arm, and shows whether the +6.1 / +7.6 / +10.8% gaps change. It needs no retraining.
2. **Loss by position inside the 256-character window**, from the existing evaluation code. It gives the early-token curve l(c) for our model directly and replaces the bound in §B.
3. **Equivalent-compute reading of the gaps.** On the centralized validation curve, find the step at which centralized reaches each arm's final bits per character. That converts each gap into "the arm is worth X% of the centralized steps" and shows whether 5% is lax or strict in our regime. This uses existing logs, with the caveat that validation and test sets differ (closeout §3.4).
4. **Dense baselines at the same budget:** one of ~10M (FLOP-matched to our active parameters) and one of ~46M (parameter-matched). These say whether the MoE helps at 164M characters, which σ-MoE and Clark cannot say for this regime.
5. **A longer centralized run** (2 or 4 times the steps). It gives the slope of bits per character against data at our scale, and so a data-equivalent reading of 0.072 bits per character.
6. **Small sensitivity sweeps of the centralized baseline:** balance coefficient 0.001 to 0.1, dropout or weight decay, context 512. These bound how much hyperparameter slack the baseline has.

---

## Could not verify

- **Transformer-XL's training steps and batch size for enwik8 and text8:** not in the paper text; the paper defers to released code, which I did not read. Also the 12-layer model's evaluation attention length.
- **Cooijmans et al.:** the LSTM's training length and parameter count (I give only my own estimate, which assumes one layer).
- **Krause et al.:** the text8 training length, and parameter counts for the small and unregularised rows.
- **SMoE-Dropout:** parameter count and segment length; whether Table 1 is validation or test.
- **S2MoE:** parameter count and evaluation protocol.
- **DiLoCo scaling laws, Table 3:** whether the 35M token budget is 70M (as printed) or 700M.
- **Whether D3PM's 256-character test chunks are non-overlapping:** the text says "chunks of length 256" only.
- **Not found in this search:**
  - a published text8 or enwik8 result at about 2 passes or 164M training characters;
  - a direct measurement of non-overlapping against sliding-window evaluation on text8 or enwik8;
  - a character-level MoE at about 10M active parameters with a dense baseline on text8.
- **Venues not stated in the version read:** Longformer, Clark et al., ST-MoE, SMoE-Dropout, S2MoE, DiLoCo, DiLoCo scaling laws, Discrete Flows. I recorded these as preprints.
- **Leads seen in search results but never opened, so unverified:**
  - arXiv 2405.14131 (perturbed cosine router; enwik8 and text8 named in the snippet);
  - arXiv 2607.16427 (multi-level context MoE; enwik8);
  - arXiv 2606.19036 (MoE discontinuities; enwik8);
  - arXiv 1904.08378 (dynamic evaluation of transformers);
  - arXiv 1808.05908 (decoding the past);
  - arXiv 2308.07037 (Bayesian Flow Networks; text8);
  - arXiv 1611.06188 (variable computation in RNNs; text8);
  - arXiv 2102.11417 (Legendre Memory Unit).
- **Numbers seen only as citations inside other papers** (I did not open the original papers, so treat these as second-hand):
  - RHN 1.27 (Zilly et al., arXiv 1607.03474);
  - HM-LSTM 1.29 (Chung et al., arXiv 1609.01704);
  - mLSTM with dynamic evaluation 1.19 (Krause et al., arXiv 1709.07432).

---

## Query log

All times are local (TST), from the `date` command on 2026-10-11.

- **10:29:39:** session start. Read the brief, `stage0-report.md` §§2 and 3.3, and `stage0-closeout.md` §3.4.
- **~10:30, WebSearch (standard), discovery only; no numbers taken from snippets:**
  1. "character-level language model mixture of experts enwik8 text8" (led to S2MoE 2503.23007; other MoE leads not opened);
  2. "text8 bits per character small model" (pointed back to the mLSTM paper; the parent project's own Hugging Face card appeared and was ignored);
  3. "enwik8 sliding window evaluation non-overlapping bits per character" (no character-level measurement found; general discussion only).
- **~10:30 to 10:31:18, arxiv.org PDFs (3 s between requests, all HTTP 200):** 1808.04444, 1901.02860, 1905.07799, 2004.05150, 1609.07959, 1603.09025, 2310.10837, 2303.01610, 2101.03961, 2202.08906, 2202.01169, 2012.15832, 2311.08105, 2503.23007.
- **10:31:24, export.arxiv.org API:** one id_list query for the 14 IDs, giving first and last version dates.
- **~10:35 to 10:37:00, arxiv.org PDFs (all 200):** 2107.03006, 2102.05379, 1905.10347, 2406.07524, 2503.09799. These came from a lead I reasoned out myself: discrete-diffusion papers use 256-character text8 chunks with autoregressive baselines.
- **~10:38 to 10:39:55, arxiv.org abs pages for 18 IDs:** version histories and comments, parsed with a local script run as `python -I`.
- **10:45:43, abs page for 2406.07524.**
- **Not used:** Semantic Scholar, OpenAlex, Papers with Code or any other leaderboard. There were no 429 or 503 responses.

**What I did not cover:**

- recent (2023-2026) small character-level or byte-level transformer runs other than the papers above (for example hierarchical or hourglass transformers, MambaByte, SpaceByte; most report enwik8 only);
- dynamic evaluation;
- compression baselines (cmix, paq);
- ALiBi's sliding-window discussion (Press et al. 2108.12409), which is word level;
- the Transformer-XL and Longformer code configurations;
- citation chasing through OpenAlex;
- the MoE leads listed under "Could not verify";
- local-SGD and DiLoCo literature beyond two headline tables (another researcher's strand).
