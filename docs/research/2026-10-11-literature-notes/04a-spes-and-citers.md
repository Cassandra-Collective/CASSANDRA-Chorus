# Question 4a: SPES in full, and papers citing SPES or FlexOlmo

| | |
|---|---|
| Date | 2026-10-11 (all fetches 10:28 to 10:48 local time, machine clock "TST") |
| Scope | The SPES-and-citations half of question 4 of `docs/research/2026-10-11-deep-research-prompt.md` |
| Method | Raw paper text only: arXiv PDFs converted with `pdftotext -layout`, plus arXiv HTML stripped to text where PDF tables were garbled. Version history from the arXiv API and the abs pages. SPES code read from raw.githubusercontent.com and never run. Citation graphs from OpenAlex and the Semantic Scholar API. WebSearch was used only to discover papers. No number below comes from a search snippet or a WebFetch summary; WebFetch was not used at all. |
| Conventions | "(inference)" marks my reasoning, not a paper's claim. "Locator" means section, table or figure, and version. Quotes are under 15 words. |

Our setting, for comparison throughout: 46.05M-parameter character-level MoE (text8), 6 layers, width 384, 8 experts (hidden 768), top-2, Switch balance loss 0.01. N = 4 workers, H = 125, 40 rounds, a fresh AdamW every round, plain averaging, IID data, compute matched to 20,000 centralized steps. Test bits-per-character (bpc) gaps to centralized: full averaging +6.1%, partial update +7.6%, sliced +10.8%. In additive steps: local averaging +6.1, partial updates +1.4, masked routing +3.2.

---

## Papers

### 1. SPES: Pretraining A Large Language Model using Distributed GPUs: A Memory-Efficient Decentralized Paradigm

- **Authors:** Jinrui Zhang, Chaodong Xiao, Aoqi Wu, Xindong Zhang, Lei Zhang (Hong Kong Polytechnic University; OPPO Research Institute).
- **Year and venue:** 2026, preprint. The v3 PDF header reads "Preprint. June 16, 2026"; no venue is stated.
- **arXiv:** 2602.11543.
  - v1: Thu 12 Feb 2026 04:02:45 UTC.
  - v2: Mon 4 May 2026 04:04:29 UTC.
  - v3: Mon 15 Jun 2026 05:42:32 UTC.
  - Source: arXiv abs page and API, fetched 2026-10-11.
- **Link and DOI:** https://arxiv.org/abs/2602.11543, DOI 10.48550/arXiv.2602.11543 (DataCite, via OpenAlex).
- **Code and licence:** https://github.com/zjr2000/SPES, Apache-2.0. GitHub API on 2026-10-11: created 2026-02-08, last push 2026-05-08 (before v3), 24 stars, 0 forks, not archived.
- **Read status:**
  - v3: full text, PDF plus HTML for the tables.
  - v1 and v2: diffed word by word against v3 (HTML text).
  - v1 sections read directly: §3.2 to §4.2, Table 1, Table 4, Appendices B and E.
  - Code: files read in full are `spes/spes/spes_server.py`, `spes/spes/spes_server_knowledge_transfer.py`, `spes/spes/spes_utils.py`, `spes/custom_sparse_glu_impl.py`, `spes/decayed_load_balance_loss.py` and `run_scripts/run_parameter_server.sh`. Read in part: `scripts/train.py` (lines 140 to 210), `spes/train.py` (lines 265 to 304, 860 to 939 and 1340 to 1580), the `SPESConfig` block of `spes/config.py`, and the 1B configs (centralized, DiLoCo, SPES node 0 and node 1).

**Setting and scale (v3 unless stated).**

*Architecture (§3.2).*
- Decoder-only MoE: RoPE, SwiGLU, RMSNorm, QK-Norm.
- Dropless MoE (MegaBlocks), softmax routing, built on the OLMo codebase.

*Table 2 configurations (unchanged v1 to v3):*

| Model | Active / total | Layers | Heads | Hidden | Intermediate | Experts | Top-k |
|---|---|---|---|---|---|---|---|
| 1B | 0.3B / 1.1B | 12 | 12 | 768 | 2048 | 16 | 2 |
| 2B | 0.8B / 2.1B | 16 | 24 | 1536 | 1280 | 16 | 2 |
| 7B | 1.6B / 7.3B | 16 | 16 | 2048 | 2048 | 32 | 4 |
| 9B, upcycled | 3.1B / 9.4B | 28 | 16 | 2048 | 6144 | 8 | 2 |

*Hardware (§4.1):*
- **7B:** N = 4 nodes, each 8×A800 over NVLink, joined by 13 Gbps Ethernet. Each node trains 8 experts, "approximately 2.5B trainable parameters per node".
- **2B:** N = 16 nodes, each one 48 GB L40S, joined by 17 Gbps Ethernet. Each node trains 1 expert, roughly 0.7B trainable parameters.
- **9B:** upcycled from Qwen3-1.7B-Base by replicating the FFN 8 times. Gaussian noise (std 0.02) is injected into 50% of parameters, and gate scores are normalized after top-k.

*Data (§4.1, App. C):*
- 2B and 7B: Ultra-FineWeb 64.2%, SlimPajama 27.2%, StarCoder 6.6%, arXiv 0.7%, OpenWebMath 0.4%, peS2o 0.5%, Algebraic Stack 0.4% (Table A2).
- 1B: SlimPajama only.
- 9B: Nemotron data.
- Each node's data is "randomly sampled from the whole dataset", i.e. IID. In the code each node gets its own data seed.

*Tokens (Table 3, v3 HTML):* SPES-2B 500B, SPES-7B 500B, SPES-9B 400B. The 1B controlled comparison uses 50B (v3) or 100B (v1 and v2); see the version notes.

*Hyperparameters (Table A1, identical in v1 and v3):*

| | 1B | 2B | 7B | 9B |
|---|---|---|---|---|
| Peak LR | 5e-4 | 5e-4 | 4e-4 | 1e-4 |
| Batch | 0.5M tokens × 4 | 0.5M × 16 | 2M × 4 | 0.5M × 4 |
| Sequence length | 2048 | 2048 | 2048 | 4096 |
| H | 50 | 100 | 100 | 100 |

- Shared by all sizes: minimum LR is 10% of peak, eps 1e-8, weight decay 0.1, betas (0.9, 0.95), 2,000 warm-up steps.
- App. B: for the 2B and 7B from-scratch runs, after 70% of tokens the per-node batch is halved and H is set to 50.

**What each node stores and trains (§3.3).**
- Experts are partitioned into N disjoint subsets, one owner per expert. Each node optimizes the shared parameters plus its assigned experts and keeps the rest fixed.
- Storage: "each node stores a full copy of the model" (§3.3). Gradients and optimizer states exist only for the updated parameters.
- Code: `scripts/train.py` sets `requires_grad=False` on the w1, v1 and w2 tensors of every non-owned expert. Owned experts form a contiguous block: indices `peer_id*n` to `peer_id*n + n - 1`, where n = `num_train_experts_per_node`, a single integer.

**Routing during local training: over all experts, unmasked.**
- Paper: sparse updates leave "many tokens assigned to frozen (unassigned) experts" (§3.3, Expert-Merging Warm-Up). Tokens are therefore routed to frozen local copies.
- Code: `CustomSparseGLU.forward` concatenates every expert's w1, v1 and w2, frozen ones included, and runs the standard MegaBlocks dropless top-k kernels. No mask exists in the code read. The router (`ffn.router.layer`) is never frozen, so it trains on every node.

