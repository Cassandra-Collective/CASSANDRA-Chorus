# W1d: storage on public hosts, code trust, and update sizes · system-study notes

Strand W1d of `docs/research/2026-10-13-system-study-brief.md`: questions 5 (checkpoints and public-host limits), 8 (code trust) and 10 (bandwidth and compression). Written 2026-10-13. Status: complete for this strand (finished 2026-10-13 17:50 TST); open items are under "Could not verify" and "Gaps".

How these notes were made. Papers: PDFs fetched from arxiv.org with `curl` and converted with `pdftotext -layout`, one new directory per source under the session scratchpad (`sysstudy/sources/w1d/`). Documentation: the raw page or its source file on GitHub fetched with `curl`, tags stripped with a script kept outside the source folders. GitHub data via `gh api` (read-only). Search tools were used only to discover sources; no number below comes from a search snippet or a summarizing fetch.

Classification used throughout (from the brief): **(a)** a server we would run; **(b)** a public host for static files; **(c)** a public third-party network used for live coordination or discovery.

## Sources

Blocks are grouped by question: P (papers on update sizes and compression, question 10), H (public hosts and storage, question 5), S (systems' storage side, question 5), T (code trust, question 8). A source that bears on two questions appears once, in its main group.

Setting warning for every P block: none of these papers measured home connections. Every experiment ran in data centres or between rented cloud machines (the links are stated per block). Any statement below about home connections is labelled (inference).

### P1. DeMo: Decoupled Momentum Optimization

- **Authors:** Peng, Chen, Su, Quesnelle, Kingma, Liu (Nous Research; University of Texas at Austin). Preprint.
- **arXiv:** 2411.19870. Versions: v1 29 Nov 2024, v2 6 Feb 2026 (arXiv API, queried 2026-10-13 17:21). **Read v2** (PDF; Table 1 also from arXiv HTML v2, fetched 2026-10-13 17:22, because the PDF table text was scrambled).
- **Code:** github.com/bloc97/DeMo (no licence per the GitHub API, recorded in `01-local-averaging.md` D3; not re-queried).
- **Read status:** sections read: abstract, §1, §2.1 (algorithm and compression), §3.1 to §3.5, §5 (limitations). Not read: §2.2 and the appendix convergence analysis.
- **What it shows:** DeMo is not local averaging. Every step, each worker sends a compressed version of its local momentum: the momentum tensor is cut into chunks (64 × 64 for matrices), each chunk is transformed by a DCT, and only the top-k coefficients per chunk are sent. What was sent is subtracted from the local momentum, which acts as error feedback (§2.1). Upload is reduced "by a factor of roughly 4096/k" (§3.2).
- **Numbers (Table 1, v2 HTML; OLMo models trained on 100B tokens of Dolma; 64 H100 GPUs, global batch 2048 × 2048 tokens; per-GPU transmitted MB per step):**

  | Optimizer | 300M: HellaSwag / ARC-Easy / PIQA | 300M MB/step | 1B: HellaSwag / ARC-Easy / PIQA | 1B MB/step |
  |---|---|---|---|---|
  | DeMo k = 32 | 0.37 / 0.46 / 0.67 | 29.9 | 0.48 / 0.55 / 0.70 | 110.32 |
  | DeMo k = 16 | 0.38 / 0.50 / 0.67 | 14.9 | 0.47 / 0.53 / 0.70 | 55.16 |
  | DeMo k = 8 | 0.38 / 0.47 / 0.67 | 7.49 | 0.47 / 0.52 / 0.69 | 27.58 |
  | DeMo k = 4 | 0.37 / 0.47 / 0.67 | 3.74 | 0.45 / 0.52 / 0.70 | 13.79 |
  | DeMo k = 2 | 0.36 / 0.46 / 0.65 | 1.87 | 0.44 / 0.51 / 0.69 | 6.89 |
  | DeMo k = 1 | 0.35 / 0.45 / 0.65 | 0.93 | 0.41 / 0.52 / 0.69 | 3.44 |
  | AdamW-DDP | 0.35 / 0.46 / 0.65 | 636.9 | 0.43 / 0.51 / 0.68 | 2416.6 |

  - "300M" has 320M non-embedding parameters, "1B" has 1.18B (§3.1).
  - §3.3: at 300M, k = 8 "cuts data transfer by 85 times (7.5 MB vs. 637 MB)"; at 1B, k = 16 transmits "only 55 MB per step".
  - §3.5: with tuned baselines on a 300M model at 20 tokens per parameter, "DeMo underperforms AdamW at equal update counts" (Fig. 5, figure only). Against DiLoCo at comparable compression, DeMo "consistently yields lower perplexity" (Fig. 6, figure only, 8 workers).
- **Quality effect:** downstream accuracies equal to or above AdamW-DDP in Table 1 at 100B tokens; worse than tuned AdamW at equal updates in the shorter-budget comparison (§3.5). No loss numbers in the text.
- **Limitation stated by the authors (§5):** analysis covers upload; "the download bandwidth scales with the number of workers". Designed for "a small number of geographically distributed compute centers".
- **Central elements:** none stated for DeMo itself (an optimizer). The experiments used one H100 cluster.
- **Fit with R1 to R7:** an optimizer, not a system; communicates every step, so it needs a live all-gather each step, which is a poor match for R4's asynchronous or group averaging (inference).
- **Question for us:** DeMo sends a few MB per step but every step. At a home GPU's step time, is per-step exchange ever cheaper in wall-clock terms than DiLoCo-style exchange every H steps?

### P2. A Preliminary Report on DisTrO

- **Authors:** Peng, Quesnelle, Rolnick, Lotter, Adil, La Rocca (Nous Research). Technical report PDF in a GitHub repository, not on arXiv; dated 26 Aug 2024 by the repository README.
- **Link:** github.com/NousResearch/DisTrO, file `A_Preliminary_Report_on_DisTrO.pdf`, fetched raw at commit `24f10628c2` (2025-10-14) on 2026-10-13 17:27. Repository: licence `null`, `pushed_at` 2025-10-14T15:37:16Z (GitHub API, 2026-10-13 17:26).
- **Read status:** full text (5 pages; Table 1 and Table 2 layout garbled, not used).
- **What it shows:** the README calls DeMo the "original seed research/idea for DisTrO", and links Psyche's production code (`shared/modeling/src/distro.rs`). The report itself does not describe the algorithm.
  - Setting: 1.2B Llama-2-style model, 105B tokens of Dolma, 32 H100 GPUs in DDP, batch 4M tokens (§2, Table 1).
  - Table 3 (row layout garbled; mapped using the "857x" stated in §3): All-Reduce + AdamW: 17.1 h, 74.4 GB received per step, final loss 2.449. DisTrO + AdamW: 19.8 h, 86.8 MB received per step (857× less), final loss 2.373.
  - §3.1: each node sends 2.8 MB per step; "2.8MB×31 = 86.8MB" received in a naive 32-node peer-to-peer exchange. With aggregation servers, a node would upload 2.8 MB and receive 86.8 MB. At an assumed 100 Mbps down and 10 Mbps up the report computes 6.94 s down and 2.24 s up per step. It also says "we currently do not use any compression".
  - §3.2 and footnote 7: "the 1.2B model seems to be the smallest size" with which DisTrO works consistently; 50M and 300M models "do not converge as well".
  - The abstract claims "four to five orders of magnitude"; the README says "three to four"; §3 says 857× measured and "up to 1000x to 3000x" in preliminary tests. These are not consistent with each other.
- **Central elements:** none in the experiment (one cluster). The §3.1 "dedicated servers for data aggregation" would be (a).
- **Fit with R1 to R7:** the report's own size limit (works consistently from 1.2B; 300M "do not converge as well") is directly relevant to a 100M to 300M pilot.
- **Question for us:** does the later DeMo v2 paper (P1), which reports results at 300M, supersede the report's statement that 300M models do not converge well with DisTrO?

### P3. SparseLoCo: Overcoming the Communication-Performance Tradeoff in LLM Pretraining

- **Authors:** Sarfi, Thérien, Lidin, Belilovsky (Covenant AI, Université de Montréal, Mila, Concordia). Preprint.
- **arXiv:** 2508.15706. Versions: v1 21 Aug 2025, v2 5 Nov 2025, v3 23 Jul 2026. **Read v3** (PDF; Tables 1 and 7 confirmed in arXiv HTML v3, fetched 2026-10-13 17:23).
- **Read status:** sections read: abstract, §3 (chunked top-k), §4 setup, §4.1 to §4.4 (Tables 1 to 7), Appendix A (deployment), B (MoE), C (wall clock), D (utilization), I (index compression). Not read: theory appendices, Appendix Q in full.
- **What it shows:** DiLoCo with the outer momentum replaced by a local error-feedback buffer; pseudo-gradients are sparsified with chunk-wise top-k (64 × 64 blocks) and the kept values quantized to 2 bits using INTELLECT-1's statistical scheme (mean-centred, range ±6σ, four bins, each bin's centroid in a lookup table) (§4).
- **Numbers:**
  - **Table 1** (512M, R = 8 workers, H = 15, 10B tokens):

    | Method | Density | Loss | Pseudo-gradient size | Syncs | Quantization |
    |---|---|---|---|---|---|
    | AdamW DDP | 100% | 2.69 | 1.02 GB | 2445 | 16-bit |
    | DiLoCo (H = 15) | 100% | 2.76 | 512.40 MB | 163 | 8-bit |
    | DeMo | 0.78% | 2.83 | 10.01 MB | 2445 | 8-bit |
    | DeMo | 3.12% | 2.86 | 40.03 MB | 2445 | 8-bit |
    | SparseLoCo (H = 15) | 0.78% | 2.79 | 5.45 MB | 163 | 2-bit |
    | SparseLoCo (H = 15) | 3.12% | 2.70 | 17.21 MB | 163 | 2-bit |

  - **Table 7, quantization ablation** (bits 1 / 2 / 3 / 4 / 32): loss 4.79 / 2.70 / 2.70 / 2.70 / 2.70. Top-k against random-k at the same density: 1.56% 2.74 vs 3.05; 3.12% 2.70 vs 2.98; 6.25% 2.71 vs 2.93.
  - **Table 2:** DiLoCo 2.760; DiLoCo without outer momentum 2.868.
  - **Table 4** (2B, R = 16, H = 50): loss AdamW DDP 2.34, DiLoCo 2.37, SparseLoCo 2.36 (6.25% density per the text).
  - **Table 6** (MoE, 645M total, 273M active): AdamW 2.739; SparseLoCo 3.12% 2.741; 1.56% 2.776; DiLoCo 2.803.
  - **Appendix I:** index cost with 4096-entry chunks is about 12 bits per value naively; a Rice-coding scheme achieves 8.9, 6.6 and 5.6 bits per value for k = 32, 128 and 256.
  - **Appendix C:** under a 300 Mbps cross-replica limit (512M, R = 8, 8 × H100), SparseLoCo reaches DiLoCo's final loss "about two hours earlier" (Fig. 5); compression overhead "only 0.03% extra compute per outer step".
  - **Appendix A (deployment):** an 8B model's communication took "on average 12 seconds" per round with the test node never above 500 Mb/s; a 70B test with R = 20 took 70 s on average, at most 500 Mb/s down and 110 Mb/s up.
- **Quality effect:** at 3.12% density with 2 bits, loss equal to AdamW DDP and below dense 8-bit DiLoCo (Table 1). Quantization to 2 bits costs nothing measurable in Table 7; 1 bit fails.
- **Storage side (Appendix A):** pseudo-gradients went through Cloudflare R2; "Each peer maintained their own storage bucket", posting read credentials to a blockchain. See S1.
- **Central elements:** R2 buckets (b, but paid object storage owned by each peer; see H6); Bittensor blockchain (c).
- **Fit with R1 to R7:** the algorithm fits R4 only as synchronous rounds as tested; the deployment depends on (c).
- **Question for us:** SparseLoCo's best density rises with H (§4.4). Would its advantage over 8-bit dense DiLoCo hold at our H and at 100M to 300M, where the paper's smallest model is 178M (Appendix J, not read)?

### P4. Covenant-72B: Pre-Training a 72B LLM with Trustless Peers Over-the-Internet

- **Authors:** Lidin, Sarfi, Miahi, Anthony, Chauhan, Pappas, Thérien, Belilovsky, Dare (Covenant AI, Mila). Preprint (technical report).
- **arXiv:** 2603.08163. Versions: v1 9 Mar 2026, v2 10 Mar 2026 ("minor update, no content changes"). Title confirmed through the arXiv API before use. **Read v2.**
- **Read status:** sections read: abstract, §1, §2.2 (Gauntlet), §3 (communication and systems), §4.1, §4.3, §4.4, Appendix A.
- **What it shows:**
  - Each peer is a SparseLoCo replica with at least 8 × B200 GPUs (§3). H = 30, chunk 4096, top-k = 64, 2-bit values: "a compression ratio of more than 146×" against dense communication (§4.1).
  - With R = 20 peers and a 20-minute compute window, under at most 500 Mb/s down and 110 Mb/s up per node, communication averaged 70 s per round, 94.5% compute utilization (§4.3).
  - Mean 16.9 contributing peers per round (cap 20), mean 24.4 active peers, at least 70 unique peers over the run (§4.4, Appendix A).
- **Storage side (§3):** "we utilize object storage (specifically Cloudflare R2) as the communication backbone". Peers upload pseudo-gradients to their own R2 bucket and share credentials; a validator selects the top-scoring ones and every peer downloads them from those buckets. Data shards are pre-tokenized and hosted on object storage; peers download them ahead of time (§4.1). Checkpoints are released on Hugging Face (§1, §4.2). The paper does not say how a joining peer obtains the current model.
- **Central elements:** Bittensor blockchain, Subnet 3 (c); per-peer R2 buckets (b, paid); the validator (a role run by a participant; its operator is not stated in the sections read); Hugging Face for released checkpoints (b).
- **Fit with R1 to R7:** permissionless, ledger-based; R3 is met in the sense that no peer-to-peer connection is needed at all (all exchange is through object storage) (inference).
- **Question for us:** exchange through per-peer object storage avoids NAT traversal entirely. Is there a free host that allows the same pattern at our size (H5 to H7)?

### P5. Streaming DiLoCo with overlapping communication

- **Authors:** Douillard, Donchev, Rush, Kale, Charles, Garrett, Teston, Lacey et al. (Google DeepMind). Preprint.
- **arXiv:** 2501.18512. v1 30 Jan 2025 only. **Read v1.** (Quality findings already in `01-local-averaging.md` A3; this block covers communication only.)
- **Read status:** sections read: §2.4 (quantization), §3.1 (simulation, Fig. 4 caption), §3.2 Table 1, §3.3.3 (quantization ablation), Supplement Table 4.
- **What it shows:**
  - Outer gradients are sent as 4-bit floats (E3M0: 1 sign, 3 exponent, 0 mantissa bits); accumulation is done in FP32. The authors found "no sign of performance regression" from such low precision in communication, "even at the billion scale" (§2.4).
  - §3.3.3 and Fig. 11 (figure only): lowering precision "from float32 to float4 does not affect the performance"; zeroing values (FedDropout, DARE, top-k) "is significantly worse".
  - **Table 1** (1B model, Dolma, H = 100): over 25B / 100B / 250B tokens, data-parallel exchanged 441 / 1,767 / 4,418 TB with eval loss 2.67 / 2.52 / 2.45; Streaming DiLoCo with overlapped FP4 exchanged 1.10 / 4.42 / 11.05 TB with eval loss 2.66 / 2.51 / 2.45. The caption: "400× fewer bits", peak bandwidth reduced 8×.
  - **Table 4** (simulation; 1B model, step time 0.1 s, H = 100, fragments of 3 layers): Gbit/s needed for 50% / 80% / 90% / 95% / 99% compute utilization: data-parallel 86.8 / 152.6 / 184.2 / 222.3 / 569.0; vanilla DiLoCo 1.4 / 6.2 / 13.3 / 23.3 / 86.8; Streaming DiLoCo with overlapped FP4 0.4 / 0.9 / 1.7 / 2.0 / 3.0.
- **Central elements:** none in the method; the paper's runs are TPU data-centre runs.
- **Fit:** the 0.1 s step time assumes data-centre compute; a home GPU's step is far longer, which lowers the bandwidth needed for a given utilization (inference; the paper's §3.1 text says longer step time improves utilization at fixed bandwidth).
- **Question for us:** FP4 outer gradients cost nothing at 35M to 4B in this paper. Is that robust when M is small and updates are averaged with plain averaging, as in Stage 0?

### P6. MuLoCo: Muon is a practical inner optimizer for DiLoCo

- **Authors:** Thérien, Huang, Defazio, Rish, Belilovsky (FAIR at Meta, Mila, Université de Montréal, Concordia). Preprint.
- **arXiv:** 2505.23725. Versions: v1 29 May 2025, v2 25 Feb 2026, v3 2 Jun 2026. **Read v3.** (`01-local-averaging.md` B3 read §5 to §6.2; this block adds §6.3 and §6.4.)
- **Read status:** sections read: abstract, §2 (compression background), §5 setup, §6.3, §6.4.
- **What it shows (416M Gemma3-style model, K = 8 workers, H = 30, global batch 1M tokens):**
  - "Finding 3: Both MuLoCo and DiLoCo achieve lossless 4-bit quantization" (Fig. 7, figure only).
  - At 2 bits, linear quantization degrades substantially; statistical quantization does not (§6.3). Error feedback helps little except for 2-bit linear.
  - Top-k (0.5% to 50% kept): error feedback helps, but "does not make extreme sparsities viable" (Fig. 8a caption); index overhead makes 5% to 10% sparsity "less appealing than using 2-bit quantization" (§6.3).
  - Streaming in three partitions every 10 steps reaches the same final loss as non-streaming (Finding 4, Fig. 8b).
  - Quantized all-reduce is done as all-to-all reduce-scatter plus all-gather, to avoid compounding quantization error in a ring (§2, §6.3).
- **Numbers:** none in the text for these findings; all are figures. No numeric quality effect can be recorded.
- **Central elements:** none (simulation on a cluster).
- **Question for us:** do the 4-bit results at 416M carry to the 100M to 300M range with M = 3 to 5?

### P7. OpenDiLoCo (communication sections)

- **Authors:** Jaghouar, Ong, Hagemann (Prime Intellect). Preprint.
- **arXiv:** 2407.07852. v1 10 Jul 2024 only. **Read v1.** (Quality numbers in `01-local-averaging.md` A4.)
- **Read status:** sections read: §2 (implementations), §3 "All-Reduce in FP16" and "Globally Distributed Training Setting", Table 2, Fig. 6 and Fig. 8 captions.
- **What it shows:**
  - Main experiments all-reduce pseudo-gradients in FP32; the FP16 repeat showed "no noticeable impact on performance" with 8 workers / 500 local steps and 4 workers / 50 local steps (150M), and "can halve the communication time" (§3, Fig. 6, figure only).
  - Global run: 1.1B model, 4 workers each with 8 × H100 in Canada, Finland and two US states; measured worker-to-worker bandwidth 127 to 935 Mbit/s (Fig. 8, iperf); 500 local steps, about 67.5 minutes of independent compute; average all-reduce 300 seconds; the all-reduce "only accounts for 6.9% of the training time"; gradients all-reduced in FP16 (§3).
  - The Hivemind implementation uses a DHT built on libp2p (§2).
- **Central elements:** Hivemind DHT bootstrap (other strands cover it).
- **Question for us:** (inference) a 1.1B FP16 pseudo-gradient is about 2.2 GB (1.1 × 10⁹ × 2 bytes). How did a 300 s all-reduce of that size relate to the 127 Mbit/s slowest link? The paper does not give the ring order.

### P8. INTELLECT-1 Technical Report (communication and checkpoint sections)

- **Authors:** Jaghouar, Ong, Basra, Obeid, Straube, Keiblinger, Bakouch, Atkins et al. (Prime Intellect). Preprint.
- **arXiv:** 2412.01152. v1 2 Dec 2024 only. **Read v1.** (`01-local-averaging.md` A5 read §2, §3.1, §3.4 for the schedule; this block adds §2.2, §2.4, §2.5, §3.2.)
- **Read status:** sections read: abstract, §1, §2 intro, §2.2, §2.4.1 to §2.4.5, §2.5, §3.1, §3.2 (Table 2).
- **What it shows:**
  - Bandwidth between nodes "limited to 500 Mb to 4 Gb/s" (§2).
  - Int8 ring all-reduce with FP32 accumulation; values are quantized only for transmission. Scheme: per tensor mean μ and standard deviation σ, range [μ − 6σ, μ + 6σ], 256 uniform buckets, each bucket's code is the mean of its values (§2.2). "4 times reduction" against FP32.
  - "400×" reduction against data-parallel training (abstract; §3.1 attributes it to int8). (inference) 4× from int8 times 100× from H = 100 gives 400×.
  - Table 2 (10B model, 8 × H100 nodes, 100 inner steps take 38 minutes): median all-reduce 103 s (USA), 382 s (USA + Europe), 469 s (global); compute utilization 95.7%, 85.6%, 83.0%. §3.1 says averages of "approximately 2 minutes" (USA) and "10 minutes" (global). Covenant-72B (P4 §4.3) cites INTELLECT-1 as 8.3 minutes average.
  - **Quality effect of int8:** no ablation in the sections read; only "while delivering comparable performance" (abstract) and "while maintaining model quality" (§2).
  - **Checkpoints (§2.4.2):** a joining node downloads model and optimizer state directly from an active peer, "Rather than relying on a centralized storage system". Two modes (non-blocking with a skip of the current inner steps, or blocking). Blocking was used because non-blocking caused "small loss spikes"; transfers "completed within 30-60 minutes". Checkpoint saving to disk took 60 s (§3.2).
  - **Liveness (§2.4.3):** heartbeats every 2 s to a "master key-value store"; eviction after 6 s.
  - **Networking (§2.5):** all nodes on a Tailscale VPN, which "became a bottleneck" intercontinentally.
- **Central elements:** master key-value store (a); Tailscale coordination (c, third-party network); released checkpoints on Hugging Face (b).
- **Question for us:** peer-to-peer checkpoint transfer took 30 to 60 minutes for a 10B model's state between data centres. What would a 300M state take between homes, and can it come from a public host instead?

### P9. DiLoCo (communication section only)