**Aggregation (Eq. 4, App. A Eqs. 9 and 10).** Shared parameters are averaged with FedAvg; each expert is copied from its owner.

What the code does (`aggregate_step` in both server files):
- Keys containing `ffn.experts.mlp` are copied from peer `expert_idx // num_train_experts_per_node`.
- Every other key, router included, is a plain unweighted mean over all peers.
- So router rows are averaged over all N nodes, not over holders.
- `spes_server.py` declares "Nesterov Momentum Buffers" but never uses them. There is no outer optimizer: an outer SGD step with learning rate 1 is FedAvg, as §3.1 notes.

**Inner optimizer state (code only; the paper says nothing).**
- `spes_sync_if_needed` uploads weights, downloads the aggregate and loads it with `load_state_dict`. It never touches `self.optim`, so inner AdamW moments persist across rounds.
- The LR schedule (cosine with warm-up) runs on the global step and is continuous across rounds.
- (inference) This differs from our fresh AdamW every round.

**Losses.** Cross-entropy, z-loss and load-balancing loss (§3.3). v3 App. B gives the coefficients:
- cross-entropy 1;
- load-balancing 0.01;
- MoE router z-loss 0.001;
- standard z-loss 1e-5.

v1 and v2 do not list them. The released 1B configs carry the same values (`moe_loss_weight 0.01`, `moe_zloss_weight 0.001`, `auxiliary_loss_multiplier 1e-5`).

The code also contains an optional `using_decayed_aux_loss`: the trainable experts' load-balancing weight ramps from 0.7 to 1.0 over the first 20% of steps. It is off in the released configs and absent from the paper.

**Expert-merging warm-up (§3.3, Eqs. 5 and 6).**
- For each expert, compute cosine similarity of input-projection weights with every other expert and take the K most similar (excluding itself).
- Update it by task arithmetic with strength α, toward the mean difference to those K.
- Merging runs only in the first T_w steps, at interval T_i, with α decayed linearly to 0.
- Paper settings: T_w = 12,500, T_i = 300, α = 0.1, K = 4 (v3 §4.1). v1 and v2 named the warm-up length T_merge and said merging ran "every 500 steps"; T_i first appears in v3.
- Code differences:
  - Similarity is computed per layer on w1 only; the merge is applied to w1, v1 and w2.
  - Merging happens when `step % merge_interval == 0`, with α decayed linearly over `merge_decay_steps`.
  - Launcher defaults: interval 500, α_start 0.01, decay over 10,000 steps (`run_parameter_server.sh`). The 9B cluster script uses 4 peers, 2 experts per node, interval 500, α_start 0.05, decay over 20,000 steps.
  - None of these match the paper's α = 0.1, T_i = 300, T_w = 12,500.

**Theory (App. A, all versions).**
- Convergence bound for block-sparse local SGD.
- The shared block gets 1/N variance reduction. Expert blocks carry owner-only variance (σ_Φ², not divided by N).
- A heterogeneity term ζ², zero under IID data, and a local-drift term in γ²H²G².
- Merging enters as a vanishing perturbation.
- (inference) The paper's own bound says expert gradients get no cross-node noise averaging under owner-only updates. This is one theoretical reason a partial-update cost could exist.

**Quality against centralized training and DiLoCo (Table 1).**

Setting (v3): 1B MoE, SlimPajama, "same 1B-parameter MoE architecture and 50B training tokens" (Table 1 caption). The match is in tokens. The metric is zero-shot or few-shot accuracy on 8 benchmarks. No validation loss or perplexity is reported anywhere.

| Version | Arm | ARC-e | ARC-c | PIQA | SciQ | OBQA | BoolQ | SIQA | WinoG | Avg |
|---|---|---|---|---|---|---|---|---|---|---|
| v3 (50B tokens) | Centralized | 50.18 | 25.08 | 67.08 | 77.50 | 31.40 | 55.50 | 42.48 | 50.91 | **50.02** |
| v3 | DiLoCo | 46.84 | 25.08 | 67.03 | 76.90 | 30.00 | 60.09 | 42.22 | 50.12 | **49.79** |
| v3 | SPES | 52.11 | 26.42 | 66.27 | 76.50 | 31.80 | 60.95 | 42.73 | 50.83 | **50.95** |
| v1, v2 ("100B tokens", §4.2 text) | Centralized | 49.7 | 24.4 | 68.9 | 74.0 | 30.6 | 54.3 | 42.0 | 53.5 | **49.7** |
| v1, v2 | DiLoCo ("DiLiCo" in v1) | 51.7 | 26.6 | 68.4 | 77.4 | 29.6 | 55.7 | 43.4 | 51.1 | **50.5** |
| v1, v2 | SPES | 51.7 | 26.3 | 68.1 | 78.0 | 29.8 | 59.8 | 43.0 | 51.5 | **51.0** |

What the table shows:
- SPES's average exceeds centralized by +0.93 points (v3) or +1.3 points (v1).
- DiLoCo sits −0.23 points below centralized in v3 but +0.8 points above it in v1.
- The baseline definitions are thin. The paper never states DiLoCo's outer optimizer, H or node count.
- The released configs (all 50,000 steps, cosine schedule to 50,000) say:
  - centralized: global batch 1024 × 2048 tokens, about 105B tokens;
  - `dilico_fedavg_adamw...`: 4 nodes × 256 sequences × 2048, about 105B tokens, `sync_steps: 50`, no expert freezing;
  - SPES 1B: 4 peers, 4 experts each, `sync_steps: 100`, `global_train_batch_size: 1024` per node. As released that is about 419B tokens, and its H differs from Table A1's 50.
- Whether these configs produced Table 1 cannot be determined (see "Could not verify").
- No seeds, repeats or error bars are reported.
- (inference) ARC-c near 25 and WinoGrande near 50 are close to chance (4-way and 2-way tasks), so the 8-task average at 1B parameters and 50B tokens moves partly on noise. Most of SPES's v3 lead comes from BoolQ (+5.45 over centralized) and ARC-e (+1.93). SPES trails centralized on PIQA, SciQ and WinoGrande. These differences would not detect a 1 to 2% loss gap of the size we measure.

**Other main results (v3).**
- Fig. 4 (curves only): SPES "exhibits a slightly slower initial learning curve" (§4.2), then matches or beats both baselines.
- Throughput: centralized 3.79k tokens/s per GPU (FSDP over RDMA, 4×8 A800) against SPES with H = 50 at 3.67k (§4.2).
- Memory, 2B model on 16 nodes: DiLoCo needs 55 GB per node, SPES 35 GB. Communication falls 33.3% (§3.3).
- Upload, 7B model on 4 nodes: 9.8 GB per node per round against 28.6 GB, a 65% cut (§4.2).
- Table 3 compares SPES-2B, 7B and 9B with other published models trained on different data and token counts (for example SPES-7B, 500B tokens: SciQ/PIQA/SIQA 89.9/74.7/44.8, against MoE++ 7B at 1T tokens: 89.7/78.0/45.7). **This is not a centralized-baseline comparison** and does not isolate the method.

**Ablations.**