- **arXiv:** 2311.08105 v3 (23 Sep 2024). **Read v3.** Sections read for this strand: §6.2 "Pruning outer gradients" (Table 6) and the "Infrastructure" paragraph. Quality numbers are in `01-local-averaging.md` A1.
- **What it shows:**
  - Table 6 (per-neuron sign pruning of each replica's outer gradient; 150M, the paper's default 8 workers, H = 500): perplexity 15.02 (0% pruned), 15.01 (25%, −0.06%), 15.08 (50%, +0.39%), 15.27 (75%, +1.66%).
  - Communication is H = 500 times less frequent than data-parallel (§3).
  - The outer step runs "on a CPU server connected to the local machines" (Infrastructure).
- **Central elements:** the CPU server for the outer step (a).

### P10. Distributed Deep Learning in Open Collaborations (DeDLOC)

- **Authors:** Diskin, Bukhtiyarov, Ryabinin, Saulnier, Lhoest, Sinitsin, Popov, Pyrkin et al. NeurIPS 2021 (arXiv comment).
- **arXiv:** 2106.10207. Versions: v1 18 Jun 2021, v2 8 Nov 2021. **Read v2.**
- **Read status:** sections read: §3.2 (backbone peers), §4.3 (volunteer run), Appendix F (fleet setups, partial), the security appendix on access passes. Not read: averaging algorithm sections (other strand).
- **What it shows (question 5 and setting for 10):**
  - "backbone" peers store checkpoints and welcome newcomers; "at least one of them is available at all times"; they "can be hosted on inexpensive servers without GPU" (§3.2). A peer that falls behind downloads "the latest parameters and optimizer statistics from one of the up-to-date peers" (§3.2).
  - The volunteer run (sahajBERT, ALBERT-large, Bengali): 40 volunteers, 91 unique devices, 15 to 35 simultaneously active (§4.3).
  - Access is through an authorization server that issues signed, expiring access passes after checking an identity provider and an allowlist (security appendix).
- **Central elements:** backbone peers needing one always online (a, by R1's definition); authorization server (a); Hugging Face identity (third-party, used at join time).
- **Question for us:** DeDLOC's backbone needs one peer always online, which R1 forbids on the owner's side. Could checkpoints on a public host replace the backbone's storage role?

### P11. Training Transformers Together

- **Authors:** Borzunov, Ryabinin, Dettmers, Lhoest, Saulnier, Diskin, Jernite, Wolf. NeurIPS 2021 Demonstration Track (arXiv comment).
- **arXiv:** 2207.03481. v1 7 Jul 2022 only. **Read v1.** **Read status:** full text (10 pages).
- **What it shows:**
  - Volunteers trained a DALL-E-style model: "1.1B parameters in total", with layer weights tied so "the model uses 8x fewer parameters" (§3.1).
  - Gradients and parameters were exchanged with "8-bit quantization" for tensors of at least 2^16 elements and "16-bit precision for other tensors" (§3.3).
  - It states that typical Internet connections run at 10 to 100 Mbit/s (§2, paraphrased because the source uses a dash; an assertion, not a measurement).
  - Training data (VQGAN codes) was hosted on the Hugging Face Dataset Hub and streamed; checkpoints were "uploaded to the Model Hub"; volunteers joined a Hugging Face organization for authentication (§2, §3.2).
  - 37 volunteers besides the authors contributed at least 10 minutes; the run lasted 2.5 months and reached 80% of its schedule (§3.4).
- **Central elements:** Hugging Face Hub (b) for data and checkpoints; Hugging Face organization membership as identity (third-party service).
- **Question for us:** this is the nearest precedent found for volunteers on home connections exchanging 8-bit updates for a model of about our size, but it reports no quality comparison for the quantization.

### P12. INTELLECT-2 (SHARDCAST only)

- **Authors:** Prime Intellect team. Preprint. **arXiv:** 2505.07291, v1 12 May 2025 only. **Read v1.**
- **Read status:** sections read: §2.2 (SHARDCAST, 2.2.1 to 2.2.3) and the compute-utilization paragraph of §4 (results).
- **What it shows (checkpoint distribution, question 5):**
  - Weights are sent from training nodes to inference workers through "a network of relay servers ... similar to a content delivery network"; checkpoints are sharded and streamed; relays keep "only the last five checkpoint versions" (§2.2).
  - nginx with per-IP rate limiting and firewall allow-lists (§2.2.1). Clients pick relays in proportion to success rate × bandwidth (§2.2.2).
  - Each worker checks the SHA-256 of the assembled checkpoint against a reference checksum from the training nodes (§2.2.3). Peer-to-peer weight transfer was rejected because of the security risks of exposing workers to each other (§2.2.3).
  - The broadcast "averaged 14 minutes", about 590 Mb/s, for 62 GB of weights (§4).
- **Central elements:** relay servers (a).
- **Question for us:** SHARDCAST's integrity check (hash of the assembled checkpoint, reference hash from the producer) is the pattern a public-host design would also need. Who publishes the reference hash when no server exists?

### H1. Hugging Face Hub: storage limits, repository limits, buckets

- **Maintainer:** Hugging Face. Documentation.
- **Source:** `huggingface/hub-docs`, read at repository commit `ef42b8f945` (main, fetched 2026-10-13 17:29). Last commits touching each file (GitHub API, 2026-10-13 17:29): `docs/hub/storage-limits.md` `a8a654b781` 2026-06-23; `docs/hub/storage-buckets.md` `b6c0e7d210` 2026-10-01; `storage-buckets-access.md` `f88183be09` 2026-09-17; `storage-buckets-s3.md` `7c0de6650b` 2026-07-07 (not read beyond a grep).
- **Read status:** files read: `storage-limits.md` (full), `storage-buckets.md` (lines 1 to 140 and a grep of the rest, including "Pricing"), `storage-buckets-access.md` (grep).
- **Limits (storage-limits.md, "Storage plans" table and "Repository limitations and recommendations"):**
  - Free user or organization: public storage "Best-effort*"; private storage 100GB. PRO: public "Up to 10TB included*"; private 1TB plus pay-as-you-go. The footnote asks users, "Beyond the first few gigabytes", to upload "content that offers genuine value to other users".
  - Abuse: "We do have mitigations in place to prevent abuse of free public storage" (line 12).
  - Public storage add-on (paid plans only): $12 per TB per month (1 to 20 TB), $10 per TB per month at 50 TB. Private pay-as-you-go: $18 per TB per month base.
  - Per repository: no size limit ("There is no per-repo size limit for models and datasets", but uploads count against the account quota); files per repo recommended < 100k; entries per folder < 10k ("cannot exceed 10k files per folder"); file size recommended < 200GB, hard limit 500GB ("no single file will exceed 500GB"); commit size recommended < 100 files; HTTP push requests time out at 60 s.
  - Commits: "There is no hard limit for the total number of commits", but the experience "starts to degrade after a few thousand commits"; a Git repository "is not meant to work as a database". History can be squashed (`super_squash_history`), and quota effects of a squash appear "within 36 hours".
  - Files are served "using CloudFront".
- **Storage Buckets (storage-buckets.md):** a repository type giving "S3-like object storage", "non-versioned and mutable", intended for "training checkpoints, logs, intermediate artifacts". The storage-limits page says its limits apply to buckets too, and the repository recommendations above "do[] not apply to Storage Buckets". Buckets have Xet chunk-level deduplication, an S3-compatible API, server-side copies between repos and buckets, optional CDN pre-warming, and a server-sent-events endpoint (`GET /api/buckets/<owner>/<bucket>/events`) that "streams a bucket's file changes"; "no token is needed for a public bucket". Pricing section: buckets "are free to create and have a free storage allowance"; beyond that, see hf.co/storage.
- **Central elements:** the Hub itself is (b). The events endpoint is a live notification service run by the host; it is still the host, not a peer network (classification as (b) is my reading; the brief's (c) covers third-party networks for live coordination, so this one is borderline and is flagged).
- **Fit:** R2 lists the Hub as an allowed central host. Free public storage is "best-effort", not a stated quota.
- **Question for us:** how many GB would a pilot store at once if only the latest checkpoint and one round's updates are kept, and does that stay within "the first few gigabytes"?

### H2. Hugging Face Hub: rate limits

- **Source:** `huggingface/hub-docs` `docs/hub/rate-limits.md`, last commit `242f4a1eeb` 2026-08-22; read at `ef42b8f945`, fetched 2026-10-13 17:29. **Read status:** full file.
- **Limits:** three buckets (Hub APIs, Resolvers i.e. `/resolve/` file downloads, Pages), all over fixed 5-minute windows. The table is labelled "current rate limits (in September '25)":

  | Plan | API | Resolvers | Pages |
  |---|---|---|---|
  | Anonymous (per IP) | 500* | 3,000* | 100* |
  | Free user | 1,000* | 5,000* | 200* |
  | PRO user | 2,500 | 12,000 | 400 |

  "*" means "subject to change over time depending on platform health". For organizations, limits apply "individually to each member, not shared".
  - "Granular user action Rate limits" exist for "repo creation", "repo commits" and others, but "We don't currently document the rate limits for those specific actions".
  - Exceeding a limit returns HTTP 429 with `RateLimit` headers; `huggingface_hub` 1.2.0+ waits and retries automatically.
- **Fit:** the commit rate limit, which matters most for frequent update uploads, is undocumented. Any pilot rate must be measured, not read (inference).
- **Question for us:** with 3 to 5 peers each uploading one update per round, how many commits per hour would a round length of, say, 30 minutes generate, and does that trip the undocumented commit limit?

### H3. Hugging Face Hub: Xet storage backend

- **Source:** `huggingface/hub-docs` `docs/hub/xet/overview.md` (last commit `b722616cc9` 2025-10-24), `xet/deduplication.md` (`c83b9adb6e` 2026-06-08), `xet/legacy-git-lfs.md` (`b722616cc9` 2025-10-24); read at `ef42b8f945`, fetched 2026-10-13 17:29. **Read status:** all three files in full.
- **What it shows:**
  - Xet replaced Git LFS on the Hub (acquired August 2024). Xet "deduplicate[s] at the level of bytes": content-defined chunking into chunks of about 64KB; new chunks are grouped into 64 MB blocks, "stored once in a content-addressed store (CAS), keyed by its hash" (deduplication.md).
  - When a Xet-backed file is updated, "only the modified data is uploaded" (overview.md).
  - Legacy clients still work through a Git LFS bridge; files keep the Git LFS pointer format with SHA-256 (legacy-git-lfs.md).
- **Inference:** an averaged model or a pseudo-gradient changes almost every value each round, so byte-level deduplication should save little on updates or new checkpoints, whatever it saves on datasets. The docs make no claim for training updates; the marketing page (H5) claims savings when "only 5% of weights change". This would need a measurement.
- **Central elements:** (b).

### H4. huggingface_hub library: upload guide and CommitScheduler

- **Source:** `huggingface/huggingface_hub` `docs/source/en/guides/upload.md`, last commit `4dc3b2875b` 2026-10-12; read at main `a704b8488c`, fetched 2026-10-13 17:30. `guides/buckets.md` (`ce69fdb010` 2026-09-22) grepped only.
- **Read status:** sections read: upload_folder behaviour, "Tips and tricks for large uploads", hf_xet, CommitScheduler.
- **What it shows:** `upload_folder` with `hf_xet` splits large folders into several commits "to stay below server limits", and is resumable from any machine because uploaded chunks deduplicate. `CommitScheduler` commits a folder every N minutes; "it is recommended to set a minimal value of 5 minutes" (to avoid "polluting the git repository"); it assumes append-only data: "Deleting or overwriting a file might corrupt your repository".
- **Question for us:** the library's own advice (≥ 5 minutes between scheduled commits; thousands of commits degrade a repo) bounds how a Git repository can serve as a per-round exchange; buckets are the documented route for mutable, frequent writes.

### H5. Hugging Face: terms of service, content policy, storage pricing page

- **Source:** web pages, fetched 2026-10-13 17:30 and tags stripped: `huggingface.co/terms-of-service` ("Effective Date: September 15, 2022"), `huggingface.co/content-policy` ("Effective Date: April 10, 2025"), `huggingface.co/storage` (marketing page, undated).
- **Read status:** page read (fetched 2026-10-13): terms, sections "Your Content" and account security; content policy, section 5 "Platform Abuse, Security Violations and Spam"; storage page, pricing section.
- **What it shows:**
  - Terms: "You may not disclose your password to any third party"; public repositories grant every user a licence to use and redistribute the content; Hugging Face may "suspend or terminate your access to the Services anytime with or without cause".
  - Content policy §5 lists as abuse "Hosting excessive or irrelevant data in repositories", "Using unauthorized bot APIs", and "excessive bulk activity".
  - Storage page: "Egress and CDN are included at no extra cost"; base $12 per TB per month public, $18 private.
- **Fit:** no clause forbids frequent checkpoint uploads by name; the operative limits are the vague "excessive" wording and the undocumented commit limits (inference).
- **Question for us:** does a run that overwrites the same small set of files each round count as "excessive bulk activity"? Only Hugging Face can answer; a written enquiry before the pilot would settle it.

### H6. GitHub: releases, repository and file limits, Git LFS

- **Maintainer:** GitHub. Documentation.
- **Source:** `github/docs`, read at main `d1a0081f24` (fetched 2026-10-13 17:31). The Markdown uses Liquid variables; their values were read from `data/variables/large_files.yml` (last commit `c548237dc9` 2026-03-26) and `data/variables/releases.yml` (`c820893a5c` 2025-07-03). Pages: `about-releases.md`, `about-large-files-on-github.md`, `about-git-large-file-storage.md` (all last changed `6c39b7b7de` 2026-07-08), `content/billing/concepts/product-billing/git-lfs.md` (`7c06b1d8a4` 2026-07-09).
- **Read status:** files read in full (about-releases, about-git-large-file-storage, git-lfs billing, the two variable files); about-large-files: sections "About size limits", "Distributing large binaries".
- **Limits:**
  - Releases: "Up to 1000 release assets may be associated with a single release" (`release_asset_limit: '1000'`). "Each file included in a release must be under 2 GiB" (`max_file_size: '2 GiB'`). "There is no limit on the total size of a release, nor bandwidth usage" (about-releases, "Storage and bandwidth quotas").
  - A second page says each release file must be smaller than "the maximum file size limit for Git LFS on your plan" (about-large-files, "Distributing large binaries"), and that limit is 2 GB on Free and Pro, 4 GB on Team, 5 GB on Enterprise Cloud (about-git-large-file-storage). The two pages agree for free accounts (2 GiB vs 2 GB, unit wording differs) and disagree for paid plans.
  - Repository files: Git warns above 50 MiB; files above 100 MiB are blocked; repositories "ideally less than 1 GB, and less than 5 GB is strongly recommended".
  - Git LFS free quota: 10 GiB bandwidth and 10 GiB storage per month on Free and Pro (`included_bandwidth_free_pro`, `included_storage_free_pro`); 250 GiB each on Team and Enterprise. Each push of a changed LFS file stores "a new version of the entire file"; downloads count against "the repository owner's bandwidth". Without a payment method, exceeding storage blocks pushes and exceeding bandwidth disables LFS "until the next month".
- **Central elements:** (b).
- **Inference (arithmetic):** Git LFS's free 10 GiB per month of bandwidth would be used up by about 10.7 GB ÷ 0.6 GB ≈ 17 downloads of a 0.6 GB checkpoint, or about 53 downloads of a 0.2 GB one (1 GiB = 1.074 GB). Release assets have no stated bandwidth cap, so a 0.2 to 0.6 GB checkpoint fits as a release asset under the 2 GiB per-file limit.
- **Question for us:** can release assets serve as the checkpoint store (a release per checkpoint, assets per shard), given the 1000-asset cap per release and the API's content-creation limits (H7)?

### H7. GitHub: REST API rate limits

- **Source:** `github/docs` `content/rest/using-the-rest-api/rate-limits-for-the-rest-api.md` (last commit `ad4064a77b` 2026-09-29) and its reusables `data/reusables/rest-api/secondary-rate-limit-rest-graphql.md` (`57d23589f5` 2026-02-13), `primary-rate-limit-unauthenticated-users.md` (`e486529b94` 2025-05-15), `primary-rate-limit-authenticated-users.md` (`383864a9af` 2026-01-13); read at `d1a0081f24`, fetched 2026-10-13 17:31.
- **Read status:** the page (grep plus lines 36 to 56) and the three reusables in full.
- **Limits:** unauthenticated 60 requests per hour per IP; authenticated 5,000 per hour. Secondary limits: at most 100 concurrent requests; 900 points per minute per REST endpoint (most writes cost 5 points); at most 80 "content-generating requests per minute" and 500 per hour; these "are subject to change without notice". Git LFS API requests have a separate bucket: 300 per minute unauthenticated, 3,000 per minute authenticated.
- **Fit:** a pilot of 3 to 5 peers making a few uploads per round is far below these limits (inference). Downloads of release assets through `github.com/.../releases/download/` URLs are not described as API requests on this page; whether they count was not established (Could not verify).

### H8. GitHub: acceptable use and terms of service

- **Source:** `github/site-policy` at `b9578b546d` (fetched 2026-10-13 17:32): `Policies/acceptable-use-policies/github-acceptable-use-policies.md` (last commit `e998634a11` 2026-04-20); `Policies/github-terms/github-terms-of-service.md` (`166eb97e48` 2026-04-27; "Effective date: April 27, 2026").
- **Read status:** acceptable use: sections 4 (grep: bulk activity) and 9 "Excessive Bandwidth Use" read; terms: account section (lines 69 to 86) read.
- **What it shows:**
  - §9: if bandwidth use is "significantly excessive in relation to other users of similar features", GitHub may "suspend your Account, throttle your file hosting, or otherwise limit your activity". Repositories "placing undue strain on our infrastructure" may be deleted after notice.
  - Prohibited: "using our servers for any form of excessive automated bulk activity".
  - Terms: one person may hold "no more than one free Account", plus at most "one free machine account", which is "used exclusively for performing automated tasks"; "Multiple users may direct the actions of a machine account", but its owner is "ultimately responsible".
- **Question for us:** "no bandwidth limit" on releases (H6) sits beside "significantly excessive" bandwidth in §9; the operative limit is GitHub's judgement. A machine account per participant is permitted for automated uploads.

### H9. BitTorrent: BEP 3, 5, 19, 46, 52

- **Maintainer:** BitTorrent.org. Specifications.
- **Source:** `bittorrent/bittorrent.org` at `7b7b41f46d` (repository `pushed_at` 2024-05-29; fetched 2026-10-13 17:33). Last commits: `bep_0003.rst` 2017-02-04 (Status Final); `bep_0005.rst` 2020-01-22 (Accepted); `bep_0019.rst` 2017-01-12 (Accepted); `bep_0046.rst` 2016-08-15 (Draft); `bep_0052.rst` 2017-08-31 (Draft).
- **Read status:** BEP 3: entities and serving steps (lines 20 to 45) and tracker sections (grep); BEP 5: abstract and overview; BEP 19: abstract to metadata extension; BEP 46: abstract to consuming content; BEP 52: overview and the `pieces root` and `piece layers` definitions.
- **What it shows:**
  - A distribution has "An ordinary web server", "A static 'metainfo' file", "A BitTorrent tracker" and an "original" downloader (BEP 3). Trackerless torrents use the DHT, where "each peer becomes a tracker" (BEP 5, Kademlia over UDP).
  - BEP 19 web seeds: an HTTP or FTP server "acts as a permanently unchoked seed"; "No changes to trackers, HTTP, or FTP servers are needed"; seeding "could be done entirely with a company or individual's existing HTTP/FTP servers". The `url-list` key in the metainfo lists the URLs.
  - BEP 52 (v2): per-file `pieces root`, the root of a SHA-256 Merkle tree over 16 KiB blocks; "identical files always result in the same root hash".
  - BEP 46 (Draft): a publisher signs a mutable DHT item pointing to the current infohash; consumers poll it by public key, so "the publisher has control over when the torrent is updated".
- **Classification:** a tracker we run is (a), or a role on bootstrap peers if it runs only while they are on (inference); the public mainline DHT, including BEP 46 update pointers, is (c); a web seed on Hugging Face or GitHub releases is (b).
- **Fit:** (inference) a torrent whose web seeds are a public host (b), with peers seeding to each other, gives peer-to-peer distribution with no always-on seed of ours. Peer discovery would still need either a tracker on our machines or the public DHT (c). Whether Hugging Face or GitHub download URLs work as BEP 19 web seeds in practice (redirects, range requests) was not checked.
- **Question for us:** BEP 52's per-file Merkle root is a content address. Could the published model version simply be a BEP 52 root, verifiable by any peer?

### H10. WebTorrent

- **Maintainer:** WebTorrent project (Feross Aboukhadijeh and contributors). Software, MIT (`license.spdx_id` "MIT"); `pushed_at` 2026-10-08; latest release v3.0.21 `published_at` 2026-07-27 (GitHub API, 2026-10-13 17:34).
- **Source:** `README.md` (last commit `40c13811e3` 2025-12-09) and `docs/faq.md` (`296e7984b3` 2026-09-13) at `bbcd95c0c0`, fetched 2026-10-13 17:34.
- **Read status:** README lines 25 to 56; FAQ "How does WebTorrent work?".
- **What it shows:** in the browser WebTorrent uses WebRTC data channels and "does not support UDP/TCP peers in browser"; a browser peer "can only connect to other clients that support WebTorrent/WebRTC". To support WebRTC's connection model "we made a few changes to the tracker protocol"; no BEP has been written ("Until a spec is written, you can view the source code").
- **Classification:** a WebSocket tracker for signalling is needed: public ones are (c); our own would be (a) (inference from the FAQ; the docs read do not discuss STUN or TURN servers).
- **Fit:** relevant only if peers run in a browser; a native client can use ordinary BitTorrent (inference).

### H11. IPFS: persistence, pinning, DHT

- **Maintainer:** IPFS project (Protocol Labs and IPFS Foundation). Documentation.
- **Source:** `ipfs/ipfs-docs` at `1261c016f2` (fetched 2026-10-13 17:34): `docs/concepts/persistence.md` (last commit `ed5f5d92c5` 2026-08-02), `docs/how-to/work-with-pinning-services.md` (`4b17e1312b` 2026-08-27), `docs/concepts/dht.md` (`3ad3e76ed5` 2024-11-26).
- **Read status:** persistence.md in full; pinning services (grep); dht.md lines 1 to 71 and the provider-records section.
- **What it shows:**
  - Nodes cache content and garbage-collect it; data persists only if it is "pinned to one or more IPFS nodes". IPFS "doesn't guarantee that any content is persistently available", only that it is discoverable.
  - Pinning services let users "pin data on those nodes for a fee"; "Some services offer a free storage allowance" (examples listed: 4EVERLAND, Filebase, Pinata, with a warning that there is "no guarantee" they continue). Local pinning works "If you have one local IPFS node that's always running" (pinning-services page).
  - Discovery uses the public Amino DHT; a separate "LAN DHT" exists for "segregated networks such as local networks or isolated VPNs". Nodes behind NAT stay in DHT client mode. "you are only allowed to put a provider record for yourself".
- **Classification:** self-pinning needs an always-on node: (a) if it is ours. A pinning service is a third-party paid host: (b) if used only as storage plus a gateway, but the public DHT it announces to is (c). Retrieval by other peers through the public network is (c).
- **Fit with R1:** persistence without a node we run requires a third-party pinning service; persistence with only intermittent home nodes is not guaranteed (the docs' own wording).
- **Question for us:** does IPFS add anything over BitTorrent v2 plus a public host for a 3 to 5 peer pilot, given that both need someone online to serve?

### H12. Cloudflare R2: pricing and limits

- **Maintainer:** Cloudflare. Documentation.
- **Source:** `cloudflare/cloudflare-docs` at `9a7810d424` (branch `production`, fetched 2026-10-13 17:35): `src/content/docs/r2/pricing.mdx` (last commit `ed083b2b78` 2026-10-01), `r2/platform/limits.mdx` (`7f91f1ccd7` 2026-06-08), `r2/get-started/index.mdx` (`cd4a0dc718` 2026-04-21), `r2/buckets/public-buckets.mdx` (grep).
- **Read status:** pricing.mdx and limits.mdx in full; get-started "Before you begin"; public-buckets (grep).
- **Limits and prices:**
  - Free tier per month: storage "10 GB-month / month"; Class A operations (writes, lists) 1 million; Class B (reads) 10 million; egress free. Free tier applies only to Standard storage.
  - Beyond: $0.015 per GB-month; Class A $4.50 per million; Class B $0.36 per million. Usage is rounded up to the next unit ("1.1 GB-month ... billed for 2 GB-month").
  - Egress: "There are no charges for egress bandwidth for any storage class".
  - Object size up to 4.995 TiB; single-part upload up to 4.995 GiB; "Maximum concurrent writes to the same object name (key)": 1 per second.
  - `r2.dev` public URLs are "not intended for production usage" and are rate limited ("hundreds of requests/second") and may be bandwidth-throttled; production use needs a custom domain.
  - Getting started: "You need a Cloudflare account with an R2 subscription", added through a "checkout flow"; "R2 is free to get started with included free monthly usage."
- **Classification:** (b), a public object store; but each bucket belongs to an account that has subscribed, so a bucket the owner opens is a service the owner may end up paying for. Not a server we run, but R1 also excludes things the owner pays for around the clock; whether a free-tier bucket counts is for the owner (flag).
- **Use in decentralized training:** Templar and Covenant-72B use one R2 bucket per peer (P3, P4, S1).
- **Inference (arithmetic):** the 10 GB-month free storage holds about 16 copies of a 0.6 GB checkpoint or 50 of a 0.2 GB one, if kept all month; free egress means downloads by peers cost nothing on the R2 side.

### S1. Templar (Covenant): storage side

- **Maintainer:** Covenant AI (formerly tplr.ai); repository `one-covenant/templar` (the old name `tplr-ai/templar` redirects). Software. Licence `MIT` (`license.spdx_id`), `pushed_at` 2026-10-04T16:14:55Z (GitHub API, 2026-10-13 17:36).
- **Source:** read at `0fefc2ad76` (fetched 2026-10-13 17:36). Files: `docs/miner.md` (last commit `65c4059bd9` 2026-01-21), `docs/validator.md` (same commit; grep only), `src/tplr/dcp_checkpoint.py` (`f607562af2` 2025-10-06). `docs/r2_bucket_management.md` fetched, not read.
- **Read status:** files read: `miner.md` (prerequisites, environment variables, "Miner Operations"); `dcp_checkpoint.py` (class docstring, `Layout`, `_choose_read_bucket`, `_discover_latest`, `download_distributed` docstring).
- **What it shows:**
  - Each miner creates its own R2 bucket for gradients, "Name it the same as your account ID", with a read token and a read-write token (miner.md). Shared dataset and "aggregator" buckets are read with credentials published in the documentation itself.
  - At startup the miner "Attempts to load the latest checkpoint from the validator with the highest stake" (miner.md, "Model Synchronization").
  - Checkpoints are PyTorch Distributed Checkpoint (DCP) sharded checkpoints: "each rank uploads its shard subset; rank-0 uploads metadata + _LATEST.json"; on download, DCP "reshards to miner topology" (class docstring). Keys follow `checkpoints/<version>/<window>/`; the newest window is found from `_LATEST.json` or by listing (`_discover_latest`). The reader tries "highest-staked validator bucket first, then own".
- **Central elements:** per-peer R2 buckets (b, paid accounts); the stake ranking that picks which validator's checkpoint is authoritative comes from the Bittensor chain (c).
- **Fit:** the storage pattern (each writer owns a bucket; a pointer file names the latest version; readers choose whose bucket to trust) maps onto R7's "signed per-peer storage" option, with the chain as the trust selector (inference).
- **Question for us:** without a chain, what replaces "highest-staked validator" as the rule for whose checkpoint to load: a merge every peer recomputes, or a signature from a known key?

### S2. Psyche (Nous Research): storage side

- **Maintainer:** Psyche Foundation / Nous Research. Repository `PsycheFoundation/psyche`, which now redirects to `PsycheFoundation/nousnet`. Software. Licence `Apache-2.0`; `pushed_at` 2026-03-24T20:46:58Z (GitHub API, 2026-10-13 17:36).
- **Source:** read at `0bdb13d94a` (fetched 2026-10-13 17:37). Files: `psyche-book/src/explain/model-sharing.md` (last commit `370bdb5300` 2026-01-13), `explain/gcs-checkpoints.md` (`c3dce1a0cb` 2026-02-20), `enduser/join-run.md` (`21e821d28a` 2026-03-02), `tools/rust-tools/run-manager/README.md`, `run-manager/src/docker/coordinator_client.rs` and `docker/manager.rs` (both `21e821d28a` 2026-03-02).
- **Read status:** model-sharing.md in full; gcs-checkpoints.md: setup steps and "Checkpoint Manifest" (lines 104 to 213, grep plus reading); join-run.md lines 1 to 80 and grep; run-manager files: grep and the `get_docker_tag_for_run` function.
- **What it shows:**
  - At the start of a run "all clients must download the model parameters" from Hugging Face. Every client then applies the other clients' results, keeping copies "identical within an epoch without an additional full synchronization step" (model-sharing.md).
  - Two checkpoint variants for joiners: (1) **Hugging Face checkpoint**: clients that declare a checkpoint URL act as "checkpointers", upload the model after each epoch and send the URL to the coordinator; a joiner gets the URL from the coordinator. (2) **P2P checkpoint**: a joiner requests "a set of parameters for each layer from different clients", so no single peer has to serve the whole model (model-sharing.md and its diagram: layer 1 from client 1, layer 2 from client 2, layer 3 from client 3).
  - GCS checkpoints use a `manifest.json` uploaded "after all safetensors files are successfully uploaded", acting as "an atomic marker", recording each file's GCS generation so downloads cannot mix versions while an upload is in progress (gcs-checkpoints.md). Setting up GCS needs "A credit or debit card for billing purposes". Config files (`.json`, `.py`) are fetched by listing, outside the manifest.
- **Central elements:** the coordinator (on Solana for on-chain runs; the chain is (c)); Hugging Face (b); GCS buckets (b, paid account).
- **Fit:** the P2P layer-wise checkpoint is the nearest precedent found for assembling a model from peers that each serve part of it. It still assumes every training client holds the full model (inference from "all clients must have an identical model").
- **Question for us:** Psyche's manifest-last pattern is the documented answer to "a reader sees half an upload". Is the same needed on a Hugging Face Git repository, where files arrive as commits (whether a multi-file commit becomes visible all at once is not stated in H1), or only on object stores and buckets?

### S3. Prime Intellect: storage side (prime-diloco, INTELLECT-1's framework)

- **Repository note:** the INTELLECT-1 report (P8) points to `github.com/PrimeIntellect-ai/prime`. On 2026-10-13 that repository's description is "Official CLI and Python SDK for Prime Intellect" (`pushed_at` 2026-10-13T00:22:13Z) and its tree has no training code. The training framework is in `PrimeIntellect-ai/prime-diloco` (description "prime is a framework for efficient, globally distributed training of AI models", created 2024-09-11, licence `Apache-2.0`, `pushed_at` 2026-07-17T22:02:52Z) (GitHub API, 2026-10-13 17:38). (inference) `01-local-averaging.md` A5's code link and its "MIT, pushed 2026-10-11" refer to the repurposed repository, not to the framework.
- **Source:** `prime-diloco` `src/zeroband/checkpoint.py` (last commit `ced4ca77ce` 2025-02-05), read at `de5b9317da`, fetched 2026-10-13 17:38.
- **Read status:** files read: `checkpoint.py` (function list, `save`, `_async_save_remote`, `recv_ckpt_from_peer` signature and loop).
- **What it shows:** checkpoints are written with `torch.distributed.checkpoint` (`dcp.save`) to local disk, then optionally pushed "asyncronously" to a remote path with fsspec's `rsync` ("to handle remote cloud storage without to install specific libraries (e.g. s3fs)"). Data-loader state is pushed per data rank to a separate remote path with a `latest` copy. Live recovery (`recv_ckpt_from_peer`) receives model, outer-optimizer, optimizer and scheduler state from a configured source rank over the process group (matches P8 §2.4.2).
- **Central elements:** remote storage is whatever fsspec URL is configured (b if a public bucket); the process group needs the master key-value store (a) (P8).
- **Question for us:** fsspec makes the storage backend a URL; a Hugging Face `hf://` path is an fsspec filesystem too (H1 access patterns). Is any storage-specific code needed at all?

### S4. Hivemind: storage side

- **Maintainer:** learning-at-home. Software. Licence `MIT`; `pushed_at` 2026-01-11T21:13:45Z (GitHub API, 2026-10-13 17:36). Maintenance is another strand's question.
- **Source:** read at `4bd43b7789` (fetched 2026-10-13 17:39): `README.md` (last commit 2026-01-04), `hivemind/averaging/averager.py` (`02184953d9` 2025-04-18), `hivemind/compression/__init__.py`.
- **Read status:** files read: README install section; `averager.py` docstring parameters and `_declare_for_download_periodically`; compression `__init__.py`.
- **What it shows:**
  - No checkpoint store. A peer with `allow_state_sharing` periodically stores itself in the DHT under `<prefix>.all_averagers` as a state donor (every `declare_state_period`, default 30 s) with a priority; a newcomer calls `load_state_from_peers` and downloads state over RPC from a donor (`averager.py`).
  - Compression codecs available for averaging and state transfer: `Float16Compression`, `ScaledFloat16Compression`, `Uniform8BitQuantization`, `Quantile8BitQuantization`, `BlockwiseQuantization` (bitsandbytes), plus per-tensor, size-adaptive and role-adaptive wrappers (`compression/__init__.py`). State transfer has its own `state_compression` (default none).
- **Central elements:** none for storage; state lives only on online peers (inference: if every peer goes offline, the state is gone unless someone saved it elsewhere).
- **Question for us:** for a pilot where all peers may be off at night, Hivemind's model needs an outside checkpoint store; DeDLOC (P10) and Training Transformers Together (P11) used the Hugging Face Hub for that.

### S5. Petals: storage side

- **Maintainer:** BigScience workshop. Software. Licence `MIT`; `pushed_at` 2024-09-07T11:54:28Z (GitHub API, 2026-10-13 17:36).
- **Source:** read at `22afba627a` (fetched 2026-10-13 17:39): `README.md` (last commit `a2d4b65ae0` 2024-07-24), `src/petals/server/from_pretrained.py` (`8ad5513bea` 2024-07-24).
- **Read status:** files read: README (grep of install and hosting lines); `from_pretrained.py` module docstring and `_load_state_dict_from_repo`.
- **What it shows:** each server holds only some transformer blocks and loads just those from the Hugging Face Hub: it reads `model.safetensors.index.json`, keeps the files whose `weight_map` entries start with the block prefix, and downloads only those shards. The module docstring lists, as possible alternatives, S3, "BitTorrent ... or IPFS".
- **Central elements:** Hugging Face Hub (b) for weights; Petals' public swarm and its bootstrap peers are other strands' subject.
- **Fit:** the nearest precedent found for a peer that never holds the whole model fetching only its part from a public host. Petals serves pretrained weights; it does not train and write them back.
- **Question for us:** if each expert's tensors are kept in their own shard files with a safetensors index, a slice holder could download only the shared part plus its experts the way Petals does (inference). Does `huggingface_hub` permit partial downloads of a Xet-backed file, or only of whole files?

### T1. BOINC code signing (contrast case, mechanism only)

- **Maintainer:** BOINC project (UC Berkeley). Documentation (wiki).
- **Source:** the BOINC wiki repository `github.com/BOINC/boinc.wiki.git`, shallow clone at `7e16379966` (2026-10-10), made 2026-10-13 17:42. Pages: `Code-signing.md`, `Security-in-volunteer-computing.md`, `BoincSecurity.md` (all at that commit; the shallow clone shows no earlier history). Files read only; nothing run.
- **Read status:** files read: all three in full.
- **What it shows:**
  - "When a project is created, an RSA key pair is created"; the public key goes to clients when they attach; each app-version file gets a signature made with the private key; "The client verifies that the file matches the signature" (Code-signing.md).
  - The aim is to stop attackers, "even if they've broken into your server", from distributing malware. The page recommends keeping the private key encrypted, or better on "a separate computer" that "must remain physically secure and disconnected from the network", moving files by USB stick (Code-signing.md).
  - Key rotation: the new public key is signed with each old private key, so clients accept it without re-attaching (Code-signing.md).
  - Threats listed include "Malicious executable distribution" (answered by code signing) and "Result falsification" (answered by replication or other validation). Input and output files are not encrypted. Applications run under a separate account ("account-based sandboxing") (Security-in-volunteer-computing.md).
  - "The BOINC system requires that you run executables provided by a third party"; official client builds are signed with the UC Berkeley code-signing key (BoincSecurity.md).
- **Work units as data:** in BOINC the application is signed code and the work unit's input files are data; the code itself also comes from the project server (inference from the pages read; the term "work unit as data" is not BOINC's).
- **Central elements:** the project server (a); the offline signing machine holds the key (the R2-permitted "code-signing key").
- **Question for us:** BOINC's offline key plus signed key rotation is a complete key-based scheme with no third-party service. Does Chorus need anything more than this for a trusted pilot?

### T2. Sigstore and cosign

- **Maintainer:** Sigstore project (OpenSSF). Documentation.
- **Source:** `sigstore/docs` at `b25f111947` (fetched 2026-10-13 17:40): `content/en/about/overview.md` (last commit `dbfbe9cdfc` 2026-04-15), `about/bundle.md` (`aabcc1915e` 2026-08-25), `cosign/verifying/verify.md` (`2b0f856d21` 2026-04-15), `cosign/signing/overview.md` and `signing_with_blobs.md` (`dbfbe9cdfc` 2026-04-15), `cosign/key_management/overview.md` (`29b73b3299` 2026-10-05; first lines only).
- **Read status:** about/overview.md in full; verify.md and bundle.md: grep plus the passages on bundles and offline verification; signing_with_blobs.md in full; signing/overview.md: the transparency-log paragraph.
- **What it shows:**
  - Keyless signing: the client makes an ephemeral key pair, sends an OIDC identity token to Fulcio, gets "a short-lived certificate bound to the provided identity", signs, and records digest, signature and certificate in Rekor, "an immutable, append-only ledger". Verification checks the signature, the identity in the certificate, the certificate chain to "Sigstore's root of trust", and inclusion in Rekor (about/overview.md).
  - Key-based signing of files is also supported: `cosign sign-blob --key cosign.key --bundle bundle.sigstore.json` (signing_with_blobs.md).
  - A bundle holds everything needed to verify; with short-lived certificates it must include a log's signed entry timestamp or an RFC 3161 timestamp (bundle.md). The newer bundle format "supports offline verification" (verify.md).
- **Classification:** the Sigstore public-good instance (Fulcio, Rekor) is a third-party online service used at signing time, and for online verification. It does not fit (a), (b) or (c) cleanly, because it does not coordinate training; it is flagged rather than classified. Key-based signing with a key the owner holds needs none of it (inference).
- **Question for us:** R2 allows "the code-signing key" to stay central. Keyless signing replaces that key with an identity (for example the owner's GitHub Actions workflow). Which of the two does the owner mean?

### T3. GitHub artifact attestations

- **Source:** `github/docs` at `d1a0081f24` (fetched 2026-10-13 17:31): `content/actions/concepts/security/artifact-attestations.md` (last commit `25d85ce313` 2026-07-16), `content/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline.md` (`1484a08c7c` 2026-07-16). **Read status:** both files in full.
- **What it shows:** GitHub generates attestations with Sigstore; for public repositories "the Sigstore Public Good Instance", with the bundle "written to an immutable transparency log". Attestations alone give "SLSA v1.0 Build Level 2"; building in a shared reusable workflow can reach Build Level 3. "artifact attestations are not a guarantee that an artifact is secure"; they link the artifact to its source and build instructions. Offline verification: download the bundle (`gh attestation download`) and the trusted root (`gh attestation trusted-root`) while online, then `gh attestation verify ... --bundle ... --custom-trusted-root`; the trusted root has no built-in expiry, and offline you "will not know if key material has been revoked".
- **Classification:** GitHub (b) plus the Sigstore public-good instance (flagged as in T2).
- **Question for us:** a client that verifies offline needs a trusted root shipped with it; who refreshes that root when Sigstore rotates keys "a few times per year"?

### T4. PyPI Trusted Publishing and attestations

- **Maintainer:** PyPI (Python Software Foundation). Documentation and API.
- **Source:** `pypi/warehouse` at `20c44b5595` (fetched 2026-10-13 17:41): `docs/user/trusted-publishers/index.md` (last commit `e6bdf57bed` 2024-12-12), `docs/user/attestations/index.md` (`83e36c7420` 2026-08-12), `attestations/consuming-attestations.md` (`23808cea05` 2026-03-12), `attestations/security-model.md` (grep). PyPI JSON API and Integrity API, queried 2026-10-13 17:42.
- **Read status:** trusted-publishers index (first 40 lines), attestations index and consuming-attestations in full; security-model grep only.
- **What it shows:**
  - Trusted Publishing exchanges an OIDC token from a CI service for "a short-lived API token" that is "only valid for 15 minutes".
  - Attestations (PEP 740) bind each distribution file to a digest and an identity; PyPI accepts SLSA Provenance and PyPI Publish predicates, signed by Trusted Publisher identities (GitHub Actions, GitLab CI/CD, Google Cloud, ActiveState). They are served through the simple index and the Integrity API; the consuming guide names the `pypi-attestations` CLI for manual verification. The pages read do not say that pip verifies them.
  - **Hivemind** 1.1.12 (latest on PyPI, files uploaded 2026-01-03): the Integrity API returns a provenance object for the manylinux x86_64 wheel and the sdist (HTTP 200). Decoded: publisher `{"kind": "GitHub", "repository": "learning-at-home/hivemind", "workflow": "release.yml"}`, predicate `https://docs.pypi.org/attestations/publish/v1`, subject digest matching the wheel's SHA-256 (`acb8f0cf2cdb0852…`).
  - **Petals** 2.2.0.post1 (latest on PyPI, uploaded 2023-11-20): "No provenance available" (HTTP 404). The Petals README installs from Git (`pip install git+https://github.com/bigscience-workshop/petals`) or Docker (S5).
- **Classification:** PyPI (b); attestation signing uses Sigstore (T2).
- **Question for us:** Hivemind's README says it ships "the precompiled binary of the go-libp2p-daemon" (S4). A publish attestation proves which workflow uploaded the wheel, not what the binary inside was built from.

### T5. How the candidate systems distribute client code (from sources already listed)

- **Hivemind (S4, T4):** `pip install hivemind` from PyPI (publish attestations present for 1.1.12) or from source; the wheel contains a precompiled go-libp2p-daemon binary, which can be rebuilt with `HIVEMIND_BUILDGO=1`; a Docker image is also offered (README).
- **Petals (S5, T4):** `pip install git+https://github.com/...` or a Docker image; no PyPI provenance for the latest PyPI release.
- **Psyche (S2):** participants receive a `run-manager` binary that "should have been distributed to you"; it pulls the client Docker image and keeps it updated (join-run.md). The image is chosen from the run's coordinator account on the Solana chain: if the stored `client_version` starts with `sha256:`, the image is pulled as `nousresearch/psyche-client@sha256:<digest>`, otherwise by tag (`coordinator_client.rs`, `get_docker_tag_for_run`). A grep of `docker/manager.rs` for "digest", "sha256", "pull", "verify" and "signature" found the pull itself, "Verify docker is available", and Solana key-pair imports, but no image-signature check (grep only; absence not proven). (inference) The trust anchor is whoever can write the run's on-chain `client_version`, and the content address is the image digest.
- **Templar (S1):** `git clone` of the repository then `uv sync`, or Docker Compose (miner.md). No signing step in the sections read.
- **Prime (S3):** not checked for client distribution.
- **Question for us:** Psyche's pattern (a content digest of the code, published where every client reads it) works with a digest in any authenticated place, such as a signed file on a public host (inference).

### T6. Reproducible builds (definition)

- **Source:** `reproducible-builds.org/docs/definition/`, page read (fetched 2026-10-13 17:44; tags stripped).
- **What it shows:** A build is reproducible if "any party can recreate bit-by-bit identical copies of all specified artifacts" from "the same source code, build environment and build instructions". The relevant attributes are "defined by the authors or distributors"; reproducibility "is verified by bit-by-bit comparison", usually with cryptographic hashes.
- **Fit:** for a pure-Python client the artifact is source plus pinned dependencies; the hard part would be the binary dependencies (PyTorch, CUDA wheels), which the project does not build (inference).

### T7. Keeping work units and updates as data: safetensors, `torch.load`, Hub pickle scanning

- **safetensors:** `huggingface/safetensors` README (last commit `62e4d8b860` 2026-04-15), read at `e246a25606`, fetched 2026-10-13 17:44; licence `Apache-2.0`. Read status: sections "Format", "Yet another format?", "Benefits" (grep). It is a format "for storing tensors safely (as opposed to pickle)": an 8-byte header length, a JSON header (dtype, shape, offsets; `__metadata__` string-to-string only), then raw bytes. Its "Safe" criterion (a downloaded file can be used "and expect not to run arbitrary code") is marked yes for safetensors and no for pickle. The header is limited to 100MB "to prevent parsing extremely large JSON". "Tensor values are not checked"; "NaN and +/-Inf could be in the file". The byte buffer "cannot contain holes", which "prevents the creation of polyglot files".
- **PyTorch:** `pytorch/pytorch` `docs/source/notes/serialization.md` (last commit `2a847c2a16` 2026-05-08), read at `52976db7b6`, fetched 2026-10-13 17:45; section "`torch.load` with `weights_only=True`" read. "Starting in version 2.6, `torch.load` will use `weights_only=True`" by default; it "narrows the surface of remote code execution attacks" but "does not guard against denial of service attacks" and memory corruption "might still be possible".
- **Hugging Face Hub:** `docs/hub/security-pickle.md` (last commit `810aeb31d2` 2024-03-14), grep: pickle loading allows "dangerous arbitrary code execution attacks"; the Hub scans every pushed file with ClamAV and a "Pickle Import scan".
- **Fit:** (inference) a work unit made of a model version identifier, shard IDs and settings in JSON, and updates as safetensors files, contain no code under these formats' own guarantees; the NaN/Inf note means the merge must still check values. Psyche's GCS checkpoints also fetch `.py` config files from the bucket (S2), which would be code if a loader executes them.

## Findings for questions 5, 8 and 10

### Question 5a: limits of the public hosts a pilot would use (read 2026-10-13)

| Host | Size limits | Rate and quota limits | Terms that bear on frequent uploads | Class |
|---|---|---|---|---|
| Hugging Face Hub, Git repos (H1, H2, H4, H5) | 500GB per file (hard), < 200GB recommended; no per-repo limit; < 100k files, < 10k per folder | Free public storage "Best-effort"; free private 100GB. Downloads ("Resolvers") 5,000 per 5 min for a free user, 3,000 per IP anonymous ("September '25" table). Commit limits exist but are undocumented. "a few thousand commits" degrade a repo | "Hosting excessive or irrelevant data", "excessive bulk activity" are abuse (content policy §5); account can be suspended "with or without cause" (terms) | (b) |
| Hugging Face Storage Buckets (H1) | as above for quota; repo recommendations do not apply | not stated beyond the account quota; S3-compatible; change-event stream endpoint | same terms | (b), events endpoint flagged |
| GitHub releases (H6, H7, H8) | 1000 assets per release; each asset under 2 GiB (or the plan's LFS limit, 2 GB free); no limit on total release size | "nor bandwidth usage" (releases page); API: 5,000 requests per hour, 80 content-creating requests per minute, 500 per hour | "significantly excessive" bandwidth may lead to throttling or suspension (acceptable use §9) | (b) |
| GitHub Git LFS (H6) | 2 GB per file on Free and Pro | 10 GiB storage and 10 GiB download bandwidth per month free; then blocked without a payment method | as above | (b) |
| Cloudflare R2 (H12) | 4.995 TiB per object; 4.995 GiB single-part upload | free per month: 10 GB-month, 1M writes, 10M reads; egress free; 1 write per second per key | needs "an R2 subscription" (checkout flow) | (b), owner's paid account: flag for R1 |
| BitTorrent (H9) | none in the protocol | none; needs a tracker (a, or a role on our peers) or the public DHT (c); BEP 19 web seeds can be (b) | n/a | mixed |
| IPFS (H11) | none in the protocol | persistence needs a pinned, online node: our own always-on node (a) or a paid pinning service; discovery via the public Amino DHT (c) | pinning services' own terms (not read) | (a) or (c) |

(inference) Against a pilot full update of 0.2 to 0.6 GB in fp16, no host's per-file limit binds. What binds is per-round frequency: Git LFS's 10 GiB per month of downloads, Hugging Face's undocumented commit limits and its "a few thousand commits" guidance, and the vague "excessive" clauses of both Hugging Face and GitHub. Hugging Face Storage Buckets are the only free-tier option documented for mutable, overwrite-in-place checkpoints without commit history; their free allowance is not quantified.

### Question 5b: how systems persist state when no peer holds the whole model

What the sources show:

- **Every system read keeps at least one complete copy somewhere.** Psyche's training clients all hold the identical full model (S2); Hivemind and DeDLOC peers hold full state and newcomers download it from a peer (S4, P10); INTELLECT-1 transfers the full model and optimizer state peer to peer, 30 to 60 minutes for 10B (P8); Templar and Covenant store full checkpoints in a validator's bucket (S1); Petals serves pretrained weights whose full copy lives on the Hugging Face Hub (S5). No source read stores a training checkpoint only as pieces spread across peers that each hold part of the model.
- **Partial retrieval from a full public copy:** Petals servers download only the shard files containing their blocks, found through `model.safetensors.index.json` (S5). Psyche's P2P checkpoint assembles a joiner's model layer by layer from different peers (S2).
- **Sharded checkpoint formats:** PyTorch Distributed Checkpoint, used by Templar (resharded "to miner topology" on load, S1) and prime-diloco (S3); sharded safetensors with an index, used by Psyche and Petals (S2, S5).
- **Pointers and atomicity:** Templar writes `_LATEST.json` naming the newest window (S1). Psyche writes `manifest.json` after all shards, as "an atomic marker" with per-file generation numbers, because bucket listings are eventually consistent (S2). Hugging Face commits are versioned Git commits; buckets are not versioned (H1).
- **Content addressing:** Xet stores ~64KB content-defined chunks in 64 MB blocks in a content-addressed store, and Git LFS pointers carry SHA-256 (H3); BitTorrent v2 gives each file a SHA-256 Merkle root (H9); SHARDCAST checks the SHA-256 of the assembled checkpoint against the producer's reference (P12).
- **Where the four named systems put checkpoints:** Psyche: Hugging Face (checkpointer clients) or peer-to-peer, plus optional GCS (S2). Templar and Covenant: per-peer Cloudflare R2 buckets; the checkpoint read is the highest-staked validator's (S1, P4). Prime Intellect: local DCP plus fsspec `rsync` to any remote URL, and peer-to-peer live recovery (S3, P8); released checkpoints on Hugging Face (P8). Hivemind: no store; donors announced in the DHT serve state (S4).

Inference (labelled): for Chorus's slices, a checkpoint written as one shard file per expert plus one for the shared part, with an index, would let a slice holder fetch only its part from a public host the way Petals does. Nothing read shows such a layout in a training system, and nothing read tests whether R5's two holders per expert are enough to rebuild a checkpoint when the public copy is stale.

### Question 8: genuine code, and work units as data

What the sources show:

- **Key-based signing (BOINC, T1):** a project RSA key pair; each application file is signed, ideally on an offline machine; clients verify every file against the project's public key; a new key is accepted because each old key signs it. Even a compromised project server cannot make clients accept unsigned code. BOINC also sandboxes applications under a separate account. This needs no third-party service.
- **Identity-based signing (Sigstore, T2; GitHub attestations, T3; PyPI attestations, T4):** a CI identity (OIDC) gets a short-lived certificate; signatures are logged in Rekor. Verification can be done offline with a downloaded bundle and trusted root, at the cost of not seeing revocations. Both GitHub and Sigstore say attestations establish provenance, not safety ("not a guarantee that an artifact is secure", T3).
- **What the candidate systems do (T5):** Hivemind's PyPI wheels carry PyPI publish attestations from its GitHub release workflow (verified through the Integrity API) and embed a precompiled libp2p daemon. Petals installs from Git with no provenance on its latest PyPI release. Psyche pins the client Docker image by `sha256` digest in the run's on-chain coordinator account. Templar is installed by `git clone`. In the files read, no candidate's client verifies a code signature before running; Psyche's digest pin is the closest mechanism.
- **Reproducible builds (T6):** defined as bit-for-bit identical artifacts from the same source, environment and instructions. No candidate's documentation read claims reproducible builds (not searched for beyond the files listed).
- **Work units and updates as data (T7):** safetensors is designed so a downloaded file cannot run code; its header is capped at 100MB; values are not checked, so NaN and Inf can arrive. `torch.load` defaults to `weights_only=True` since PyTorch 2.6, which "narrows" but does not remove the attack surface. The Hub scans pickles. Psyche's checkpoint download fetches `.py` config files (S2), a possible code path.

Inference (labelled): R2's "code-signing key" matches the BOINC pattern (one owner key, offline, signing releases) more directly than keyless Sigstore, which would make an online identity provider and Sigstore's public-good instance part of the trust chain. The roadmap's principle 2 (work units are data, never code) has direct support in the formats read, provided the client never loads pickle or executes files fetched with a checkpoint.

### Question 10: update sizes and compression

Sizes reported (all data-centre or cloud settings; per worker unless stated):

| Source | Model | What is sent | Size or ratio | Quality effect reported |
|---|---|---|---|---|
| OpenDiLoCo (P7) | 150M, 1.1B | FP16 pseudo-gradient every 125 or 500 steps | half of FP32; all-reduce 300 s on 127 to 935 Mbit/s links (1.1B) | FP16 vs FP32: "no noticeable impact" (150M, figure only) |
| INTELLECT-1 (P8) | 10B | int8 pseudo-gradient every 100 steps | 4× vs FP32; "400×" vs data-parallel; median all-reduce 103 s to 469 s | no ablation found; "comparable performance" (claim) |
| Streaming DiLoCo (P5) | 35M to 4B | FP4 (E3M0) outer gradients, streamed fragments | 1B: 1.10 TB over 25B tokens vs 441 TB for data-parallel (whole method) | "no sign of performance regression" from FP4 (text; figure only) |
| MuLoCo (P6) | 416M, K = 8, H = 30 | quantized or top-k pseudo-gradient | 8, 4, 2 bits; top-k 0.5% to 50% | 4-bit lossless; 2-bit statistical fine, 2-bit linear "substantial" degradation; extreme top-k not viable (figures only) |
| SparseLoCo (P3) | 512M, R = 8, H = 15 | top-k 3.12% + 2-bit + error feedback | 17.21 MB vs 512.40 MB for 8-bit DiLoCo | loss 2.70 vs DiLoCo 2.76 vs AdamW DDP 2.69 (Table 1); 1-bit fails (4.79) |
| Covenant-72B (P4) | 72B | SparseLoCo, top-k 64 of 4096 + 2-bit | "more than 146×" vs dense | no ablation; benchmarks only |
| DiLoCo (P9) | 150M, 8 workers, H = 500 | sign-pruned outer gradients | 25% / 50% / 75% pruned | perplexity −0.06% / +0.39% / +1.66% |
| DeMo (P1) | 300M, 1B | DCT top-k momentum, every step | 300M: 7.49 MB per step at k = 8 vs 636.9 MB (AdamW-DDP) | downstream equal or better at 100B tokens; worse than tuned AdamW at equal updates (300M, figure only) |
| DisTrO report (P2) | 1.2B | not described | 86.8 MB received per step vs 74.4 GB (857×) | final loss 2.373 vs 2.449 (garbled table, row mapping recovered from the 857× in §3; see P2); "smaller models do not converge as well" (50M, 300M) |
| Training Transformers Together (P11) | 1.1B with weight tying | 8-bit (large tensors) and 16-bit gradients and parameters | not stated | none reported |

Where sources disagree or condition each other:

- **Dropping values:** Streaming DiLoCo and MuLoCo find value-dropping (top-k, random dropout) worse than lowering precision; SparseLoCo finds top-k fails with DiLoCo's outer momentum but works when error feedback replaces it; DeMo makes top-k work through a DCT and momentum subtraction. The results are consistent once the method around the top-k is specified.
- **2-bit:** fine with statistical quantization (SparseLoCo, MuLoCo), poor with linear quantization (MuLoCo).
- **DisTrO at small scale:** the 2024 report says 300M models "do not converge as well" with DisTrO; DeMo v2 (2026) reports 300M results comparable to AdamW-DDP downstream. The DisTrO README calls DeMo the "seed research/idea for DisTrO", so the two may not be the same algorithm and this is not a direct contradiction. A grep of the DeMo v2 text finds no mention of DisTrO.
- **INTELLECT-1's communication time:** "approximately 2 minutes" and "10 minutes" (§3.1) against medians of 103 s and 469 s (Table 2); Covenant-72B cites 8.3 minutes on average.

Inference (labelled; arithmetic shown): a full update for 100M to 300M parameters is 0.2 to 0.6 GB in fp16 (2 bytes per parameter), 0.1 to 0.3 GB in int8, 0.05 to 0.15 GB at 4 bits. At an uplink of U Mbit/s, sending S GB takes 8,000 × S ÷ U seconds: at an assumed U = 20, 0.6 GB takes 240 s, 0.3 GB 120 s, 0.15 GB 60 s. Scaling SparseLoCo's 17.21 MB at 512M linearly to 300M gives about 10 MB (17.21 × 300 ÷ 512), about 4 s at 20 Mbit/s. In an all-to-all exchange through a host each of N peers also downloads N − 1 updates: with N = 5 and 0.6 GB, 2.4 GB per peer per round. The uplink figure is a parameter, not a sourced number; the only sources stating home speeds are an assertion of 10 to 100 Mbit/s (P11, paraphrased) and an assumed 100 down, 10 up (P2).

Unknowns:

- No source measured any of these schemes over home connections or with consumer GPUs.
- The smallest models with compression results are 150M (DiLoCo pruning; OpenDiLoCo FP16), 178M (SparseLoCo Appendix J, not read), 300M (DeMo) and 416M (MuLoCo); none uses 3 to 5 workers with plain averaging, and none uses MoE slices with per-expert averaging. SparseLoCo has one MoE result (645M total, 273M active) with all experts on every worker.
- No source isolates int8's quality cost in INTELLECT-1.

### Fit with R1 to R7 for blocks without a "Fit" line

| Block | R1 to R7 relevance |
|---|---|
| P6 MuLoCo, P9 DiLoCo | algorithms only; bear on R4 and R6 indirectly through update size; DiLoCo's experiments used a CPU server for the outer step (a) |
| P7 OpenDiLoCo | Hivemind DHT bootstrap (other strands); relevant to R4 as synchronous rounds only |
| P8 INTELLECT-1 | master key-value store (a) and Tailscale (c) conflict with R1 and R3 |
| P10 DeDLOC | backbone peer always online and an authorization server: (a), against R1 |
| P11 Training Transformers Together | Hugging Face Hub for data and checkpoints, consistent with R2 |
| P12 INTELLECT-2 | relay servers (a), against R1 |
| H3 Xet, H4 huggingface_hub | storage mechanics under R2's allowed hosts |
| H6 GitHub releases, H8 terms | allowed by R2; limits as tabled |
| H12 R2 | allowed by R2 as a file host if the owner accepts a subscribed account (R1 flag) |
| S3 prime-diloco, S4 Hivemind | storage needs an outside store for R1 (no always-on peer) |
| T1 to T4 | R2 allows the code-signing key; Sigstore's online services would be an extra central element (flag) |

## Could not verify

- **Hugging Face commit rate limits:** the rate-limits page says they exist and are not documented (H2).
- **Hugging Face free public storage:** "Best-effort" and "the first few gigabytes" are not quantified (H1); bucket free allowance likewise.
- **BEP 19 web seeds on Hugging Face or GitHub URLs:** whether their redirects and range requests work with BitTorrent clients was not tested or documented in what was read.
- **Cloudflare R2 checkout:** whether the "checkout flow" for an R2 subscription requires a payment card was not stated in the page read.
- **GitHub release downloads and API limits:** whether `github.com/.../releases/download/...` downloads count against REST rate limits is not stated on the page read.
- **cosign key-based signing:** whether `sign-blob --key` also uploads to the Rekor log by default was not read.
- **pip and PEP 740:** whether pip verifies attestations at install time was not established (the PyPI page names a separate CLI).
- **DisTrO's algorithm:** the report does not describe it; Psyche's `distro.rs` (named in the DisTrO README) was not read.
- **Psyche run-manager:** absence of image-signature checks rests on a grep of two files.
- **Covenant-72B joiners:** the paper does not say how a joining peer gets the current model.
- **SparseLoCo at 178M (Appendix J)** and **Table 5's per-cell values** (garbled layout) were not used.
- **Prime Intellect code link:** INTELLECT-1's `PrimeIntellect-ai/prime` now hosts a CLI and SDK; that `prime-diloco` is the same framework rests on its description and checkpoint code, not on a statement by Prime Intellect.

## Gaps

- **Home connections:** no primary source in this strand measures update exchange between home machines for 100M to 1B models. Gate-style measurements would have to come from the pilot.
- **Partial-holder checkpoints:** no system found stores a training checkpoint only in pieces across peers; R5's holder rule has no storage precedent in the sources read.
- **Not read:** Psyche's DisTrO implementation; DeMo's OpenReview v2; Pluralis, Gensyn and SWARM storage; PyTorch Distributed Checkpoint documentation; Hugging Face S3-compatible bucket API page; GitHub Additional Product Terms; Cloudflare's terms of service; IPFS pinning services' own terms and free tiers; INTELLECT-3.
- **Not measured:** Xet deduplication savings on successive checkpoints or pseudo-gradients of a training run (the docs claim savings for unchanged regions only).

## Query log

All times local (TST), 2026-10-13.

| Time | Tool or site | Query or action |
|---|---|---|
| 17:18 | n/a | Started; read the brief, `docs/ROADMAP.md`, `docs/SRS.md` §9 (D29 to D38), and `docs/research/2026-10-11-literature-notes/01-local-averaging.md` (A1 to A5, B3, D3) |
| 17:21 | export.arxiv.org API | `id_list` 2411.19870, 2508.15706, 2603.08163, 2501.18512, 2505.23725, 2407.07852, 2412.01152, 2311.08105 (titles and versions; Covenant-72B title confirmed) |
| 17:21 to 17:22 | arxiv.org | PDFs of the eight papers (`sleep 3` between requests); `pdftotext -layout`; versions confirmed from the PDF stamps |
| 17:22 | arxiv.org | HTML of 2411.19870v2 (Table 1) |
| 17:23 | arxiv.org | HTML of 2508.15706v3 (Tables 1 and 7) |
| 17:25 | export.arxiv.org API | `id_list` 2106.10207, 2207.03481, 2505.07291, 2506.21263 |
| 17:25 to 17:26 | arxiv.org | PDFs of 2106.10207, 2207.03481, 2505.07291 (2506.21263 DiLoCoX not downloaded) |
| 17:26 | api.github.com | `repos/NousResearch/DisTrO`, its contents and commits |
| 17:27 | raw.githubusercontent.com | DisTrO README and preliminary report PDF at `24f10628c2` |
| 17:29 | api.github.com | `repos/huggingface/hub-docs` tree; commits per path for 12 files |
| 17:29 | raw.githubusercontent.com | hub-docs files at `ef42b8f945` |
| 17:30 | huggingface.co | `/terms-of-service`, `/content-policy`, `/storage` (HTML, tags stripped) |
| 17:30 | api.github.com, raw | `huggingface/huggingface_hub` guides `upload.md`, `buckets.md` at `a704b8488c` |
| 17:30 to 17:31 | api.github.com, raw | `github/docs` tree; pages, variables and reusables at `d1a0081f24`; commits per path |
| 17:32 | api.github.com, raw | `github/site-policy` tree; acceptable use and terms at `b9578b546d` |
| 17:33 | api.github.com, raw | `bittorrent/bittorrent.org` BEPs 3, 5, 19, 46, 52 at `7b7b41f46d` |
| 17:34 | api.github.com, raw | `webtorrent/webtorrent` repo, latest release, README and FAQ at `bbcd95c0c0` |
| 17:34 | api.github.com, raw | `ipfs/ipfs-docs` tree; three pages at `1261c016f2` |
| 17:35 | api.github.com, raw | `cloudflare/cloudflare-docs` R2 pages at `9a7810d424` |
| 17:36 | api.github.com | `repos` for tplr-ai/templar (redirects to one-covenant/templar), PsycheFoundation/psyche (redirects to nousnet), PrimeIntellect-ai/prime, learning-at-home/hivemind, bigscience-workshop/petals |
| 17:36 | api.github.com, raw | Templar tree; `docs/miner.md`, `docs/validator.md`, `docs/r2_bucket_management.md`, `src/tplr/dcp_checkpoint.py` at `0fefc2ad76` |
| 17:37 | api.github.com, raw | Psyche (nousnet) tree; six psyche-book pages, run-manager README and two source files at `0bdb13d94a` |
| 17:38 | api.github.com | `PrimeIntellect-ai/prime` tree; `orgs/PrimeIntellect-ai/repos` (sorted by push); `prime-diloco` repo and tree |
| 17:38 | raw.githubusercontent.com | `prime-diloco/src/zeroband/checkpoint.py` at `de5b9317da` |
| 17:39 | api.github.com, raw | Hivemind README, `averager.py`, `state_averager.py` (fetched, not read), `compression/__init__.py` at `4bd43b7789`; Petals README and `from_pretrained.py` at `22afba627a` |
| 17:40 | api.github.com, raw | `sigstore/docs` tree; six pages at `b25f111947` |
| 17:41 | api.github.com, raw | `pypi/warehouse` docs tree; five pages at `20c44b5595` |
| 17:42 | pypi.org | JSON API for `hivemind` and `petals`; Integrity API provenance for three files |
| 17:42 | raw.githubusercontent.com, github.com | BOINC wiki raw URLs (404); then `git clone --depth 1` of `BOINC/boinc.wiki.git` (files read only) |
| 17:44 | reproducible-builds.org | `/docs/definition/` (HTML, tags stripped) |
| 17:44 | api.github.com, raw | `huggingface/safetensors` README at `e246a25606` |
| 17:45 | api.github.com, raw | `pytorch/pytorch` `docs/source/notes/serialization.md` at `52976db7b6` (the `.rst` path returned an empty file) |
| 17:47 | n/a | Wrote findings; WebSearch and WebFetch were not used in this strand (all sources were reached through known repositories, APIs and arXiv IDs) |

Not covered: DiLoCoX (2506.21263, metadata only); Psyche's `distro.rs`; DeMo's OpenReview version; Pluralis, Gensyn and SWARM storage; PyTorch Distributed Checkpoint docs; Hugging Face S3 bucket API page; GitHub Additional Product Terms; Cloudflare terms; IPFS pinning-service terms; INTELLECT-3; Hivemind `state_averager.py` (fetched, not read); Templar `r2_bucket_management.md` and `validator.md` beyond a grep.