[REMEDY | expert-merging warm-up (top-K cosine task arithmetic) | partial-update cost (per-expert token utilization) | 1B MoE, 16 experts, H = 50; node count not stated in the paper (4 is my inference from Table A1's "0.5M × 4" and the released configs) | pretraining | 8-benchmark average 48.99 → 50.95 (+1.96 points) in v3; 50.5 → 51.3 in v1 and v2 | Table 4, §4.2, v3 and v1]

[REMEDY | ablation, not a remedy: merging hyperparameters α, K, T_w, T_i | same | 1B | pretraining | best at α = 0.1, K = 4, T_w = 12.5k, T_i = 300. Values are readable only from the figure; the text says larger values "interfere with expert specialization" | App. E, Fig. A1, v3]

[REMEDY | shorter synchronization interval, H ∈ {50, 100, 200, 400} | local-averaging drift | 1B, 100B tokens (v3 App. B) | pretraining | performance declines as H rises from 50 to 200 or 400, H = 50 best; values in figure only | App. E, Fig. A2, all versions]

[REMEDY | ablation, not a remedy: node count N ∈ {2, 4, 8} at fixed global batch | fragmentation of data and experts | 1B, 100B tokens | pretraining | average 50.6, 49.7, 49.5 | Table A5, all versions]

- Experts per node is never ablated separately. (inference) With 16 experts split disjointly it is tied to N: 8, 4 and 2 experts per node in Table A5.

**Differences between versions.**
- **v1 → v2:** spelling only ("DiLiCo" becomes "DiLoCo"). The phrase "via a parameter server" is dropped from the introduction, the Fig. 2 caption and §3.3; the v2 hardware paragraph in §4.1 still mentions a parameter server. No numbers change.
- **v2 → v3:**
  - Table 1: the stated budget falls from 100B to 50B tokens and every cell changes; (inference) so it reports a different run. DiLoCo moves from above centralized to below it; SPES stays above.
  - Table 4 changes: the without-merging row falls from 50.5 to 48.99, and the with-merging row (50.95) now equals Table 1's SPES row. In v1 the two differed (51.3 against 51.0).
  - T_i = 300 is introduced, replacing "every 500 steps"; T_merge is renamed T_w.
  - Appendix B is rewritten: the 1B budget is 50B except the H and N ablations at 100B, and the loss coefficients are added. v1 and v2 had instead mentioned a per-node batch of 1024 for comparison with "larger token budgets (400B)".
  - The parameter server disappears from the hardware text.
  - The abstract's motivation for the warm-up changes from accelerating convergence to "limited per-expert data utilization".
  - "consistently outperform most of their counterparts" becomes "achieve competitive results".
  - A T_i panel is added to Fig. A1.
- **Unchanged across versions:** Table 2, Table A1, Table A5, the H-ablation text and the theory.

**Which of our costs or questions it bears on.**
- Q4: it is our partial-update arm at scale.
- Q3, the partial-update cost of +1.4%: SPES reports no cost on a coarse benchmark metric.
- Q1, the local-averaging cost of +6.1%: DiLoCo is within about 1 point of centralized either way.
- Q5: the merging warm-up, z-loss, shorter H, and (from the code) persistent optimizer state.

**How its setup differs from ours.**
- Scale: 1.1B parameters and 50 to 100B BPE tokens, against our 46M and about 164M characters.
- 16 experts against 8.
- Disjoint ownership against our overlapping experts, each held by 2 of 4 workers.
- H = 50 against 125.
- Persistent inner AdamW state (code) against fresh AdamW each round.
- z-loss and merging warm-up, which we do not use.
- Downstream accuracy against bpc.
- Router rows averaged over all nodes: the same as our partial-update arm.

**Question it raises for us.** Does our partial-update arm's +1.4% shrink if inner AdamW state persists across rounds, as in SPES's code, or with H = 50?

**Classification on the four axes.**
1. Workers store only shared part plus own experts: **No** (full copy).
2. Routing masked to held experts: **No** (all experts, frozen copies included).
3. Holder-only averaging of experts: **No** (disjoint owners; experts copied, not averaged; router averaged over all).
4. Per-worker slice sizes: **No** (one integer for all nodes).

---

### 2. FoMoE: Breaking the Full-Replica Barrier with a Federation of MoEs

- **Authors:** Lorenzo Sani, Zeyu Cao, Meghdad Kurmanji, Alex Iacob, Andrej Jovanović, Yan Gao, Wanru Zhao, Nicholas D. Lane (Cambridge ML Systems Lab; Flower Labs). This is the Photon and DEPT group.
- **Year and venue:** 2026, preprint.
- **arXiv:** 2606.19025. v1 Wed 17 Jun 2026 12:50:07 UTC; v2 Sat 20 Jun 2026 12:18:17 UTC. **Read v2.**
- **Link:** https://arxiv.org/abs/2606.19025
- **Code:** no repository link found in the paper. The §5 Reproducibility paragraph says Sec. F records "artifact status", but App. F Table 7 has no such row.
- **Read status:** full text (v2 PDF). Tables 1 and 3 to 6 re-read from the v2 HTML because the PDF text interleaved rows.
- **How found:** WebSearch. It does **not** cite SPES or FlexOlmo (grep of the full text for "2602.11543", "SPES" and "FlexOlmo": no hits). It is therefore not a citer, but it is the closest method found.

**Setting.**
- Cross-datacenter (WAN) MoE pretraining with M homogeneous workers.
- "i.i.d. data partitions", K local steps per round, central coordinator, synchronous rounds (§3.1).
- Overlap factor O_e ∈ {1, …, M}: each expert is hosted by O_e workers, and each worker holds N_le = O_e·N_e/M experts. The same count for every worker (§3.3.1).
- Dense parameters (attention, norms, shared experts, embeddings) are fully replicated (§3.2).

**Routing.**
- "we partition each router, along with the experts" so tokens never go to unavailable experts (§3.3.3). Router rows travel with their experts, and the gate projects only to local experts (§4.1, App. D.3).
- An alternative "skip-token / ghost experts" mode keeps the full router, which is communicated as a dense part. Tokens routed to non-local experts skip that expert path.
- Sigmoid gating (App. B.3.2) is chosen so that a missing expert does not "skew the probability distribution" of the available ones.
- Fine-grained experts: expert hidden size 128 (App. B.3.1).
- A load-balancing loss is used (§4.1); its scope is not stated.

**Aggregation.**
- Dense parts: ring all-reduce over all workers.
- Sparse parts (experts and router rows): aggregated "within expert replica groups" (Alg. 2, §5 Implementation). This is holder-only averaging.
- Outer optimizer: server momentum. DiLoCo/Nesterov uses server learning rate 0.7 and momentum 0.9. Alternatively LocalAdamW, which also synchronizes both AdamW moments (App. F).
- "local optimizer states are preserved rather than reset" (§3.4); for experts each worker keeps state only for its own.
- On reassignment (random placement) optimizers are reinitialized with an LR warm-up on the moved weights. The authors report that "preserving local momentum prevents the divergence observed in stateless approaches" (§3.4). No numbers accompany that claim.

**Scale.**
- Trained quality runs use only the **Small Proxy, about 54M**: d_model 256, 4 layers, 4 heads, 8 experts of hidden 128, 2 active (Table 1, HTML).
- Tokenizer: gpt-oss, vocabulary 200,019. Sequence length 2048.
- Global batch 1024 sequences, local batch 1024/M. 640 optimizer batches, about 1.34B tokens at 20 tokens per parameter.
- Data: FineWeb-Edu-dedup 90%, Python-Edu 10%. Evaluated by C4-en validation perplexity.
- Sweep grid: M ∈ {2, 4, 8}, K ∈ {32, 64, 128}, seeds {42, 123, 456} (App. F).
- (inference) With d_model 256 and a tied 200,019-token vocabulary, about 51M of the 54M parameters are embeddings. The expert and attention part being partitioned is only a few million parameters.
- The 150M configuration is used only for a skip-token throughput measurement on 8 B200 GPUs. The 2B, 13B and 100B configurations are analytical projections, not training runs (§6.4, §7).

**Key findings with numbers.** Validation perplexity, mean ± std, v2 HTML. The std is described as "across the dataset" in §5 but "across runs with different seeds" in App. F, an internal inconsistency.

*Full replica (O_e = M), Table 4 (LocalAdamW) and Table 5 (DiLoCo):*

| M | LocalAdamW K=32 | K=64 | K=128 | DiLoCo K=32 | K=64 | K=128 |
|---|---|---|---|---|---|---|
| 2 | 105.03 | 104.70 | 106.91 | 118.01 | 117.94 | 507.21 |
| 4 | 103.91 | 104.47 | 111.89 | 137.27 | 124.17 | 420.49 |
| 8 | 106.30 | 112.99 | 159.71 | 145.64 | 133.37 | 647.11 |

DiLoCo with Nesterov diverges or degrades badly at K = 128. LocalAdamW does not.

*Partial replication, fixed placement, M = 4 (Table 6):*

| Outer optimizer | K | O_e = 1 | O_e = 2 | O_e = 4 (full replica) |
|---|---|---|---|---|
| LocalAdamW | 32 | 121.42 | 112.00 | 103.91 |
| LocalAdamW | 64 | 130.79 | 119.53 | 104.47 |
| LocalAdamW | 128 | 143.72 | 123.50 | 111.89 |
| DiLoCo | 32 | 142.94 | 130.58 | 137.27 |
| DiLoCo | 64 | 154.73 | 142.25 | 124.17 |

M = 8, K = 32, LocalAdamW, fixed placement: 135.74 / 122.49 / 114.69 / 106.91 for O_e = 1 / 2 / 4 / 8. This 106.91 disagrees with Table 4's 106.30 for the same cell; 106.91 is Table 4's M = 2, K = 128 value.

What the authors conclude:
- Lower O_e gives higher perplexity at an iso-token budget, because each site has "less active capacity" (§6.2).
- "O_e ≈ 4 yields the configurations that best balance quality" against communication and compute (§6.2, HTML).
- Fixed placement beats random placement in the IID sweep; random placement may help on non-IID data (§6.2).

My conversion to cross-entropy, ln(perplexity), so the gaps are comparable in kind to our bpc ratios. Arithmetic only (inference):
- M = 4, O_e = 2 against full replica, LocalAdamW: +1.6% (K = 32), +2.9% (K = 64), +2.1% (K = 128).
- O_e = 1 against full replica: +3.4% (K = 32), +4.8% (K = 64), +5.3% (K = 128).
- DiLoCo, O_e = 2: −1.0% (K = 32, where full replica is itself poor) and +2.8% (K = 64).

There is **no numeric centralized result.** "Centralized" appears only as a point in Fig. 5, a "quality reference" (§6.1). The cost against centralized training therefore cannot be extracted from the text; only the cost against full-replica local training can.

Other results:
- Skip-token: on the compute-quality frontier, skip-token mode adds configurations with lower perplexity at comparable FLOPs (Fig. 7, §6.3; figure only). The authors say it "does not significantly impact training convergence".
- Throughput up to 1.4× with skip-token.
- Communication cut up to 1.42× against efficient baselines and 45.44× against DDP (abstract, §8). These are modeled or controlled-regime figures.

[REMEDY | ablation, not a remedy: overlap factor O_e (holders per expert) | partial updates and masked routing combined, against full replica | 54M proxy, M = 4 and 8, K = 32 to 128 | pretraining | e.g. M = 4, K = 128, LocalAdamW: perplexity 143.72 / 123.50 / 111.89 for O_e = 1 / 2 / 4 | Table 6, v2]

[REMEDY | LocalAdamW outer step (synchronizes both moments) against DiLoCo/Nesterov | local-averaging cost | 54M, M = 2 to 8, K = 32 to 128 | pretraining | e.g. M = 4, K = 64: 104.47 against 124.17; DiLoCo diverges at K = 128 (420 to 647) | Tables 4 and 5, §6.1, v2]

[REMEDY | preserve local optimizer state across rounds (no reset) | local-averaging cost | proxy | pretraining | qualitative only: avoids "divergence observed in stateless approaches" | §3.4, v2]

[REMEDY | ablation, not a remedy: fixed against random expert placement | masked routing and specialization | 54M | pretraining | fixed better under IID, e.g. M = 4, K = 32, O_e = 2: 112.00 against 113.65 | Table 6, §6.2, v2]

[REMEDY | ablation, not a remedy: skip-token (unpartitioned router, ghost experts skipped) against partitioned router | masked-routing design | 54M | pretraining | frontier shift; figure only | §6.3, Fig. 7, v2]

**Which of our costs or questions it bears on.**
- Q4: the closest found to our sliced method.
- Q2: masked routing combined with partial updates.
- Q1: outer optimizer and persistent optimizer state against our plain averaging with fresh AdamW.
- Q5: overlap, placement and the outer optimizer.

**How its setup differs from ours.**
- Sigmoid gating with fine-grained experts (8 experts of hidden 128) against softmax top-2 with renormalized weights over 8 experts of hidden 768.
- A tiny non-embedding model inside a 54M embedding-heavy one against 46M character-level.
- BPE perplexity against bpc.
- Outer momentum or LocalAdamW with persistent state against plain averaging with fresh AdamW.
- The global batch is split across workers, so it is token-matched per round.
- No SPES-like arm. Full replica means every worker trains every expert, so FoMoE's O_e < M gap bundles storage, partial updates and masked routing together.
- (inference) Our nearest analogue is sliced against full averaging. In our additive steps that is +4.6 points (1.4 + 3.2; 10.8 − 6.1 = 4.7 before rounding), about +4.4% relative to the full-averaging bpc. FoMoE's matching cell (M = 4, O_e = 2, K ≈ 128, LocalAdamW) is about +2.1%, roughly half ours, with every difference above uncontrolled.

**Question it raises for us.** Does adding Nesterov outer momentum, which our harness has, and persistent inner AdamW state shrink our sliced-against-full gap toward FoMoE's 1.6 to 2.1%? And does our softmax top-2 renormalization over held experts add a cost that sigmoid gating avoids?

**Classification.**
1. Only shared part plus own experts: **Yes** (partial replica; expert memory scales with O_e/M).
2. Routing masked to held experts: **Yes**, in the main mode (router partitioned with the experts). The skip-token mode instead routes over all experts and skips the absent ones.
3. Holder-only averaging: **Yes** (aggregation within each expert's replica group of O_e workers; router rows follow their experts in the main mode).
4. Per-worker slice sizes: **No** (uniform N_le; homogeneous workers, App. D.1).

---

### 3. FlexMoRE: A Flexible Mixture of Rank-heterogeneous Experts for Efficient Federatedly-trained Large Language Models

- **Authors:** Annemette Brok Pirchert, Jacob Nielsen, Mogens Henrik From, Lukas Galke Poech, Peter Schneider-Kamp (University of Southern Denmark; Ordbogen A/S).
- **Year and venue:** 2026, preprint.
- **arXiv:** 2602.08818, v1 only (Mon 9 Feb 2026 15:54:29 UTC). https://arxiv.org/abs/2602.08818
- **Code:** "Code will be made available" (footnote 1); no link found.
- **Read status:** sections read: Abstract, §1 to §5 (Introduction, Related Work, Methods, Experimental Setup, Results), §6 opening; Tables 1 and 2. Appendices not read.
- **Citation status:** cites FlexOlmo (Shi et al., 2025) throughout. Predates SPES.

**Setting.**
- No new training. FlexOlmo's released 7B domain experts are compressed after the fact into low-rank (truncated-SVD) deltas over the public expert (§3.2).
- 150 mixtures (96 with 2 experts, 54 with 7) evaluated on 120 tasks (abstract).

**Findings.**
- Abstract: FlexMoRE averages 47.18 against FlexOlmo's 45.46, at 10.75B against 33.27B parameters. (inference) These values match Table 2's a4 rows (0.4718 against 0.4546).
- Single low-rank experts gain +0.73% to +7.13% relative to full-size for 5 of 6 experts; Math loses 1.34% (Table 1, §5.1).
- Reasoning-heavy benchmarks peak at higher ranks than knowledge-heavy ones (§5.3).

[REMEDY | ablation, not a remedy: per-expert low-rank compression after independent training | expert capacity and memory | 7B experts | post-training composition, no pretraining | +3.79% relative average at a4 (per Table 2, as read through the abstract's numbers) | abstract, Table 2]

**Bearing.** Q4 classification only. Weak relevance to per-worker capacity: expert size differs per expert, not per worker.

**Differences from ours.** No distributed training, no averaging, 7B fine-tuned experts.

**Question it raises.** Could heterogeneous capacity be expressed as smaller experts on weaker workers rather than fewer experts?

**Classification.**
1. FlexOlmo's training (each owner trains its expert against a frozen public model) resembles "shared plus own" storage, but FlexMoRE itself trains nothing: **N/A**.
2. **N/A.**
3. **No** (composition, no averaging).
4. **No** per-worker slices. It has per-expert rank heterogeneity instead.

---

### 4. IOTA: Incentivised Orchestrated Training Architecture, A Technical Primer for Release

- **Authors:** Felix Quinque, Alan Aboudib, Szymon Fonau, Rodrigo Lopez Portillo Alcocer, Brian McCrindle, Steffen Cruz (Macrocosmos AI).
- **Year and venue:** 2025, preprint (technical primer).
- **arXiv:** 2507.17766, v1 only (16 Jul 2025). https://arxiv.org/abs/2507.17766
- **Read status:** sections read: Abstract, §1, §2 (architecture: orchestrator, miners, validators). Not read: §3 to §7 (incentives, activation compression, butterfly all-reduce, CLASP, summary); headings only.
- **Model type:** dense. The words "mixture", "expert" and "MoE" never occur in the text (grep count 0).

**Setting.**
- Data-parallel plus pipeline-parallel, SWARM-style. The orchestrator assigns each miner one model layer (§2.2).
- Miners synchronize with peers holding the same layer, combining DiLoCo-style local steps with periodic full synchronization of weights and optimizer states (§2.1, §2.2).

**Findings.** No quality comparison in the sections read.

**Bearing.** Only as a non-MoE route to "no worker holds the whole model".

**How its setup differs from ours.** Dense pipeline parallelism with activations streamed between miners, against our MoE with local slices and no activation exchange.

**Question it raises.** None for our three costs. It is a reminder that layer-wise sharding is the main alternative route to "no full model per worker".

**Classification.**
1. Analogue only (a miner holds a layer, not shared part plus experts).
2. **N/A** (dense).
3. Averaging among miners holding the same layer (layer-level analogue of holder-only).
4. Not stated in the sections read.

---

### 5. Incentivizing Permissionless Distributed Learning of LLMs (Gauntlet)

- **Authors:** Joel Lidin, Amir Sarfi, Evangelos Pappas, Samuel Dare, Eugene Belilovsky, Jacob Steeves (Templar AI; Concordia University and Mila; Opentensor Foundation).
- **Year and venue:** 2025, preprint.
- **arXiv:** 2505.21684, v1 only (27 May 2025). https://arxiv.org/abs/2505.21684
- **Code:** "code can be found at tplr.ai" (not opened).
- **Read status:** sections read: Abstract, §1, §2, §6, §7. Not read: §3 to §5.
- **Model type:** dense. No mention of experts or MoE.

**Setting.**
- 1.2B dense model, about 20K communication rounds, FineWebEdu.
- DeMo-compressed pseudo-gradients from permissionless peers; the top 15 peers are aggregated per round (§6).

**Findings.** The training curve is compared against an AdamW DDP baseline with 15 peers at 400K tokens per round (Fig. 1). The downstream Table 1 was garbled in text extraction; its numbers are not recorded.

**How its setup differs from ours.** A dense model, compressed pseudo-gradients and permissionless peers, against our MoE slices with plain averaging.

**Question it raises.** None for our costs. It matters only for a later incentive or trust stage.

**Classification.** All four axes **No or N/A** (each peer holds and updates the full dense model).

---

### 6. Efficient Training of Large-Scale AI Models Through Federated Mixture-of-Experts: A System-Level Approach

- **Authors:** Xiaobing Chen, Boyang Zhang, Xiangwei Zhou, Mingxuan Sun, Shuai Zhang, Songyang Zhang, Geoffrey Ye Li.
- **Year and venue:** 2025, preprint (7-page magazine-style article).
- **arXiv:** 2507.05685, v1 only (8 Jul 2025). https://arxiv.org/abs/2507.05685
- **Read status:** sections read: §I to §III and the start of §IV.
- **How found:** WebSearch lead; not a citer of SPES or FlexOlmo.

**Setting.**
- A conceptual design. Clients train a capacity-limited subset of experts; "memory-limited clients cannot load large amounts of experts" (§III.A).
- A server assigns experts to clients using client-expert fitness scores, global expert-usage scores and capacity profiles (§III.B).

**Evidence.**
- Only a "conceptual comparison" on non-IID CIFAR-10 (Fig. 3): random assignment 18% accuracy in 83 rounds; greedy 43% in 38; load-balanced 59% in 33.
- No language model and no centralized baseline.

**Classification.**
1. **Implied yes.**
2. **Not specified.**
3. **Not specified** ("server aggregates").
4. **Yes, conceptually**: the number of experts per client is capacity-constrained.

**How its setup differs from ours.** A vision design sketch with non-IID data and dynamic server-side assignment, against our measured language-model pretraining with fixed coverage assignment.

**Question it raises.** Would load- and capacity-aware assignment matter for us once slice sizes vary per worker?

**Relevance.** Low. It is a design sketch, not a measurement.

---

### 7. EMO: Pretraining Mixture of Experts for Emergent Modularity

- **Authors:** Ryan Wang, Akshita Bhagia, Sewon Min (as listed by the arXiv API).
- **Year and venue:** 2026, preprint.
- **arXiv:** 2605.06663. v1 7 May 2026; v2 10 May 2026. **Read v2.** https://arxiv.org/abs/2605.06663
- **Read status:** sections read: §3 (method), §4 (setup), §5.1, §5.2, start of §5.3. Not read: appendices, rest of §5.3, §6 and §7.
- **How found:** FlexOlmo citer (Semantic Scholar citations endpoint).

**Setting.**
- **Centralized** pretraining: 1B active / 14B total, 128 experts (127 routed plus 1 shared), k = 8.
- 1T tokens of the OLMoE corpus plus a 50B annealing phase; ablations at 130B tokens (§4.1).

**Mechanism (§3.2).**
- Each document's tokens are restricted to a "document expert pool": the top-d experts by the router's average probability over the document.
- The mask is renormalized, and d is drawn uniformly from {k, …, n_r} per document.
- Global load balancing across data-parallel groups is required. Micro-batch balancing "directly opposing the shared-pool constraint", causing instability (§3.3).

**Findings.**
- As a full model EMO "matches the performance of a standard MoE" (§5.1, Table 1).
- Keeping 25% of experts costs about 1% and 12.5% about 3%, against standard MoEs' drops of "over 10%" at 25% (§5.2, Fig. 3).
- Experts specialize by domain, not by surface syntax (§5.3).

[REMEDY | global (cross data-parallel) load balancing instead of micro-batch | instability under restricted routing pools | 1B active / 14B MoE | pretraining, centralized | described as important for stable training; Fig. 7 not read | §3.3, v2]

**Bearing.** Q2, the masked-routing cost and interchangeable experts. Restricting routing to a subset during pretraining does not by itself produce generalists.

(inference) EMO's pool is chosen *from content* by the router. Our workers' masks are content-independent under IID data, so every held expert sees every content type. That pressure toward generalists is consistent with our Task A probe. Our Switch balance loss is computed per worker batch, which EMO identifies as conflicting with pool restrictions.

**Differences from ours.** Centralized training, 14B, 128 fine-grained experts, a data-dependent mask, no averaging.

**Question it raises.** Would content-correlated slices (skewed data per worker) or a balance loss computed globally or over held experts change our interchangeability result?

**Classification.**
1. **N/A** (centralized).
2. Analogue: routing masked to a per-document subset, chosen by the router rather than assigned.
3. **N/A.**
4. Pool size varies per document, an analogue of variable slice size.

---

## Citing papers

**SPES citers.**
- OpenAlex `cites:W7128813075`: 0 results; the SPES record shows `cited_by_count: 0`.
- Semantic Scholar `/paper/arXiv:2602.11543/citations`: HTTP 200 with an empty list.
- WebSearch: no citing paper found.
- **No SPES citer was found by any route.** OpenAlex and Semantic Scholar both lag on recent arXiv preprints, so this is weak evidence of absence.

**FlexOlmo citers.**
- OpenAlex resolves the DOI 10.48550/arXiv.2507.07024 to W4416105355, a proceedings record with DOI 10.52202/085713-5530. It has 1 citer.
- Semantic Scholar lists 16 citers (citationCount 16).
- An OpenAlex full-text `search=FlexOlmo` returned 25 works. Those not in the citation lists are marked "search hit" and were not confirmed as citers.

| Title | ID | Year | How screened | Four-axis classification (1 storage / 2 masked routing / 3 holder-only averaging / 4 per-worker slices) | Relevance |
|---|---|---|---|---|---|
| CORTEX: Learning to Share and Specialize in Dense Language Models | 2609.34449 | 2026 | abstract (S2 citer) | dense, centralized: N/A all | low |
| DistMoE: Private-data Rehearsal-free Routing in MoE for Distributed Instruction Tuning | 2608.09907 | 2026 | abstract (S2 citer) | clients train public plus own private FFN expert / not stated / no averaging (router-only composition stage) / no | low to medium (remedy: public-anchored router-only composition; fine-tuning an MLLM) |
| Toward Open Weight Models Without Risks | 2606.21638 | 2026 | abstract (S2 citer) | not MoE distributed: N/A | none |
| Scaling Participation in Modular AI Systems | 2606.07812 (v2 2026-10-05) | 2026 | abstract (S2 citer) | collaboration of separately trained models: N/A | low |
| EMO: Pretraining MoE for Emergent Modularity | 2605.06663 | 2026 | sections read (S2 citer) | centralized; per-document masked pools (see entry 7) | **medium (Q2)** |
| PubSwap: Federated RLVR | 2604.12160 | 2026 | abstract (S2 citer) | LoRA federated RL: N/A | none |
| Optimal Splitting of LMs from Mixtures to Specialized Domains | 2603.19149 | 2026 | abstract (S2 citer) | split continued pretraining, no averaging: N/A | low |
| A Human-Centric Framework for Data Attribution in LLMs | 2602.10995 | 2026 | title and abstract (S2 citer; FAccT per S2) | N/A | none |
| The Single-Multi Evolution Loop | 2602.05182 | 2026 | abstract (S2 citer) | N/A | none |
| BACo: Base-Aligned Model Collaboration | 2511.05650 | 2025 | abstract (S2 citer) | N/A | none |
| Position: Research in Collaborative Learning Does Not Serve Cross-Silo FL in Practice | 2510.12595 (SaTML 2026 per S2 and OpenAlex) | 2025 | abstract (S2 and OpenAlex citer) | interview study: N/A | none |
| Don't Throw Away Your Pretrained Model | 2510.09913 | 2025 | abstract (S2 citer) | N/A | none |
| Pretraining with hierarchical memories | 2510.02375 (ICLR 2026 per arXiv comment) | 2025 | abstract (S2 citer) | memory blocks fetched per context; centralized: N/A | low |
| Model Merging Scaling Laws in LLMs | 2509.24244 (ICML 2026 per arXiv comment) | 2025 | abstract (S2 citer) | merging fine-tuned experts: no / no / averaging-type merges of all / no | low (Q5, merging) |
| Exact Unlearning of Finetuning Data via Model Merging at Scale | 2504.04626 | 2025 | abstract (S2 citer) | N/A | none |
| Retrieval-Augmented Feature Generation | 2406.11177 | 2024 | abstract (S2 citer) | N/A | none |
| FlexMoRE | 2602.08818 | 2026 | sections read (search hit; FlexOlmo citation confirmed in text) | see entry 3 | low |
| MetaMoE: Diversity-Aware Proxy Selection for Privacy-Preserving MoE Unification | 2605.14289 (ICML 2026 per arXiv comment) | 2026 | abstract (search hit) | independently trained experts unified with public-proxy router learning; no averaging | low to medium (remedy: proxy-data router fit) |
| Train Separately, Merge Together (BAR) | 2604.18473 | 2026 | abstract (search hit) | independent domain experts plus lightweight router training; no averaging; 7B post-training | low to medium (remedy: router training after separate experts; abstract reports 49.1 against 47.8 and 50.5 for retraining baselines) |
| Prototype Language Models; Natively Unlearnable LLMs; A Sovereign Open-Source Foundation Model for German and English; Hubble; Tensor Seeks Layout; Open-Science AI; MSA; User Privacy and LLMs | 2607.00510; 2606.13873; 2607.09424; 2510.19811; 2608.21555; DOI 10.48448/6bdy-8733; no DOI; DOI 10.1609/aies.v8i2.36646 | 2025 to 2026 | title only (OpenAlex search hits; citation not confirmed) | not distributed MoE training, judging by title | none apparent |

**Earlier-survey leads and other candidates (not citers):**

| Title | ID | How screened | Four-axis classification | Relevance |
|---|---|---|---|---|
| FoMoE | 2606.19025 v2 | full text | **Yes / Yes / Yes / No** | **high: closest found** |
| IOTA | 2507.17766 | sections read | dense pipeline: layer-level analogues only | low |
| Gauntlet | 2505.21684 | sections read | dense: No on all | none for the axes |
| Federated MoE, system-level approach | 2507.05685 | sections read | implied yes / unspecified / unspecified / yes (conceptual) | low |

---

## Synthesis for question 4 (SPES and citers)

**What SPES actually is (primary-source correction of the earlier survey).**
- The earlier survey's SPES description is confirmed on every axis: full model stored, routing unmasked, disjoint ownership, plain averaging.
- Things the survey did not have:
  - Router rows are averaged over all nodes. The code confirms this, which is exactly our partial-update arm's router rule.
  - The released code keeps inner AdamW state across rounds.
  - The headline 1B comparison changed between versions.
- The survey's merging-ablation numbers (48.99 → 50.95) are v3's. v1 and v2 reported 50.5 → 51.3.

**What the literature says about cost against centralized training.**
- SPES reports none: SPES is above centralized by +0.93 points on an 8-task average (v3), with DiLoCo at −0.23 (1B, 50B tokens, token-matched, single runs).
- (inference) This metric is coarse and near chance on several tasks, so it cannot confirm or refute a gap of about 1.4% in loss, the size of our partial-update cost.
- SPES's own ablations show the direction of our concerns:
  - performance falls as H grows past 50 (Fig. A2);
  - it falls slightly as N grows from 2 to 8 (Table A5: 50.6 → 49.5);
  - without the merging warm-up SPES loses about 2 points and drops below centralized (48.99 against 50.02, v3).
- (inference) In SPES's own numbers, the "no cost" result depends on the warm-up.
- FoMoE is the only paper found that matches our storage, masking and holder-averaging choices. It reports a monotone cost of reducing overlap against full-replica local training, and gives no numeric centralized result. At our overlap (M = 4, each expert on 2 workers) and K ≈ 125, the cost is about 2% in cross-entropy, against our about 4.4% for sliced against full averaging. (inference) The gap is roughly half ours. Plausible contributors are its outer optimizer or LocalAdamW, persistent optimizer state, sigmoid gating and fine-grained experts. None was isolated.

**Where the papers disagree or diverge.**
1. SPES finds partial updates cost nothing, even a gain; FoMoE finds that reducing the expert copies per site always costs. The setups differ: SPES keeps full storage and routing, FoMoE masks. So they are not strictly contradictory.
2. Optimizer state: SPES (code) and FoMoE both keep inner optimizer state. FoMoE says resetting it leads to divergence. Our harness resets AdamW every round. (inference) This is an untested candidate contributor to our local-averaging cost and possibly to the others.
3. Outer optimizer: SPES uses plain averaging and does well at H = 50. FoMoE's DiLoCo/Nesterov diverges at K = 128 while LocalAdamW does not. Neither tests plain averaging at H = 125.

**What is unknown (not answered by any paper read).**
- How much of SPES's result survives H = 125, fresh optimizer state, or no warm-up, measured by loss.
- No paper measures expert specialization or interchangeability (random-routing or ablation tests) under masked routing in distributed training. FoMoE reports only routing entropy and stability, and SPES reports nothing on specialization. EMO, which is centralized, shows that content-correlated restricted pools *increase* specialization.

**Our exact combination.** Workers store only their slice, routing is masked to held experts, overlapping experts are averaged over holders, and slice sizes vary per worker.
- FoMoE matches the first three. **The full four-way combination was not found in this search.**
- No paper found combines per-worker slice sizes with the other three in language-model pretraining. 2507.05685 has capacity-varying expert counts only as a concept, on CIFAR-10.
- Search coverage:
  - OpenAlex `cites:` for SPES (0) and FlexOlmo (1).
  - OpenAlex full-text search "FlexOlmo" (25 hits) and SPES title and term searches.
  - Semantic Scholar citations endpoint for both (SPES 0, FlexOlmo 16). The Semantic Scholar keyword search failed with three 429s.
  - Eight WebSearch queries.
  - arXiv metadata for 23 IDs.
  - Full or partial reads of 7 papers.
- Not covered: Google Scholar's "cited by" (not reachable through WebSearch), GitHub code search, OpenReview, Chinese-language venues, and proceedings not indexed by OpenAlex.

---

## Candidates for the joint reading list

1. **SPES (2602.11543, read v3 and the version diff)**. *Foundational, read early.* It is our partial-update arm at 1 to 9B. Read it together with these notes' code findings: router averaged over all nodes, persistent AdamW, configs that do not match the paper, and Table 1 changing between versions.
2. **FoMoE (2606.19025 v2)**. *Foundational for the sliced method, read early.* It is the only work found matching storage, masked routing and holder-only averaging. Its Table 6 gives an overlap-against-quality curve directly comparable to our sliced arm.
3. **EMO (2605.06663 v2)**. *Specific, read later.* Restricted routing pools in pretraining, the need for global load balancing, and specialization. It bears directly on the masked-routing cost and the interchangeable-experts finding.
4. *(Optional)* **BAR / Train Separately, Merge Together (2604.18473)** or **MetaMoE (2605.14289)**. *Specific, read later, abstract-only so far.* Both are router-fit-after-independent-experts remedies in the FlexOlmo line. Include one only if the FlexOlmo reader's strand does not already cover this remedy.

---

## Gaps

Questions no paper answers that the existing harness could answer. The harness supports other H, Nesterov outer momentum, slice sizes, worker counts, assignment policies, partial/full/sliced modes, skewed data and worker dropout.

1. **Overlap sweep at N = 4.** Each expert held by 1, 2 or 4 workers, i.e. slice sizes 2, 4 and 8 of 8, for the sliced arm, measured in bpc against centralized. This is the direct analogue of FoMoE Table 6 at our scale and metric, with a centralized anchor FoMoE lacks.
2. **H sweep (for example 50, 125, 250) in all three arms.** It tests whether SPES's H = 50 explains its near-zero partial-update cost, and how our three costs depend on H.
3. **Nesterov outer momentum against plain averaging** in the full, partial and sliced arms at H = 125. FoMoE suggests the outer step matters a lot at K ≈ 128; SPES uses plain averaging.
4. **Disjoint against overlapping assignment in the partial-update arm.** This is SPES's exact assignment and quantifies what overlap buys.
5. **Worker count 2, 4 and 8 at a fixed global batch for the sliced arm.** The analogue of SPES Table A5, measured in bpc.
6. **Skewed (content-correlated) data with masked routing.** EMO's finding implies content-correlated masks could restore specialization (inference). The harness's skewed-data mode can test it with the interchangeability probes from Task A.
7. **Heterogeneous per-worker slice sizes** (for example 2, 4, 4 and 6 of 8). No paper measured this in LM pretraining.

Not supported by the harness as described, but suggested by these papers:
- persistent inner AdamW state across rounds (SPES code, FoMoE);
- LocalAdamW moment averaging (FoMoE);
- the expert-merging warm-up (SPES);
- z-loss (SPES);
- sigmoid gating (FoMoE);
- a global or held-experts-only balance loss (EMO).

---

## Could not verify

- **How SPES's DiLoCo baseline aggregated experts.** `scripts/train.py` only skips freezing when `using_dilico` is set. Both released server files always copy expert tensors from one peer (`expert_idx // num_train_experts_per_node`) and have no averaging path for experts. The server arguments used for the DiLoCo run are not in the repo. Tried: reading both server files, the launcher scripts and the DiLoCo node config.
- **Which runs produced SPES Table 1.**
  - v3 says 50B tokens, while the released 1B configs imply about 105B (centralized, DiLoCo) and about 419B (SPES as released, with `sync_steps: 100` against Table A1's H = 50).
  - Table A1's 0.5M × 4 tokens per step over the configs' 50,000 steps gives about 105B tokens, matching v1's "100B".
  - The last code push (2026-05-08) predates v3 (2026-06-15).
- **SPES Fig. A1 and Fig. A2 values.** Figures only; only the stated directions are recorded.
- **FoMoE's centralized perplexity.** Fig. 5 only. Also no code link, and the internal inconsistencies noted in entry 2: Table 6's M = 8, K = 32, O_e = 8 cell against Table 4, and the definition of the std.
- **FoMoE's load-balancing loss scope and coefficient.** Not stated in the text read.
- **Semantic Scholar keyword search for SPES mentions, and the SPES citation count via Semantic Scholar.** HTTP 429 three times (10:45:48, 10:46:36, 10:47:07) despite 30 s backoff. The earlier citations-endpoint call (10:37:48) did succeed and returned zero citers.
- **Whether the OpenAlex search hits cite FlexOlmo** (Prototype LMs, Natively Unlearnable LLMs, the German/English model, Hubble, Tensor Seeks Layout, Open-Science AI, MSA, User Privacy). Not opened.
- **Gauntlet Table 1 values.** The table was garbled in text extraction and was not re-read in HTML.
- **IOTA quality results.** Sections not read.
- **FlexMoRE and MetaMoE code; DistMoE code** (DistMoE's abstract names github.com/mainaksingha01/DistMoE). Not opened.
- **BAR's numbers (49.1, 47.8, 50.5).** Taken from the arXiv abstract text only; the paper was not opened.

---

## Query log

All times are local machine time ("TST") on 2026-10-11, from the `date` command. WebSearch calls are not individually timestamped; each is bracketed by the nearest `date` outputs.

| Time | Database / API / site | Query or request | Result |
|---|---|---|---|
| 10:28:46 | local | `date`; listed docs/research | n/a |
| 10:28:59 | export.arxiv.org API | `id_list=2602.11543` | v3 metadata, 5 authors |
| ~10:29 | arxiv.org abs | /abs/2602.11543 | v1 12 Feb, v2 4 May, v3 15 Jun 2026 |
| ~10:29 to 10:30 | arxiv.org PDF | /pdf/2602.11543v1, v2, v3 (sleep 3 between) | 19 pages each |
| ~10:30 to 10:31 | arxiv.org HTML | /html/2602.11543v1, v2, v3 | used for tables and diffs |
| 10:34:18 | api.github.com | /repos/zjr2000/SPES; /git/trees/HEAD?recursive=1 | Apache-2.0; file tree |
| ~10:34 to 10:36 | raw.githubusercontent.com | 18 files from zjr2000/SPES main (servers, train, model, config, configs, scripts) | read, not run |
| 10:36:49 | api.openalex.org | /works/W7128813075; `filter=cites:W7128813075&per-page=200` | count 0 |
| 10:37:04 | api.openalex.org | `filter=doi:10.48550/arXiv.2507.07024`; title search | W4416105355 |
| 10:37:25 | api.openalex.org | `filter=cites:W4416105355&per-page=200` | count 1 (2510.12595, SaTML version) |
| ~10:37 | api.openalex.org | `search=FlexOlmo&per-page=50` | 25 works |
| 10:37:48 | api.semanticscholar.org | /paper/arXiv:2602.11543/citations; /paper/arXiv:2507.07024/citations | SPES 0; FlexOlmo 16 |
| 10:37:48 to 10:41:40 | WebSearch (standard) | `"SPES" sparse expert synchronization decentralized MoE pretraining` | SPES pages only |
| same window | WebSearch (standard) | `"2602.11543" mixture of experts decentralized` | nothing relevant |
| same window | WebSearch (extended) | `decentralized MoE training each node holds subset of experts masked routing 2026 arXiv` | lead 2507.05685 |
| same window | WebSearch (standard) | `"Zhang et al., 2026" SPES decentralized expert training memory` | SPES pages only |
| same window | WebSearch (extended) | `federated pretraining mixture-of-experts clients hold only their experts router aggregated holders 2026` | FedWeave, ClientMorpher (not pursued: MoE-LoRA fine-tuning) |
| same window | WebSearch (standard) | `expert-sharded local SGD MoE language model workers train disjoint experts low communication` | **lead: FoMoE 2606.19025** |
| 10:41:40 | export.arxiv.org API | `id_list` of 16 candidate IDs | all exist; versions recorded |
| ~10:42 | arxiv.org | abs, PDF and HTML of 2606.19025v2 | read in full |
| 10:43:48 | arxiv.org PDF | 2602.08818, 2507.17766, 2505.21684, 2507.05685 (sleep 3 between) | read sections as listed |
| 10:45:08 | export.arxiv.org API | `id_list` of 7 more FlexOlmo citers | abstracts screened |
| ~10:45 | arxiv.org PDF | 2605.06663v2 | sections read as listed |
| 10:45:48 | api.semanticscholar.org | /paper/search `sparse expert synchronization decentralized mixture-of-experts`; paper counts | HTTP 429 |
| 10:45:5x | api.openalex.org | `search="memory-efficient decentralized paradigm"`; `search="sparse expert synchronization"` | SPES itself only, cited_by 0 |
| 10:46:36, 10:47:07 | api.semanticscholar.org | the same search, retried after 30 s waits | 429, 429; FlexOlmo citationCount 16 |
| ~10:47 | arxiv.org HTML | (cached) checks of FoMoE and SPES tables | n/a |
| 10:47:27+ | WebSearch (standard) | `"A Memory-Efficient Decentralized Paradigm" cited` | no citers |
| 10:47:27+ | WebSearch (extended) | `partial expert replication federated MoE pretraining holders average router masked 2026 FoMoE SPES comparison` | no new candidates |

**Not covered in this strand:**
- Google Scholar's "cited by" pages (WebSearch cannot reach them).
- GitHub code search (the GitHub MCP connector failed to connect).
- OpenReview and conference proceedings not in OpenAlex; Chinese-language venues.
- The Semantic Scholar keyword search (rate-limited).
- Full reads of DistMoE, BAR, MetaMoE, CORTEX and the other FlexOlmo citers beyond their abstracts.
- The SPES Hugging Face model cards.
- Appendices of FlexMoRE and EMO; IOTA §3 to §7; Gauntlet §3 to §5.
- FlexOlmo itself and the other named closest methods (MoE-DisCo, BTX, BTM, DiPaCo, SMALLTALK LM, DEPT, Learning@home), which other researchers cover by assignment.
