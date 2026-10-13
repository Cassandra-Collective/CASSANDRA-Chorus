# W1b: averaging without a server (question 4 and algorithmic churn) · system-study notes

Status: complete draft, 2026-10-13 17:45 TST (skeleton written 17:23).

Strand: question 4 of `docs/research/2026-10-13-system-study-brief.md` (averaging without a server, synchronous and asynchronous), plus the algorithmic side of question 6 (churn), and candidates for Gate N1b (ROADMAP step 3.6).

## Sources

How these notes were made. Every number and quotation below was read in raw text by me: PDFs fetched from arxiv.org with `curl` and converted with `pdftotext -layout`, and, where the PDF was two-column and interleaved, the arXiv HTML of the same version converted to text by a local script (`html.parser`, table rows collapsed onto one line). Each paper is in its own directory under the session scratchpad (`sysstudy/sources/w1b/<id>/`). Version histories come from the arXiv abs pages fetched 2026-10-13. Search tools were used only to discover papers. "Derived" numbers are mine and are labelled (inference) with the arithmetic. Relative gaps in loss are computed as ln(PPL_a)/ln(PPL_b) − 1, the same convention as the Stage 0 notes (01).

Classification of central elements follows the brief: (a) a server we would run; (b) a public static-file host; (c) a public third-party network for live coordination.

Baseline vocabulary used below (from 01, extended for asynchronous papers):

- **same-step DP**: data parallel with global batch M × local batch and the same number of steps (equal compute, equal tokens).
- **more-steps**: M× more sequential steps at the local batch (Stage 0's centralized arm).
- **equal total local steps**: asynchronous runs stopped after the same total number of worker steps as the synchronous run (equal compute and tokens), but not equal wall-clock.
- **iso-FLOPs / iso-tokens**: as the paper states.
- **per wall-clock**: compared at the same elapsed time (unequal compute).

### S1. Decoupled DiLoCo for Resilient Distributed Pre-training

- **Authors:** Douillard, Rush, Donchev, Charles, Fallen, Dubey, Gog, Josef Dean, Woodworth, Garrett, Keating, Bishop, Prior, Yvinec, Szlam, Ranzato, Jeff Dean (17; arXiv abs-page metadata); the paper header reads "Decoupled DiLoCo Team", Google DeepMind and Google Research. 2026. Preprint.
- **arXiv:** 2604.21428. Versions: v1 Thu 23 Apr 2026 08:45:38 UTC only (abs page, fetched 2026-10-13). **Read v1** (PDF and HTML of v1). https://arxiv.org/abs/2604.21428
- **Code:** none linked in the text read.
- **Read status:** sections read: abstract, §1 to §6 (all), Appendix A (related work, DiLoCo and asynchrony paragraphs), B (post-training), D.1 to D.5, E.1 to E.4, F.3 (Table 14), F.4 (Table 15). Not read: Appendix C body beyond Table 7's caption, F.1 to F.2 benchmark descriptions. Stage 0 note 01 (A8) had read abstract, §1, §2 to §3.2, §5.1, §5.4 to §6, D.2, Table 14.
- **What it does (setting and scale):** Gemma 4-based dense models of 2B (26B tokens), 5B (72B tokens; 1T tokens in the failure study) and 9B (141B tokens), and MoE models with 2.8B and 3.8B active parameters (170B and 233B tokens), text and vision data, on TPU clusters inside Google data centres; failures are simulated with event tapes for up to 2.4 million simulated chips (§3.3, §5.1, §5.5, Fig. 7). Pretraining from scratch. One real geo-distributed run: a 12B dense model with M = 8 learners in several US regions, reported only as step time (E.4, Fig. 14).
- **Mechanism.** Asynchronous. M "learners" each run inner AdamW steps on their own shard without waiting for each other. The model is split into P = 24 fragments; each fragment is synchronized every H = 24 steps, overlapped over τ = 2 steps, so one fragment is sent and received every step (§5.1). A **central synchronizer ("syncer")** holds "the global model parameters and outer optimizer state" (§4). For each fragment it waits for a minimum quorum of K learners (K = 1 by default), optionally an "adaptive grace window" to collect more, weights each learner by tokens × (tokens/steps) since its last update, merges the outer gradients (Radial-Directional Averaging on non-embedding parameters, plain averaging on embeddings; App. D.2), applies the outer optimizer (Nesterov SGD), and broadcasts the new fragment (Alg. 2, §3.2). A learner overwrites its fragment with the syncer's (α = 0 in App. D.1 was best at larger M).
  - **Is the syncer a server?** In the paper, yes. The syncer runs "on CPU-only resources, partitioned into M shards", one per learner, and the shards all-reduce among themselves (§4, Fig. 4). The design "naturally leads to a parameter server architecture" (§4). Everything is orchestrated by Pathways (§4). The paper argues for "running the syncer worker on highly stable, CPU-only resources with a minimal failure surface" (§4).
  - **Syncer failure.** The text read covers learner failure only. The syncer checkpoints with a Chandy-Lamport snapshot of "its current model parameters and outer optimizer state" (App. E.2); resuming from a checkpoint is described as "an important fallback strategy in extreme failure scenarios" (E.2). No syncer failover, replication or hand-over is described.
  - **Learner churn.** Offline or straggling learners are excluded from that fragment's merge (weight 0) (§3.2, §4). A learner that is away too long, restarts, or joins for the first time runs "learner recovery": it waits for the syncer's next fragment broadcast stamped with a vector clock, then copies parameters and inner optimizer state from a healthy peer learner, buffering syncer updates during the transfer; recovery is bounded to H syncer steps, so a recovered learner's fragments and optimizer state have "the same bounds as in any other learner" (E.3). The authors write that their asynchrony "never requires updating the model using a stale gradient" computed on an earlier model version (App. A).
  - **Determinism.** Because the quorum depends on timing, the run is nondeterministic; the syncer records an "event tape" (vector clocks, token counters, failures) that allows bitwise replay (E.1).
- **Numbers (all v1).**
  - **Asynchronous against synchronous (the only direct comparison in the paper), Table 5:** 2B dense, 26B tokens, M = 8 learners on two TPU generations (slowest 18% behind fastest, plus 10% injected variance). Downstream text average / vision average / goodput: K = 8 (fully blocking, i.e. synchronous) 54.4 / 37.6 / 84%; K = 1 without grace window 51.4 / 25.7 / 100%; K = 1 with grace window 55.3 / 37.0 / 100%. So the minimal quorum without the grace window costs 3.0 text points and 11.9 vision points; with the window it matches the synchronous run. (Inference: the K = 8 per-task values are identical to the homogeneous M = 8 run in Tables 8, 11 and 12, as expected if a fully blocking run is deterministic regardless of learner speed.)
  - **Against data parallel (equal tokens, "centralized monolithic DP baseline"), downstream text average only:**
    - Table 14 (no failures): 5B DP 62.5 vs Decoupled 62.8; 9B DP 67.8 vs 68.0. The 2B column prints 52.3 vs 51.6, but its own per-task values average to 55.1 vs 54.4 (inference: my arithmetic over the seven text tasks; 55.1 and 54.4 are also what Table 12 prints for the same runs). See "Could not verify".
    - Table 12 (2B, token budget): DP 55.1 / 61.8 / 64.5 vs Decoupled M = 8 54.4 / 62.1 / 64.9 at 26B / 260B / 1.3T tokens. The authors: Decoupled DiLoCo "can be slightly weaker at low token budget" (D.5).
    - Table 2 (5B dense, 1T tokens): DP 70.1 (no failures), 70.1 (150k chips), 69.7 (1.2M chips); Decoupled M = 8 69.8 (no failures), 70.1 (150k), 69.8 (1.2M), with goodput 100/88/58% for DP against 100/98/88% for Decoupled.
    - **MoE, Table 3** (2.8B active, 170B tokens): DP 68.4; Decoupled M = 8 without failures 67.9; with failures (1.2M simulated chips, MTBI 1 year) 68.4. Text averages; no loss column. §5.5: learners "can only optimize this loss locally" (load balancing), yet "with sufficient scale" match DP. The 3.8B-active MoE results are figure-only (Fig. 7b).
  - **Validation-loss numbers (the only loss figures in the paper):**
    - D.3, Table 10 (2B, 26B tokens, heavy simulated failures): compressing outer gradients to int4 changes "relative val loss" by +0.09%; 2 bits +32%; 1 bit +83%, against bf16.
    - F.4, Table 15b (2B, 128B tokens, iso-FLOPs scavenging, base M = 4 rising intermittently to 5, 6, 8 or 16): validation-loss deltas DP +0.02% / −0.04% / −0.02% / +0.07% and Decoupled +0.09% / −0.01% / +0.08% / +0.23% for +25% / +50% / +100% / +300% scavenging. The reference for these deltas is not stated in the text read (presumably each method's +0% run; inference). Train time Decoupled 0.90× / 0.83× / 0.75× / 0.62× against DP 1.07× / 1.09× / 1.02× / 0.80× (Table 4).
  - **Worker count under failures, Table 11** (2B, 26B tokens): text average without failures M = 2 / 4 / 8 / 16: 55.1 / 55.9 / 54.4 / 54.5; with 1.2M simulated chips 54.4 / 55.0 / 55.4 / 53.9 (goodput 70 / 82 / 88 / 93%). "neutral ML performance from M = 2 to M = 8" and "slightly degraded performance at M = 16" (D.4).
  - **Merge rule, Tables 8 and 9** (2B, 26B tokens): with M = 16, text average Avg/Avg 52.7, RDA (model)/Avg (embedding) 54.5; vision 28.2 vs 33.6. With M = 8 the four combinations range from 53.3 to 55.1 in text average, with "no entirely consistent method" (D.2).
  - **Communication:** at a 1 s compute step between 2 data centres, 99% compute utilization needs 195 Gbit/s for DP against 2.2 Gbit/s for Decoupled M = 8 and 0.53 Gbit/s with int4 (Table 13a, 5B model, simulated). A joining learner needs about 3 × N parameters (weights plus two AdamW moments) within H steps to avoid downtime (E.3).
- **Central elements:** the syncer (holds the canonical global fragments and outer momentum): **(a)** if we ran it on a dedicated machine. Pathways orchestration and the data-centre network are Google infrastructure, not applicable to us. No (b) or (c) element.
- **Fit with R1 to R7 (inference):** R1 not met as published (a stable syncer is assumed). R4 met (asynchronous, quorum-based). R5 and R6: not addressed; the fragment mechanism is per parameter subset, not per expert holder group; MoE runs are full-copy (every learner holds every expert). R2 and R3 not addressed (data-centre network).
- **Rotating the syncer (inference, not in the paper):** the syncer's state is the global parameters plus the outer optimizer's momentum, about 2 model copies (for 100M to 300M parameters in fp32, roughly 0.8 to 2.4 GB), plus the event tape and per-learner counters. Nothing in the algorithm requires the syncer to be a different machine from a learner; the paper puts it on separate CPU hosts for failure isolation. A rotating syncer would need (1) a hand-over of that state, (2) agreement among peers on who holds the role, and (3) a rule for what happens to fragments in flight. The paper describes none of these; its only syncer-failure path is restart from a checkpoint. A hand-over through a public file host is conceivable but untested anywhere I read.
- **How its setting differs from ours:** 2B to 12B parameters on TPUs in data centres with many chips per learner; downstream accuracies, not loss, as the quality measure; M = 2 to 16 learners, each itself a large data-parallel job; failures simulated by dropping slices from a learner; learners each hold the full model.
- **Question it raises for us:** with 3 to 5 learners whose step times differ by more than 18%, does K = 1 with a grace window keep its parity with the blocking run, and who holds the syncer state when the machine that held it goes offline?

### S2. Asynchronous Local-SGD Training for Language Modeling

- **Authors:** Bo Liu, Rachita Chhaparia, Arthur Douillard, Satyen Kale, Andrei A. Rusu, Jiajun Shen, Arthur Szlam, Marc'Aurelio Ranzato (Google DeepMind, Google Research, UT Austin). 2024. Preprint (no venue on the arXiv record; 01 found none in OpenAlex).
- **arXiv:** 2401.09135. Versions: v1 Wed 17 Jan 2024 11:17:04 UTC; v2 Mon 23 Sep 2024 10:49:33 UTC. **Read v2** (PDF and HTML of v2). https://arxiv.org/abs/2401.09135
- **Code:** Colab toy example at https://github.com/google-deepmind/asyncdiloco (§6 footnote 4): `license.spdx_id` Apache-2.0, `pushed_at` 2024-01-18T12:25:56Z (`gh api`, queried 2026-10-13 14:36 UTC). Files not read.
- **Read status:** sections read: abstract, §3 (framework), §4 (optimization challenge, baselines, existing fixes), §5 (Delayed Nesterov, Dynamic Local Updates), §6, §7 (Tables 1 to 4), §8 to §10, Appendix 10.1 (Tables 5 and 6). 01 had read §4, §7 and 10.1.
- **What it does:** 20M, 60M and 150M Chinchilla-style decoders on C4, 32,000-token vocabulary, sequence length 256 (Tables 5 and 6). **Not from scratch:** 24,000 steps of ordinary pretraining, then 64,000 steps per worker of asynchronous local SGD (88,000 total), "akin to post Local-SGD" (App. 10.1). 4 to 16 workers with simulated heterogeneous speeds; training time is "faked … based on real-world device statistics" in a deterministic implementation (§3). H = 50 inner steps by default.
- **Mechanism.** Asynchronous, with **a central server**: "we assume a central server controls all workers and asynchronously aggregates their updates" (§3). Each worker trains H steps from the server model it last received, returns its pseudo-gradient, and the server applies it as soon as it arrives (Alg. 2). Supporting pieces: shards sampled in inverse proportion to their progress; a per-shard learning-rate schedule with a positive floor because the end step is unknown; a "grace period" in which a worker finishing just after another is merged into the same server model (§3).
  - **How stale updates are handled.** The paper diagnoses the problem as momentum, not staleness alone: applying the M simultaneous pseudo-gradients one at a time through Nesterov momentum gives "a more rapidly decaying momentum term" but "amplifies the actual change in parameter" (§4, Eq. 5), and asynchronous DiLoCo lags synchronous DiLoCo even with identical device speeds (Fig. 7). Tested fixes from the asynchronous-SGD literature: polynomial down-weighting (1 + staleness)^−0.5, a staleness threshold of 10, delay compensation, and a FedBuff-style buffer. Poly, PolyThres and delay compensation "barely improve"; the buffer "significantly closes the gap" but is unstable early (Fig. 8 caption). None matched synchronous DiLoCo (§4).
  - **Proposed fix 1, Delayed Nesterov (DN):** buffer N incoming pseudo-gradients; apply plain gradient steps (g/N) on each arrival and update the momentum only once every N arrivals (Alg. 3; c = 0 default, Table 4 shows c = 0.1 no better).
  - **Proposed fix 2, Dynamic Local Updates (DyLU):** give each worker H × (its speed ÷ the fastest speed) local steps so that results arrive together (Eq. 6).
  - Inner AdamW state is kept locally "without reset" between rounds and not communicated (App. 10.1).
- **Numbers (v2), final perplexity; all runs at equal total local steps (equal compute and tokens), not equal wall-clock:**
  - Table 3 (4 workers; the heterogeneity level is not stated for Table 3, but its 20M values equal Table 1's "very" column, so I take it to be "very", inference): DiLoCo (synchronous) 41.35 / 24.55 / 17.23; Async DiLoCo 44.27 / 25.64 / 18.08; Async DN + DyLU 41.13 / 24.53 / 17.26; single worker at 4× batch 42.47 / 24.80 / 17.47 (20M / 60M / 150M).
    - (inference) Naive async against sync: +1.83% / +1.36% / +1.69% in loss. DN + DyLU against sync: −0.14% / −0.03% / +0.06%. DN + DyLU against the same-step large-batch baseline: −0.86% / −0.34% / −0.42%. The authors: the sync-async disparity "does not diminish even as the model size increases" (§7).
  - Table 1 (20M, 4 workers, heterogeneity none / slight / moderate / very): Async DiLoCo 44.27 / 44.38 / 44.29 / 44.27; DN + DyLU 41.27 / 41.27 / 41.09 / 41.13; DiLoCo 41.35 throughout. With no heterogeneity DN + DyLU and DiLoCo "reduce to the same" algorithm; the 0.08 difference is "numerical error" (footnote 5).
  - Table 2 (20M, 4 / 8 / 16 workers): DN + DyLU 41.13 / 41.02 / 40.98; DiLoCo 41.35 / 41.23 / 41.25; single worker at k× batch 42.47 / 41.28 / 40.60. (inference) At 16 workers the same-step large-batch baseline is 0.25% better than DN + DyLU in loss.
  - Wall-clock: DN + DyLU "outperforms in terms of time efficiency" (§7; Fig. 2, figure only). No wall-clock number in the text read.
  - **No centralized (more-steps) baseline** and no from-scratch run.
- **Communication:** one full pseudo-gradient up and one model down per worker per round (inference from Alg. 2); no compression.
- **Central elements:** the server holding the global parameters, the outer momentum and the DN buffer: **(a)** if we ran it. No (b) or (c).
- **Fit with R1 to R7 (inference):** R1 not met as published. R4 met. R5/R6 not addressed (full-copy only). DN's state (model + momentum + buffer of up to N pseudo-gradients, or their running sum) is what a rotating holder would have to hand over.
- **How its setting differs from ours:** continues from a pretrained checkpoint; simulated speeds; 20M to 150M BPE models; 4 to 16 workers; final perplexity on C4.
- **Question it raises for us:** DyLU needs each peer's speed in advance or measured; with home GPUs whose speed changes (other use, power), does DN alone carry the result?

### S3. Moshpit SGD: Communication-Efficient Decentralized Training on Heterogeneous Unreliable Devices

- **Authors:** Max Ryabinin, Eduard Gorbunov, Vsevolod Plokhotnyuk, Gennady Pekhimenko. 2021. NeurIPS 2021 (arXiv comment "Accepted to Conference on Neural Information Processing Systems (NeurIPS) 2021").
- **arXiv:** 2103.03239. Versions: v1 Thu 4 Mar 2021; v2 Mon 8 Nov 2021; v3 Thu 2 Dec 2021; v4 Tue 11 Jan 2022. **Read v4** (HTML of v4; PDF fetched). https://arxiv.org/abs/2103.03239
- **Code:** https://github.com/yandex-research/moshpit-sgd: `license.spdx_id` Apache-2.0, `pushed_at` 2025-02-04T14:21:21Z (`gh api`, queried 2026-10-13 14:36 UTC). Hivemind implements decentralized averaging and is what DeDLOC used (DeDLOC §4.1); whether Hivemind's averager is exactly Moshpit All-Reduce was not checked in code here.
- **Read status:** sections read: abstract, §2.3 to §2.4, §3.1 to §3.3 (theorem statements and assumptions; proofs not read), §4.1 to §4.3, Appendix B.4, B.5, E (first part), F, G (first part), H.2. Not read: proofs (C, D), I, J.
- **What it does:** a group all-reduce for unreliable peers. Peers form a virtual d-dimensional grid with M peers per row; in each round, each peer averages with the peers that share its group key, and the key is built from the chunk indices of the previous d − 1 rounds so that two peers grouped together in round t "must choose different groups in round t+1" (§3.1). With N = M^d peers and no failures it gives the exact average in d rounds (Torus All-Reduce, §3.1). Groups are found through a Kademlia DHT key per group (Alg. 1) with a leader-follower matchmaking protocol that guarantees groupmates agree on the member list (App. E).
- **Mechanism with respect to a server:** no server in the averaging path. "a fully decentralized averaging protocol" (§3). Moshpit SGD is local SGD with periodic Moshpit averaging; the authors place it in the asynchronous family "because the averaging steps happen in smaller groups" that can be interleaved with local updates (B.4). A joining peer downloads "the latest parameters from a random up-to-date peer discovered through DHT", including optimizer statistics and the learning-rate schedule (App. F).
- **Churn:** a peer that fails during all-reduce causes "its groupmates to skip a round of averaging" (§3.1). Correctness theorem: if every worker has a non-zero probability of completing a round, all local vectors converge to the global average with probability 1, because averaging within any subset preserves the global mean (Theorem 3.1). The optimization theorems (3.3, 3.4) allow peers to vanish (P_{k+1} ⊆ P_k, at least N_min remain) and recover local-SGD rates under conditions on how much vanishing moves the average (Assumption 3.2). Note: the theory lets peers leave but not join.
- **Numbers (v4):**
  - Averaging (§4.1, Fig. 3, figure only): with failure probability p ≥ 0.005 per peer per round, plain all-reduce needs "prohibitively high" retries; gossip and PushSum need "significantly more iterations" than Moshpit (512 to 1024 scalar peers, groups of 32).
  - ResNet-50 on ImageNet (§4.2): with 64 heterogeneous servers over 1 Gb/s links within 300 km, Moshpit's advantage over SGP is "over 30%" in time; all-reduce SGD's time is "1.5×" Moshpit's; AD-PSGD "achieves lower accuracy even after training for 150 epochs" (Fig. 4, figure only).
  - **ALBERT-large (18M parameters) masked-LM pretraining on BookCorpus** (§4.3): 66 preemptible GPUs on 3 continents (100 to 1500 Mb/s per worker) against one 8×V100 instance; global batch 4096, LAMB; after each 4096 accumulated samples the swarm runs 2 rounds of Moshpit All-Reduce with M = 8, d = 2. Plain parameter averaging "does not converge", so workers recover "pseudo-gradients" after averaging to update LAMB statistics. Result: "trains 1.5 times faster", and the final losses of the two runs are "the same within the margin of error" (§4.3; Fig. 4 right, figure only, no number in the text). Baseline: same global batch, different hardware; a wall-clock comparison.
- **Communication:** per round O(max(s, M) × (M − 1)/M) per peer for a vector of size s with butterfly all-reduce, plus O(log N) DHT requests (Eq. 4); the authors contrast this with gossip, where "network load grows linearly with the number of neighbors" (§3.1). Load balancing by linear programming for uneven bandwidth (App. G).
- **Central elements:** none in the algorithm. The DHT needs reachable bootstrap peers (handled in other strands); in the experiments the peers were cloud and marketplace machines. Classification: if the DHT runs only among our machines, no (a), (b) or (c); a public DHT would be (c).
- **Fit with R1 to R7 (inference):** R1 and R3 compatible in the algorithm (no server; relays not part of the averaging). R4: it is group averaging. R5/R6: averaging any parameter vector within any group is compatible with averaging an expert only among its holders (a group = the holders); the paper does not do this.
- **How its setting differs from ours:** tens of peers; ALBERT-large's shared weights (18M) keep messages small; synchronous large-batch steps between averaging rounds in the ALBERT run, not H-step local training.
- **Question it raises for us:** with 3 to 5 peers, a Moshpit grid degenerates to one group (d = 1); does it then reduce to all-reduce with a retry or skip rule, and is that what we want?

### S4. Distributed Deep Learning in Open Collaborations (DeDLOC)

- **Authors:** Michael Diskin, Alexey Bukhtiyarov, Max Ryabinin, Lucile Saulnier, Quentin Lhoest, Anton Sinitsin, Dmitry Popov, Dmitry Pyrkin, Maxim Kashirin, Alexander Borzunov, Albert Villanova del Moral, Denis Mazur, Ilia Kobelev, Yacine Jernite, Thomas Wolf, Gennady Pekhimenko (arXiv abs-page metadata). 2021. NeurIPS 2021 (arXiv comment).
- **arXiv:** 2106.10207. Versions: v1 Fri 18 Jun 2021; v2 Mon 8 Nov 2021. **Read v2** (HTML of v2; PDF fetched). https://arxiv.org/abs/2106.10207
- **Code:** built on Hivemind (§4.1). https://github.com/yandex-research/DeDLOC: `license.spdx_id` Apache-2.0, `pushed_at` 2022-01-13T19:25:30Z (`gh api repos/yandex-research/DeDLOC`, queried 2026-10-13 14:36 UTC). Hivemind: MIT, `pushed_at` 2026-01-11T21:13:45Z (same query time).
- **Read status:** sections read: §3.1 to §3.3, §4.1 to §4.3, Appendix C, D, E, I.6. Not read: §1 to §2, B, F to H, I.1 to I.5, I.7 to I.8, J.
- **What it does:** **synchronous** large-batch data-parallel training among volunteers. "DeDLOC follows synchronous data-parallel training with fixed hyperparameters regardless of the number of collaborators"; each device accumulates gradients until the collaboration reaches the target batch, then all exchange gradients and take one optimizer step, making it "mathematically equivalent to large-batch training" (§3.1). Delayed parameter updates overlap communication with computation "at the cost of exactly one round of staleness" (§3.2). A linear program assigns each peer to compute, aggregate or both (§3.2).
- **Server?** No server in the averaging path, but "DeDLOC requires a few peers with stable internet access" ("backbone" peers) that welcome newcomers, store checkpoints and track learning curves; "at least one of them is available at all times" (§3.3). Training data were streamed "from a dedicated storage service" (§3.3). The real run used an allowlist authentication system (§3.3, I.5 not read).
- **Churn:** a peer that missed a step sees others ahead and downloads "the latest parameters and optimizer statistics from one of the up-to-date peers" (§3.3). Node failures: with several hundred volunteers "most training iterations will have at least one participant with network issues", so global averaging is replaced by Moshpit-style group all-reduce with group size m chosen from failure rates (§3.2, App. C); in all their experiments "the optimal group size was m = n" (App. C).
- **Numbers (v2):**
  - sahajBERT (ALBERT-large, Bengali; 40 volunteers, 91 devices, 15 to 35 active at a time, plus 16 preemptible cloud T4s): converged after 8 days, "1.8x as fast as regular distributed training with 8 V100 GPUs"; "the stepwise learning curves of the two runs were virtually identical" (§4.3; App. I.6, Fig. 10, figure only). Average traffic 6.95 GB per volunteer device per hour (§4.3). Downstream: Wikiann F1 95.45 ± 0.53, NCC accuracy 91.97 ± 0.47 against XLM-R 96.48 / 90.05 (Table 2).
  - ALBERT-large on WikiText-103, 16 T4 workers: low-bandwidth peers (50 to 200 Mb/s) give "≈2.5x slowdown"; load balancing +47%; adding 8 part-time peers reaches 74% of the 25 Gb/s setup's speed (§4.2; figures only).
- **Central elements:** backbone peers that must keep at least one online (**(a)** if we had to run one around the clock; under R2, our own intermittently online machines would not satisfy "at least one at all times" without luck); a dedicated data storage service (**(b)** if a public file host); public libp2p peers act as STUN and relay nodes: "There are no dedicated STUN and TURN servers" in libp2p, and public participants play that role (App. E); that is (c) if a public libp2p network were used, and our own machines otherwise.
- **Fit with R1 to R7 (inference):** R1 partly (no server in averaging; backbone availability requirement). R4: it is synchronous; churn handled by group all-reduce. R5/R6 not addressed.
- **How its setting differs from ours:** synchronous large-batch SGD (no local steps), ALBERT's parameter sharing keeps messages small, tens of volunteers.
- **Question it raises for us:** DeDLOC equates the run to one large-batch job; Chorus's full-copy work unit is H-step local training. Which of the two should the synchronous mode be (D38 says Stage 0's rounds, i.e. local training)?

### S5. SWARM Parallelism: Training Large Models Can Be Surprisingly Communication-Efficient

- **Authors:** Max Ryabinin, Tim Dettmers, Michael Diskin, Alexander Borzunov. 2023. ICML 2023 (arXiv comment).
- **arXiv:** 2301.11913. Versions: v1 Fri 27 Jan 2023; v2 Thu 29 Jun 2023. **Read v2** (HTML). https://arxiv.org/abs/2301.11913
- **Code:** https://github.com/yandex-research/swarm: no licence detected (`license` null), `pushed_at` 2023-12-11T04:02:57Z (`gh api`, queried 2026-10-13 14:36 UTC).
- **Read status:** sections read: §3.2, §4.3, Appendix E. Not read: §1 to §3.1, §4.1 to §4.2, §4.4, other appendices (Appendix A on fault tolerance is referenced but not read).
- **What it does:** pipeline (model) parallelism over unreliable peers. "Peers within one swarm serve the same pipeline stage", i.e. the same layers and parameters (§3.2). Trainers route each micro-batch through any peer of each stage, choosing by measured throughput (stochastic wiring); peers switch stages to rebalance (§3.2).
- **How peers of the same stage average:** once enough gradients are accumulated, peers form groups, "run All-Reduce to average gradients within their pipeline stages" and take the optimizer step (§3.2). The step is **synchronous**: SWARM "still performs optimizer steps synchronously after peers collectively reach the required global batch size"; delayed parameter updates (DPU) are the only deviation (App. E). This is per-step gradient averaging within the stage group, not H-step local training.
- **Churn:** a peer that fails or misses the step "is considered a straggler" and "must reload its state from neighbors" before resuming (App. E). A new or switching peer downloads the latest stage parameters and optimizer statistics from the stage's peers; training proceeds "as long as there is at least one active participant per stage" (§3.2). A trainer that gets no answer bans the peer until it re-announces itself in the DHT (§3.2).
- **Numbers (v2):** 1.01B-parameter model with layer sharing (3 stages; compute-equivalent to a 13B model) on 400 preemptible T4s against data parallel on 128 A100s for about 4 weeks: "the training dynamics of two approaches are indeed similar" (§4.3, Fig. 4, figure only; no number). Throughput with layer sharing: T4 17.6 samples/s actual against 19.2 best-case; optimal bandwidth per intermediate-stage node 317.8 Mb/s up, 397.9 Mb/s down for T4 (Table 3).
- **Central elements:** the DHT (stage membership); classification depends on who runs it (own machines: none of (a), (b), (c)).
- **Fit (inference):** the closest systems precedent for averaging a part of the model only among the peers that hold it, with the R5-like condition "at least one active participant per stage". But averaging is synchronous per step (DeDLOC-style), not asynchronous local training.
- **Differences from ours:** pipeline stages, not experts; per-step synchronous gradient averaging; 400 peers.
- **Question it raises for us:** SWARM survives with one peer per stage because the state is reloaded from surviving stage peers; our R5 asks for 2 holders per expert per round. Is the 2-holder rule for averaging quality, or for not losing the expert's state (SWARM's reason)?

### S6. Can Decentralized Algorithms Outperform Centralized Algorithms? A Case Study for Decentralized Parallel Stochastic Gradient Descent (D-PSGD)

- **Authors:** Xiangru Lian, Ce Zhang, Huan Zhang, Cho-Jui Hsieh, Wei Zhang, Ji Liu. 2017. Venue: not stated on the arXiv record or in the PDF text read (see "Could not verify").
- **arXiv:** 1705.09056. Versions: v1 25 May 2017; v2 26 May 2017; v3 10 Jun 2017; v4 21 Jul 2017; v5 Mon 11 Sep 2017. **Read v5** (PDF). https://arxiv.org/abs/1705.09056
- **Read status:** sections read: abstract, §1 (Table 1), §3 (Algorithm 1, assumptions), §4 discussion of the rate and ring topology, §5.1 opening. Proofs and figures not read.
- **Mechanism:** each node takes a stochastic gradient step and averages its parameters with its neighbours through a symmetric doubly stochastic matrix W (Algorithm 1, §3). **Synchronous**: "The D-PSGD algorithm is a synchronous parallel algorithm" (§3), with nodes usually synchronized by a clock. No server. Per-step communication.
- **Numbers / theory (v5):** the convergence rate matches centralized mini-batch SGD with batch n; communication on the busiest node is O(degree of the graph) against O(n) for a parameter server, "O(1) in the special case of a ring" (§4, Table 1). Spectral gap of W enters the bound (§4). Experiments: CIFAR-10 ResNets and a speech CNN up to 112 GPUs; "D-PSGD can be up to one order of magnitude faster" on low-bandwidth or high-latency networks (abstract). NLP results are "in the supplementary material" (§5.1), not read. **No language-model numbers read.**
- **Churn:** the analysis assumes a fixed graph and synchronous steps; churn not treated in the parts read.
- **Central elements:** none.
- **Fit with R1 to R7 (inference):** R1 met (no server); R4 not met as such (synchronous per step); R5/R6 not addressed.
- **How its setting differs from ours:** per-step gradient-and-mix, not H-step local training; vision and speech experiments; data-centre GPUs.
- **Question it raises for us:** with 3 to 5 peers the graph is nearly complete, so D-PSGD's advantage over all-reduce (busiest-node traffic) largely disappears (inference).

### S7. Asynchronous Decentralized Parallel Stochastic Gradient Descent (AD-PSGD)

- **Authors:** Xiangru Lian, Wei Zhang, Ce Zhang, Ji Liu. 2017. Venue: not stated on the arXiv record or in the PDF text read (see "Could not verify").
- **arXiv:** 1710.06952. Versions: v1 18 Oct 2017; v2 11 Feb 2018; v3 Tue 25 Sep 2018. **Read v3** (PDF). https://arxiv.org/abs/1710.06952
- **Read status:** sections read: abstract, §1 opening, §3.2 to §3.3 (algorithm, deadlock avoidance, topology), §4 assumptions, §5 robustness paragraphs. Proofs and most figures not read.
- **Mechanism:** **asynchronous, no server.** Each worker computes a gradient, then averages its model with one randomly selected neighbour ("both models on both workers are updated to the averaged model"), with no global synchronization (§3.2). Deadlock avoided by a bipartite active/passive graph (§3.3.1). Assumptions include doubly stochastic averaging, a spectral gap, and bounded staleness T (§4, Assumption 1, items 2, 3, 7).
- **Numbers (v3):** ResNet-50 on ImageNet with up to 128 GPUs "converges (w.r.t epochs) similarly to the AllReduce-SGD", with epochs "up to 4-8×" faster in a shared HPC network (abstract); on 64 GPUs AD-PSGD 264 s per epoch against over 1000 s for AllReduce-SGD and D-PSGD (§5). One of 16 workers slowed 2× to 100× (CIFAR-10 ResNet-20): AD-PSGD "converges faster than AllReduce-SGD and D-PSGD by orders of magnitude" with one very slow worker (§5, Fig. 6, figure only). **Vision only; no language-model numbers.**
- **Disagreement:** Moshpit SGD (S3, §4.2) reports that AD-PSGD "achieves lower accuracy even after training for 150 epochs" in its heterogeneous ImageNet setup, against AD-PSGD's own epoch-wise parity with all-reduce.
- **Central elements:** none.
- **Fit with R1 to R7 (inference):** R1 and R4 met by the algorithm (no server, no global barrier); R5/R6 not addressed.
- **How its setting differs from ours:** per-step averaging; vision only; up to 128 GPUs in an HPC network.
- **Question it raises for us:** AD-PSGD's pairwise asynchronous averaging is the per-step ancestor of NoLoCo's pairwise outer step; does pairwise averaging at H-step granularity inherit its straggler tolerance?

### S8. NoLoCo: No-all-reduce Low Communication Training Method for Large Models

- **Authors:** Jari Kolehmainen, Nikolay Blagoev, Semih Kara, John Donaghy, Christopher Nies, Oğuzhan Ersoy (Gensyn). 2025. Preprint.
- **arXiv:** 2506.10911. Versions: v1 Thu 12 Jun 2025; v2 Tue 8 Sep 2026 11:26:53 UTC. **Read v2** (HTML of v2; PDF fetched). https://arxiv.org/abs/2506.10911
- **Code:** https://github.com/gensyn-ai/noloco: `license.spdx_id` MIT, `pushed_at` 2026-03-26T16:07:37Z (`gh api`, queried 2026-10-13 14:36 UTC). Files not read.
- **Read status:** sections read: abstract, §1 to §6, Appendix A, B, C, G. Not read: D, E (proofs), F.
- **Mechanism:** DiLoCo-style inner steps, but the outer step averages only within a random subgroup of n workers (n = 2 in the experiments), re-sampled every outer step, with a modified Nesterov momentum that adds a term pulling each worker towards its subgroup's mean slow weights (Eq. 2). Combined with random pipeline routing between replicas of adjacent stages (§3.1). "does not require any collective communication" (abstract). Pairs still block on each other, but not on the whole group (inference from §3.2 and App. C). Random routing uses a shared `seed` in Algorithm 1 (App. A); how the outer pairs are drawn is described only as "randomly chosen" (§3.2).
- **Numbers (v2), final validation perplexity, FSDP at the model's global batch and 25,000 optimizer steps (App. B, Table 3); DiLoCo H = 100 with outer momentum 0.3, NoLoCo H = 50 (§4.1):**
  - Table 1 (Reddit / C4), e.g. small 125M, DP 8, PP 1: FSDP 25.5 / 29.1, DiLoCo 27.6 / 35.4, NoLoCo 27.3 / 34.5; medium 1.3B, DP 8, PP 2: FSDP 19.6 / 18.8, DiLoCo 21.0 / 21.8, NoLoCo 20.5 / 21.1; large 6.8B, DP 16, PP 4: FSDP 16.1 / 15.7, DiLoCo 18.0 / 17.3, NoLoCo 17.5 / 16.6.
  - (inference) In log-PPL, NoLoCo is 0.16% to 1.45% better than DiLoCo in 14 of 16 cells and 0.27% / 0.42% worse in two C4 medium cells; against FSDP it is +0.83% to +7.68% (125M, C4, DP 16 is the worst: +7.68%).
  - The authors: both methods are "typically few percent worse" than FSDP, "in some cases even 30%" (§4.2; the 30% is in PPL: 37.7 or 39.1 against 29.1).
  - Wall-clock (Table 2, 1.3B, 32 GPUs, pure DP, H = 100, throttled links): seconds per inner step at 100 Mb/s: FSDP 5368.41, DiLoCo 61.80, NoLoCo 15.26; at 1 Gb/s: 548.97 / 6.55 / 2.80.
  - Group size (Fig. 7, 125M, figure only): perplexity "improves as n grows, but the effect is weak" (§5).
- **Communication:** per outer step, each worker sends its outer gradient and slow weights to n − 1 partners; "NoLoCo's per-byte volume is essentially the same as DiLoCo" (App. C). Speed-up comes from removing the global barrier.
- **Churn:** no churn experiment. App. G simulates log-normal message times and asynchronous arrival for up to 1024 workers (Fig. 5, figure only).
- **Disagreement (important):** Factored Gossip DiLoCo (S9, App. B.1) reimplemented NoLoCo without pipeline randomization at 1.5B: with DiLoCo hyperparameters it "diverged after approximately 5k steps"; with NoLoCo's own hyperparameters it reached 22.65 against DiLoCo 18.65 (Table 4 of S9), and they attribute the gap to NoLoCo's outer step lacking Nesterov's look-ahead (not confirmed experimentally by them).
- **Central elements:** none in the algorithm. Experiments on H100 clusters with NVLink and throttled NICs (App. B).
- **Fit (inference):** R1 met by the algorithm; R4 met (group averaging, no barrier). Uses a shared seed for routing, compatible with Chorus's seed-derived assignment.
- **Differences from ours:** pipeline parallelism with random routing is part of the method; 125M to 6.8B; 8 to 64 GPUs in one cluster.
- **Question it raises for us:** without pipeline routing (our full-copy work unit has none), does NoLoCo's outer step remain stable? S9 says it did not at 1.5B.

### S9. Factored Gossip DiLoCo: Reducing Blocking Communication in DiLoCo

- **Authors:** Chamin Hewa Koneputugodage, Thalaiyasingam Ajanthan, Sameera Ramasinghe, Hadi Mohaghegh Dolatabadi, Shamane Siriwardhana, Gil Avraham, Violetta Shevchenko, Karol Pajak, James Snewin, Alexander Long (Pluralis Research). 2026. "Accepted at ICML 2026" (arXiv comment; not checked further).
- **arXiv:** 2606.22768. Versions: v1 Mon 22 Jun 2026 only. **Read v1** (HTML). https://arxiv.org/abs/2606.22768
- **Code:** none of the authors' own linked in the text read (the HTML links PluralisResearch/node0, hivemind and torchft, which were not checked to be this paper's code).
- **Read status:** sections read: abstract, §4.1 to §4.4, §5.1 to §5.3, §6, §7, Appendix A (Algorithm 1, Table 2), B.1, B.2, C. 01 (A9) had read §4.1 setup, §5, §6, appendix optimizers. Not read: §1 to §3, D, E (proof).
- **Mechanism:** splits DiLoCo's synchronization into a **non-blocking** parameter mix (Mix1) that overlaps the next H inner steps "with no staleness", and a **blocking** mix of outer gradients (Mix2) (§4.1). Configurations: DiLoCo (Mix2 global all-reduce), LocalM1M2 (pairwise gossip for both; "very similar to NoLoCo"), GlobalM1 (global all-reduce for Mix1, no Mix2), GlobalM1LocalM2, and a subset variant (§4.1, Table 2). Pairwise gossip is "one round of random-matching pairwise averaging" (Table 2); who draws the matching is not stated.
- **Numbers (v1), Table 1, 1.5B Llama 3, FineWeb, M = 8 single-A100 workers, global batch 512 × 1024 tokens (per worker GBS/M), Sync DP at the same global batch; validation perplexity at 10B tokens (and 30B):**
  - Sync DP 17.53 (14.85); DiLoCo 18.65 (15.52); LocalM1M2 19.37 (15.83); GlobalM1 19.42 (15.91); GlobalM1LocalM2 18.80 (15.60).
  - (inference) Against Sync DP in log-PPL at 10B: DiLoCo +2.16%, LocalM1M2 (pure pairwise gossip) +3.49%, GlobalM1 +3.58%, GlobalM1LocalM2 +2.44%. Against DiLoCo: +1.29%, +1.38%, +0.27%. At 30B: DiLoCo +1.64%, LocalM1M2 +2.37% against Sync DP.
  - M = 16, GBS 512: Sync DP 17.22, DiLoCo 19.99, LocalM1M2 22.24 (inference: +5.24% and +8.99% against Sync DP); the gap between non-blocking and blocking methods "slightly widening" (§6).
  - Compute utilization (simulated, Table 1): at 100 / 200 Mb/s, DiLoCo 36% / 53%, LocalM1M2 49% / 66%, GlobalM1 56% / 100%.
  - Failures: only in the utilization simulator, "a 5% communication failure rate"; all-reduce "must restart while mixing can proceed with effectively weaker mixing"; "LocalM1M2 is unaffected since it avoids all-reduce entirely" (§5.2). No training run with failures.
  - App. B.2: Streaming DiLoCo's overlap alone (5 steps) diverged in their setting after about 900 steps (DiLoCo hyperparameters) or 500 steps (Streaming hyperparameters).
- **Central elements:** none for LocalM1M2 (pairs); GlobalM1 needs a global all-reduce (no server, but every worker must join it).
- **Fit (inference):** the only 2026 paper with a pure pairwise-gossip DiLoCo arm, a DiLoCo arm and a same-batch DP arm in one table at about 1B, aimed at single-GPU workers on consumer networks of roughly 50 Mb/s to 1 Gb/s (§5, paraphrased). But the bandwidth is simulated, workers are homogeneous A100s, and churn is not trained through.
- **Differences from ours:** 1.5B dense; 8 or 16 workers; no stragglers in the training runs.
- **Question it raises for us:** at 3 to 5 peers, pairwise gossip mixes slowly relative to a 4-way all-reduce only if pairs are disjoint; does a single pair per round leave too much disagreement at H = 125 (they found consensus error grows with M and H)?

### S10. Unifying Local Communications and Local Updates for LLM Pretraining (GASLoC)

- **Authors:** Pietro Cagnasso, Eugene Belilovsky, Edouard Oyallon. 2026. Preprint (38 pages).
- **arXiv:** 2606.11081. Versions: v1 Tue 9 Jun 2026 only. **Read v1** (HTML). https://arxiv.org/abs/2606.11081
- **Code:** no repository link found in the HTML.
- **Read status:** sections read: abstract, §3.2 (randomized peer communication, heterogeneity, fault tolerance), §3.3 (Proposition 2 statement), §4.1 to §4.3, §5. Not read: §1, §2, §3.1, appendices.
- **Mechanism:** decentralized local-SGD with an outer Nesterov step over a sparse random graph: "1-Peer" (disjoint random pairs) or "2-Peer" (random ring), a new permutation each round; complete graph recovers DiLoCo (§3.2, §5). Workers may take different numbers of local steps H_i to equalize round times (§3.2). "there is no global synchronizer"; resilience comes from sparse peer-to-peer dependencies, "assuming failed exchanges can be skipped or rescheduled" (§3.2); not tested.
- **Numbers (v1), validation loss, global batch 2M tokens split over n workers, H = 30, Chinchilla token budgets:**
  - 134M on 2.68B tokens (Table 1b): DiLoCo 3.30 / 3.40 / 3.53 for 8 / 16 / 32 replicas; GASLoC-2-Peer 3.32 / 3.45 / 3.62; GASLoC-1-Peer 3.34 / 3.49 / 3.66; AdamW DDP 3.18 (Table 1a).
    - (inference) 2-Peer against DiLoCo: +0.61% / +1.47% / +2.55% in loss; 1-Peer +1.21% / +2.65% / +3.68%. DiLoCo against DDP: +3.77% / +6.92% / +11.01%.
  - 551M on 11.02B tokens (Table 3): DiLoCo 2.64 / 2.67 (8 / 16 replicas); 2-Peer 2.64 / 2.72; 1-Peer 2.67 / 2.81; DDP 2.64 (Table 2, 16 replicas, one-step table).
  - Heterogeneous bandwidth (Fig. 3, 134M, 8 A100s, one worker at 10% or 20% bandwidth; figure only): "a significant wall-clock time advantage can be obtained over DiLoCo" (§4.2).
  - H sweep (Fig. 4, figure only): for H > 5, sparse variants "slightly underperform DiLoCo … but have similar scaling properties" (§4.3).
- **Central elements:** none.
- **Fit (inference):** no server; varying H_i per worker is a direct analogue of Async Local-SGD's DyLU without a server. Fault tolerance is argued, not measured. R5/R6 not addressed.
- **How its setting differs from ours:** dense 134M and 551M BPE models; 8 to 32 A100 workers; bandwidth heterogeneity simulated by throttling.
- **Question it raises for us:** with 4 peers, 1-Peer means 2 pairs per round; does the 8-replica gap (+1.2% for 1-Peer at 134M) shrink at 4?

### S11. HeLoCo: Efficient asynchronous low-communication training under data and device heterogeneity

- **Authors:** Abdullah Al Asif, Patrick Diem, Juan Pablo Muñoz, Felix Wolf, Ali Jannesari, Arya Mazaheri (Iowa State University; Technical University of Darmstadt; Maro Systems; PanocularAI). 2026. Preprint.
- **arXiv:** 2606.00271. Versions: v1 Fri 29 May 2026 only. **Read v1** (HTML). https://arxiv.org/abs/2606.00271
- **Code:** none linked in the HTML.
- **Read status:** sections read: abstract, §3, §4.1, §4.2 (Table 1), §5. Not read: §1, §2, appendices.
- **Mechanism:** asynchronous DiLoCo with **a central synchronizer** that holds the global model and outer momentum (§3). Two corrections: (1) workers start from a look-ahead model θ − η·μ·m; (2) when a stale pseudo-gradient arrives, each tensor block is compared with the current momentum direction (cosine c_b) and blocks that conflict are attenuated or re-oriented (Eqs. 7 to 15). Extra cost O(d) per arrival at the synchronizer (§3).
- **Numbers (v1), Table 1:** 15M-parameter "TinyGPT", 5 workers, non-IID multilingual C4 (one language per worker), 300 outer steps × 80 inner steps (24k steps); worker speeds drawn from {1, 2, 6, 15} s per step; validation loss at a fixed token budget, synchronous Nesterov DiLoCo = 6.62 in every row (one run).
  - Homogeneous (1,1,1,1,1): HeLoCo 6.50, async MLA 6.63, async Nesterov 7.03.
  - Mild (1,1,1,1,2): 6.61 / 6.69 / 7.05. Severe (1,15,15,15,15): 7.64 / 7.78 / 7.81, i.e. 15.39% worse than synchronous at equal tokens; at equal wall-clock the synchronous run is 0.26% better.
  - "Asynchronous Nesterov exhibits unstable behavior and diverges across all configurations" (§4.2).
  - The abstract's "up to 7.5%" against asynchronous baselines and "up to 22.1%" against synchronous match single table cells (7.50 ΔAN in the homogeneous row; 22.07 TΔSN in the (1,1,1,1,15) row at equal wall-clock), not a token-budget comparison with the synchronous run.
  - Losses near 6.5 nats mean the model is far from converged (inference); the authors: "it does not yet capture the scale of practical low-communication LLM training" (§5).
- **Central elements:** the synchronizer: **(a)** if we ran it.
- **Fit with R1 to R7 (inference):** R1 not met as published; R4 met; R5/R6 not addressed.
- **How its setting differs from ours:** 15M model far from convergence; one language per worker (non-IID); simulated speeds.
- **Question it raises for us:** the correction needs the current outer momentum at the moment a stale update arrives, i.e. a single holder of the global state; how would that survive the holder going offline?

### S12. HALoS: Hierarchical Asynchronous Local SGD over Slow Networks for Geo-Distributed Large Language Model Training

- **Authors:** Geon-Woo Kim, Junbo Li, Shashidhar Gandham, Omar Baldonado, Adithya Gangidi, Pavan Balaji, Zhangyang Wang, Aditya Akella. 2025. Venue not confirmed at source: the HTML keyword line reads "Machine Learning, ICML"; a search result points to PMLR v267, not opened (see "Could not verify").
- **arXiv:** 2506.04531. Versions: v1 Thu 5 Jun 2025 only. **Read v1** (HTML). https://arxiv.org/abs/2506.04531
- **Code:** https://github.com/utnslab/HALoS: no licence detected, `pushed_at` 2025-06-05T04:54:22Z (`gh api repos/utnslab/HALoS`, queried 2026-10-13 14:36 UTC).
- **Read status:** sections read: abstract, §4.1, §5 (all). Not read: §1 to §3, §4.2 proofs, appendices.
- **Mechanism:** asynchronous, **hierarchical parameter servers**: workers send H-step updates to a local parameter server (LPS) per region; each LPS applies them with momentum, sends accumulated updates to a global parameter server (GPS) every K updates, and merges the returned global model with weight α (§4.1).
- **Numbers (v1):** Pythia 70M / 160M / 410M on the Pile, 16 workers in 4 simulated regions with speeds drawn from 1 to 10; trace-driven simulation of time, real training in the simulated order (§5).
  - Table 1, tokens needed to reach the validation loss that the 160M reference reached after 12.9B tokens (the reference is described as training "from scratch on the first 12.9B tokens"; I take it to be synchronous training, see "Could not verify"): DiLoCo 11.8B / 12.9B / 12.3B; DiLoCo + DynUpd 10.2B / 11.5B / 10.8B; **Async Local-SGD (DN + DyLU) 14.0B / 16.1B / 16.1B**; HALoS 12.3B / 13.2B / 11.8B (70M / 160M / 410M).
    - (inference) Async Local-SGD needs 18.6% / 24.8% / 30.9% more tokens than DiLoCo for the same loss; HALoS +4.2% / +2.3% / −4.1%.
  - Wall-clock: HALoS 7.1× faster than DiLoCo at 160M, 1.9× faster than Async Local-SGD (Table 1).
  - With uneven workers per region and one LPS per region, HALoS "diverges" with the tuned hyperparameters (Table 3).
- **Central elements:** the GPS and the LPSs: **(a)**.
- **How its setting differs from ours:** 16 workers in 4 regions with a server per region; Pythia models; time simulated from traces.
- **Fit (inference):** not R1-compatible as published; included because it is an independent measurement of Async Local-SGD at equal loss, from scratch, with 16 heterogeneous workers, and it finds a token cost the original paper did not.
- **Question it raises for us:** Liu et al. found DN + DyLU at parity with synchronous DiLoCo per update (fine-tuning, 4 to 16 workers); HALoS finds it needs 19% to 31% more tokens (from scratch). Which regime is ours?

### S13. Eager Updates For Overlapped Communication and Computation in DiLoCo

- **Authors:** Satyen Kale, Arthur Douillard, Yanislav Donchev. 2025. Preprint.
- **arXiv:** 2502.12996. Versions: v1 Tue 18 Feb 2025 only. **Read v1** (HTML). https://arxiv.org/abs/2502.12996
- **Read status:** sections read: abstract, §2.2 to §2.3 (Algorithms 2 and 3), §3 (all), §4, §5. Not read: §1 beyond the opening, appendix tables 4 to 6.
- **Mechanism:** synchronous all-reduce DiLoCo ("implemented with an all-reduce, without any central parameter server", §3) in which each round's averaged outer gradient arrives one round late, so communication overlaps a whole inner phase. "Naïve delayed" applies the stale average; "eager" applies (1/M)(own current outer gradient + the others' previous-round outer gradients) (Alg. 3, §2.3).
- **Numbers (v1):** this is the cleanest measurement found of what a **one-round delay** costs.
  - Table 2 (500M, C4, 2 replicas, H = 30, Streaming DiLoCo underneath): eval loss no overlap 2.67; 1-inner-step overlap 2.67; 1-outer-step naive delayed 3.01 (2.73 with the outer lr lowered); 1-outer-step eager 2.69; 2-outer-steps eager 2.73. (inference) +12.7% / +2.2% / +0.75% / +2.2% in loss against no overlap.
  - H sweep (Fig. 5, 500M): loss rises 6% from H = 5 to 500 for naive delayed against 2% from H = 30 to 500 for eager (§3.4).
  - Table 1 (1B, Dolma, 2 replicas, against data parallel): DP 2.67 / 2.52 / 2.45 at 25B / 100B / 250B tokens; 1-outer-step eager 2.69 / 2.53 / 2.46 (inference: +0.75% / +0.40% / +0.41%); 1-inner-step overlap 2.66 / 2.51 / 2.45.
- **Central elements:** none (all-reduce).
- **How its setting differs from ours:** 2 replicas, each an FSDP job in a data centre; Streaming DiLoCo underneath; 500M and 1B models.
- **Fit (inference):** R1 met (all-reduce, no server); R4 only partly (still a full all-reduce each round, but one round late). It shows that a stale average can be made nearly harmless when each worker substitutes its own fresh contribution; the same idea is available to any peer that receives a late merge.
- **Question it raises for us:** with M = 2 the own-fresh share is 1/2; with 4 peers it is 1/4. Does eager's benefit shrink as M grows?

### S14. Streaming DiLoCo with overlapping communication (overlap and per-worker slack only)

- **Authors:** Douillard, Donchev, Rush, Kale, Charles, Garrett, Teston, Lacey, McIlroy, Shen, Ramé, Szlam, Ranzato, Barham (abs-page metadata). 2025. Preprint.
- **arXiv:** 2501.18512. Versions: v1 Thu 30 Jan 2025 only. **Read v1** (PDF). https://arxiv.org/abs/2501.18512
- **Read status:** sections read for this strand: §2.3 (overlap, mixing factor α), §3.3.2 (ablating the overlap, including per-worker slack). 01 (A3) read §3.1, §3.2, supplementary Tables 2, 5, 6, 7.
- **Read-status addendum:** audit 2 (2026-10-13) read the opening paragraph of §3.3 (`paper.txt` lines 499 to 505, v1), which states that all ablations use a 500M-parameter model on C4; the coordinator re-checked the same lines. The §3.3.2 overlap results above are therefore at 500M.
- **Mechanism:** synchronous fragment-wise DiLoCo over all-reduce; a fragment's outer gradient is received τ inner steps late and merged with the locally updated fragment with factor α (§2.3).
- **Numbers (v1):** the loss degradation "is negligible up to an overlap of 10 inner steps (< 0.2%)" (§3.3.2, Fig. 8); per-worker slack (τ1 = 1, τ2 varied, α = 0.5): "Training is very robust for values of τ2 less than 5" (Fig. 10 caption, figure only). Authors advise limiting the overlap to 5 inner steps.
- **Disagreement:** Factored Gossip (S9, App. B.2) found a 5-step overlap without fragment partitioning diverged at 1.5B with M = 8.
- **Central elements:** none (all-reduce).
- **Fit (inference):** R1 met; R4 partly (a bounded delay, not membership asynchrony); R5/R6 not addressed.
- **How its setting differs from ours:** 2 to 4 replicas in data centres; fragment-wise synchronization; 35M to 4B.
- **Question it raises for us:** is a per-worker slack of a few inner steps enough to absorb home-GPU speed differences, or are ours larger than τ2 < 5 covers?

### S15. What happens when nanochat meets DiLoCo?

- **Authors:** Alexander Acker, Soeren Becker, Sasho Nedelkoski, Dominik Scheinert, Odej Kao, Philipp Wiesner (exalsius). 2025. Technical report, preprint.
- **arXiv:** 2511.13761. Versions: v1 Fri 14 Nov 2025 only. **Read v1** (PDF, full text, 8 pages).
- **Code:** https://github.com/exalsius/nanochat-diloco: no licence detected, `pushed_at` 2025-11-06T13:15:28Z (`gh api`, queried 2026-10-13 14:36 UTC).
- **Read status:** full text.
- **What it is:** **synchronous** DiLoCo (8 A100 workers, H = 100 in pretraining, H = 30 in mid-training and SFT, Nesterov outer lr 0.8, momentum 0.9) wrapped around nanochat's 550M-parameter pipeline, against standard DDP with "the same number of steps" (§3, §4.2.1). The paper calls the cause "asynchronous updates", but the method described is synchronous rounds (inference from §3).
- **Numbers (v1), Table 1:** base CORE 0.2065 (DDP) against 0.1788 (DiLoCo); after mid-training ChatCORE 0.1060 against 0.0192; after SFT 0.1190 against 0.0157; switching to DDP after DiLoCo pretraining ("Hybrid") does not recover (SFT ChatCORE 0.0140). A pretraining "loss difference of roughly 0.15-0.20" (§4.1; no loss table). One run each.
- **Disagreement:** Decoupled DiLoCo (S1, App. B, Table 6) reports post-training parity at 5B and writes that its finding "is contrary to that of Acker et al. (2025)".
- **Bears on:** Chorus's product plan (pretraining then SFT and RL, D29): a pretraining gap may not stay a pretraining gap.
- **Central elements:** none.
- **Fit (inference):** synchronous all-reduce, so R1 met and R4 not; relevant as a warning about downstream effects, not as an averaging candidate.
- **How its setting differs from ours:** 550M, 8 A100s, Muon and AdamW inner optimizers, single runs; downstream metrics after mid-training and SFT.
- **Question it raises for us:** should the pilot's gates include a post-SFT check, since a pretraining gap of "roughly 0.15-0.20" in loss became a near-total downstream gap here?

### S16. Learning@home (asynchronous expert updates)

- **Source:** Ryabinin and Gusev, arXiv 2002.04013 v3 (21 Oct 2020), NeurIPS 2020; read in full in Stage 0 note 04b (block 7). For this strand I re-read §3.1 (asynchronous training), §3.3 (runtime) and §4.2 (convergence) in the v3 PDF.
- **Asynchronous expert update path:** each expert lives on one runtime; a backward request makes the runtime "update expert parameters by gradient descent" immediately, from whichever trainer sent it, so updates are asynchronous and stale (§3.3). The authors argue MoE "accumulates staleness at a slower pace" because different inputs touch different experts (§3.1). Persistence: a runtime "regularly saves latest expert weights into the same DHT" (§3.3).
- **No averaging:** each expert has a single holder; nothing is averaged (04b). Robustness: MNIST under 100 ms and 1000 ms delays and 10% expert failure (Fig. 5, figure only).
- **Relevance:** the opposite of holder-group averaging; a lone holder is the single point of loss that R5 is meant to avoid (inference).
- **Question it raises for us:** Learning@home persists expert weights in its DHT so a lost holder can be replaced; does R5 need two live holders, or one live holder plus a published copy?
- **Code:** https://github.com/mryab/learning-at-home: no licence detected, `pushed_at` 2020-11-05T11:22:48Z; successor Hivemind MIT, `pushed_at` 2026-01-11T21:13:45Z (`gh api`, queried 2026-10-13 14:36 UTC).

### S17. FoMoE (holder-group precedent; from the Stage 0 notes, not re-read)

- **Source:** "FoMoE: Breaking the Full-Replica Barrier with a Federation of MoEs", Sani, Cao, Kurmanji, Iacob, Jovanović, Gao, Zhao, Lane; arXiv 2606.19025, v1 17 Jun 2026, v2 20 Jun 2026; read in full (v2, plus v1 comparison) in Stage 0 notes 04a (block 2), 04b (block 8) and 06 (FoMoE check). Preprint; no code found.
- **What makes it the precedent:** each worker holds the dense part plus O_e·N_e/M experts; "we partition each router, along with the experts" (§3.3.3); dense parameters are averaged over all workers by ring all-reduce, while experts and their router rows are aggregated "within expert replica groups" (Alg. 2) (04a). This is exactly averaging an expert within the group of peers that holds it.
- **Synchronous and coordinated:** "i.i.d. data partitions", K local steps per round, "central coordinator, synchronous rounds" (§3.1, per 04a). Local optimizer state preserved across rounds; LocalAdamW averages both AdamW moments as well (04a, 04b).
- **Numbers (from 04a/04b, v2 Table 6, LocalAdamW, fixed placement, M = 4, validation PPL):** O_e = 1 / 2 / 4 at K = 32: 121.42 / 112.00 / 103.91; K = 64: 130.79 / 119.53 / 104.47; K = 128: 143.72 / 123.50 / 111.89. 04a's conversion: two holders of four (O_e = 2) cost +1.6% / +2.9% / +2.1% in log-PPL against full replica; one holder +3.4% / +4.8% / +5.3%. 54M proxy, about 51M of it embeddings (04a inference). No numeric centralized result (06).
- **Churn:** none studied; on reassignment, moved experts get fresh optimizer state and a warm-up (04a).
- **Central elements (inference from "central coordinator"):** (a) if run as a server; synchronous rounds.
- **Fit (inference):** R5 and R6 directly (holder groups of O_e; O_e = 2 is the R5 minimum); R1 not met as published (central coordinator); R4 not met (synchronous).
- **How its setting differs from ours:** 54M proxy dominated by embeddings, sigmoid gating, 5 to 20 rounds, LocalAdamW or Nesterov with kept state (04a, 04b).
- **Question it raises for us:** its holder-group averaging was only tested synchronously; nothing read tests holder-group averaging with peers dropping mid-round.

### S18. DiPaCo (module averaged over the paths through it; from Stage 0 note 04b, not re-read)

- **Source:** arXiv 2403.10616 v1 (15 Mar 2024), Douillard et al. (Google DeepMind), read in full in 04b block 4. Preprint.
- **Relevance:** per 04b, DiPaCo runs DiLoCo per module: each module's outer gradient is averaged over the paths through it (Algorithm 1, line 13), weighted by shard size, with its norm rescaled by the square root of the number of paths (§2.7). A module shared by some paths is averaged only among the workers that train it, i.e. a holder-group average with uneven group sizes. Synchronous rounds; starts from a pretrained 150M model. §4.5: DiLoCo against fully synchronous training of the same paths −0.3 / −0.6 / +0.1 PPL (2×2, 4×4, 8×8) (04b). No churn study.
- **Fit (inference):** R6-like (modules held by subsets of workers); R1 and R4 not addressed.
- **How its setting differs from ours:** paths of 150M with offline document routing; starts from a pretrained model.
- **Question it raises for us:** when an expert's holder count varies by round under churn, is DiPaCo's sqrt(holder count) norm rescaling the right correction?

### S19. Triaged sources (mechanism only, or not used for numbers)

- **Pseudo-Asynchronous Local SGD (PALSGD)**, Naganuma et al., arXiv 2504.18454 v2 (16 Sep 2025; v1 25 Apr 2025), TMLR 09/2025 (PDF header). Read: abstract and a grep of §4 to §5. Despite the name, it is **synchronous**: a global all-reduce every H steps, plus a local, communication-free probabilistic pull towards a stale global copy between all-reduces (§5, Eq. 6). Reports "24.4% faster than DDP" on TinyStories with GPT-Neo-125M (abstract; time to target). No server. Not an asynchronous candidate.
- **EDiT / A-EDiT**, Cheng et al. (Ant Group), arXiv 2412.07210 v2 (17 Feb 2025; v1 10 Dec 2024), ICLR 2025 (PDF header). Read: abstract, §3.3, §4.1, §4.2 text. A-EDiT replaces "fixed-step synchronization" with a fixed time interval: each worker trains until the time threshold, then all synchronize, so "no worker will wait longer than the single step time of the slowest worker" (§3.3). Still a collective sync of all workers (no server, no quorum). Quality: A-EDiT "marginally lags behind the sync version" (§4.2); its tables are garbled in the PDF text and no number was recorded.
- **Not Every Sync Is Safe**, Twelftree et al. (Maincode), arXiv 2607.02544 v1 (24 Jun 2026). Read: abstract. About scheduling DiLoCo merges around serving load (SLO violations), not averaging quality. Out of scope.
- **CGAD for Decoupled DiLoCo**, Shah and Sun, arXiv 2605.09126 v1: read in Stage 0 (01, D3): asynchronous staleness at τ = 8 with K = 4 workers on a 30M-token slice; at 10M, Nesterov 0.7/0.9 diverged (91.0) and outer lr 0.1 without momentum was best (7.6) (01, App. G Table 11). Under-trained; mechanism evidence only.
- **Momentum Look-Ahead (MLA)** for asynchronous low-communication training, Ajanthan, Ramasinghe, Avraham, Zuo, Long (Pluralis), ICLR 2025 workshop (per Decoupled DiLoCo's reference list, which I read). The Pluralis "Asynchronous DiLoCo" blog post corresponds to it (search lead). No arXiv version found (arXiv API title search, 2026-10-13). **Not read.** HeLoCo uses it as a baseline (S11).

## Findings for question 4 (and algorithmic churn)

### F1. Two different meanings of "asynchronous" in the sources

The papers use "asynchronous" for two different properties, and the distinction matters for R1 and R4 (inference, from the mechanisms in S1 to S14):

1. **No global barrier** (who must be present for a merge): quorum merges (Decoupled DiLoCo, S1), pairwise or sparse gossip (AD-PSGD S7, NoLoCo S8, Factored Gossip S9, GASLoC S10), group all-reduce (Moshpit S3, DeDLOC S4). A slow or absent peer delays only its own group or pair, or is left out of the quorum.
2. **Stale updates** (an update computed from an older model is applied to a newer one): Async Local-SGD (S2), HeLoCo (S11), HALoS (S12), the one-round delay of Eager Updates (S13), the τ-step overlap of Streaming DiLoCo (S14), DeDLOC's and SWARM's delayed parameter updates (one round).

Every published method of type 2 that I read applies stale updates to a **single global state held by one party** (a server or synchronizer), except the overlap methods S13 and S14, which keep an all-reduce and bound the delay to one round or τ steps. Every method of type 1 that has no server (gossip, group all-reduce) avoids a single global state altogether, so peers hold different models between merges.

### F2. Which methods run with no server, and what is central (classification per the brief)

| Method | Server or coordinator in the algorithm | Classification | Could the coordinator be a rotating peer role? (inference unless stated) |
|---|---|---|---|
| Synchronous all-reduce DiLoCo / Stage 0 rounds (S13, S14, 01) | none; every peer joins each all-reduce | none | not needed; but a missing peer blocks or forces a restart (S9 §5.2) |
| Moshpit / group all-reduce (S3, S4) | none; DHT for matchmaking | DHT on own machines: none; public DHT: (c) | not needed |
| DeDLOC (S4) | none in averaging; "backbone" peers, at least one always online (§3.3) | (a) if one must run around the clock | backbone role is held by several peers; availability "at all times" is the requirement |
| SWARM same-stage averaging (S5) | none; DHT | as for Moshpit | not needed |
| D-PSGD, AD-PSGD (S6, S7) | none; fixed graph | none | not needed |
| NoLoCo, Factored Gossip LocalM1M2, GASLoC 1-/2-Peer (S8 to S10) | none; random pairing each round (S8 uses a shared seed for routing) | none | not needed; the pairing could come from the run seed and round, like Chorus's assignment (inference) |
| Async Local-SGD (S2) | central server with global model, outer momentum, DN buffer (§3) | (a) | not described; state to hand over = model + momentum + buffer |
| Decoupled DiLoCo (S1) | central syncer with global fragments and outer optimizer state (§4) | (a) | **not described in the paper.** Its only syncer-failure path is restart from a Chandy-Lamport checkpoint (E.2). Learner recovery copies parameters and inner optimizer state from a peer learner (E.3), so peer-to-peer state transfer is in the design for learners, not for the syncer |
| HeLoCo (S11) | central synchronizer (§3) | (a) | not described |
| HALoS (S12) | local and global parameter servers (§4.1) | (a) | not described |
| FoMoE (S17) | "central coordinator, synchronous rounds" (04a) | (a) if run as a server | not described |

So, as published, **every asynchronous method that applies stale updates relies on a central holder of the global state**, and **every server-free method found is either synchronous within a group (all-reduce, Moshpit) or gossip without a global state**. No paper read describes or tests a synchronizer role that rotates among peers.

Inference on a rotating synchronizer (not tested anywhere I read):
- The state to hand over is about two model copies (global weights plus outer momentum; plus a DN buffer for S2), i.e. roughly 0.8 to 2.4 GB in fp32 for 100M to 300M parameters, comparable to one learner recovery in Decoupled DiLoCo (which moves 3 × N parameters, E.3).
- A hand-over needs agreement on the next holder and a rule for updates in flight. A deterministic rule from the run seed and round (as Chorus's assignment already is) could name the holder; it fails if that peer is offline, so a fallback order is needed.
- Decoupled DiLoCo's event tape (E.1: participant subsets, token weights, vector clocks) is what makes its timing-dependent merges replayable. A published tape would let any peer recompute the merges, which bears on principle 6 ("a merge rule that every peer computes identically"). Without a tape, a quorum-based asynchronous merge is not reproducible from public inputs alone (E.1: the subset "depends entirely on unpredictable wall-clock timing").

### F3. Quality cost against synchronous and against centralized training (numbers only from parts read)

Gaps in loss are relative; for perplexities they are in log-perplexity (my conversion, inference). "Same-step DP" and the other baselines are defined at the top of the Sources section.

| Method (source, locator) | Setting | Against synchronous (local averaging) | Against centralized / DP | Baseline type |
|---|---|---|---|---|
| Async Local-SGD, naive async DiLoCo (S2, Table 3, v2) | 20M / 60M / 150M, 4 workers, H = 50, continued from 24k-step checkpoint | +1.83% / +1.36% / +1.69% | not given | equal total local steps |
| Async Local-SGD, DN + DyLU (S2, Tables 1 to 3) | same; 4 to 16 workers | −0.14% / −0.03% / +0.06%; −0.14% to −0.18% at 4 to 16 workers (20M) | against same-step large-batch single worker: −0.86% / −0.34% / −0.42%; +0.25% at 16 workers | equal total local steps |
| Async Local-SGD as reimplemented in HALoS (S12, Table 1) | Pythia 70M / 160M / 410M from scratch, 16 workers, speeds 1 to 10 | +18.6% / +24.8% / +30.9% more tokens than DiLoCo to reach the same loss | 160M: +24.8% tokens against the 12.9B-token reference | tokens to target loss |
| HALoS (S12, Table 1) | same | +4.2% / +2.3% / −4.1% tokens against DiLoCo | 160M: +2.3% tokens | tokens to target loss; needs servers |
| Decoupled DiLoCo, K = 1 + grace vs K = 8 (S1, Table 5) | 2B dense, 26B tokens, M = 8, heterogeneous TPUs | text average 55.3 vs 54.4; vision 37.0 vs 37.6 (no loss reported); K = 1 without grace 51.4 / 25.7 | n/a | same run, quorum changed |
| Decoupled DiLoCo vs DP (S1, Tables 2, 3, 12, 14) | 2B to 9B dense; 2.8B-active MoE | n/a | text average within about 0.7 points (2B 54.4 vs 55.1 at 26B tokens; 5B 62.8 vs 62.5; 9B 68.0 vs 67.8; MoE 67.9 vs 68.4 without failures) | equal tokens; downstream only |
| HeLoCo (S11, Table 1) | 15M, 5 workers, non-IID, 24k steps | homogeneous: −1.8% (6.50 vs 6.62); severe staleness: +15.4% | not given | equal tokens |
| One-round-stale average, Eager (S13, Table 2) | 500M, 2 replicas, H = 30 | eager +0.75%; naive +12.7% (+2.2% with lowered outer lr); 2 rounds eager +2.2% | 1B Dolma: +0.75% / +0.40% / +0.41% at 25B / 100B / 250B tokens against DP (Table 1) | equal tokens |
| τ-step overlap, Streaming DiLoCo (S14, §3.3.2) | 35M to 4B (01) | < 0.2% up to τ = 10 | n/a | equal tokens |
| Moshpit SGD (S3, §4.3) | ALBERT-large 18M, 66 preemptible GPUs | n/a | "same within the margin of error" final loss (figure only) | wall-clock, same global batch |
| DeDLOC (S4, App. I.6) | ALBERT-large, 40 volunteers | n/a | stepwise curves "virtually identical" to 8×V100 DP (figure only) | same global batch, per step |
| NoLoCo (S8, Table 1) | 125M to 6.8B, DP 8 to 16, with pipeline routing | −0.16% to −1.45% in 14 of 16 cells; +0.27% / +0.42% in 2 | +0.83% to +7.68% against FSDP | same global batch and steps (inference from App. B) |
| NoLoCo reimplemented without pipeline routing (S9, App. B.1) | 1.5B, M = 8 | 22.65 vs DiLoCo 18.65, i.e. +6.6% (inference); diverged with DiLoCo hyperparameters | n/a | equal tokens |
| Factored Gossip LocalM1M2, pure pairwise gossip (S9, Table 1) | 1.5B, M = 8, H = 100, 10B tokens | +1.29% | +3.49% against Sync DP (+2.37% at 30B tokens); M = 16: +8.99% | same global batch, equal tokens |
| Factored Gossip GlobalM1LocalM2 (S9, Table 1) | same | +0.27% | +2.44% | same |
| GASLoC 2-Peer / 1-Peer (S10, Tables 1b, 3) | 134M (8 / 16 / 32 replicas), 551M (8 / 16), H = 30 | 134M: +0.61 / +1.47 / +2.55% and +1.21 / +2.65 / +3.68%; 551M: 0.0 / +1.87% and +1.14 / +5.24% | DiLoCo itself is +3.77 / +6.92 / +11.01% against DDP at 134M; 551M 2-Peer 2.64 vs DDP 2.64 at 8 replicas | same global batch, equal tokens |
| FoMoE holder groups O_e = 2 of 4 (S17, Table 6 via 04a) | 54M MoE, synchronous, LocalAdamW | +1.6% / +2.9% / +2.1% against full replica (K = 32 / 64 / 128) | no centralized number | equal tokens |

What the sources show, and what they do not:

- **Synchronous local averaging is itself the reference cost.** The DiLoCo-family gaps against DP in 01 (+0.3% to +3.9% at M = 4 to 8 with tuned Nesterov; Stage 0's +6.1% with plain averaging) are the floor the asynchronous and gossip variants are compared to. The asynchronous numbers above are mostly measured against DiLoCo, not against centralized training.
- **Staleness through outer momentum is the documented failure.** Naive asynchronous DiLoCo is worse than synchronous at every size tested in S2 (+1.4% to +1.8%); HeLoCo reports that asynchronous Nesterov "diverges across all configurations" in its setting (S11 §4.2); naive one-round delay costs +12.7% in S13 until the outer lr is lowered. The fixes all modify how momentum meets stale updates: delayed momentum (S2), momentum-aligned correction (S11), own-fresh substitution (S13), RDA and token weights (S1).
- **Parity claims depend on the regime.** DN + DyLU is at parity with synchronous DiLoCo per update when fine-tuning from a checkpoint with 4 to 16 simulated workers (S2), but needs 19% to 31% more tokens than DiLoCo from scratch with 16 heterogeneous workers in HALoS's reimplementation (S12). HeLoCo beats synchronous DiLoCo at equal tokens only when staleness is low and loses by up to 15% when four of five workers are 15× slower (S11).
- **Pure gossip (no global step) costs about 1% to 4% against DiLoCo at 8 to 32 workers** in the two 2026 papers that measure it (S9 at 1.5B; S10 at 134M and 551M), growing with worker count. NoLoCo reports the opposite sign (better than DiLoCo) with pipeline routing (S8); S9 could not reproduce stability without it.
- **Holder-group averaging has been measured only synchronously** (FoMoE, DiPaCo) and costs more the fewer holders an expert has (FoMoE: O_e = 1 costs about twice O_e = 2 against full replica, S17).
- **Silent (not found in this search):** any asynchronous or gossip method combined with holder-group (sliced MoE) averaging; any asynchronous LM result below 15M or with character-level data; any quality result with peers actually leaving and joining during LM training at 100M to 300M (Decoupled DiLoCo's failure runs are 2B to 5B; S9's failures are only in a utilization simulator); a rotating synchronizer.

Where sources disagree:
- Async Local-SGD's parity (S2) against HALoS's token cost for the same algorithm (S12); settings differ (fine-tuning vs from scratch; 4 to 16 vs 16 workers; simulated speeds in both).
- NoLoCo better than DiLoCo (S8) against NoLoCo much worse and unstable without pipeline routing (S9 App. B.1).
- Streaming DiLoCo's overlap negligible up to 10 steps (S14) against divergence of a 5-step overlap without fragment partitioning at 1.5B, M = 8 (S9 App. B.2).
- DiLoCo pretraining damaging later SFT (S15, 550M, synchronous DiLoCo) against post-training parity at 5B (S1 App. B, which names S15 as contrary).
- AD-PSGD's epoch-wise parity with all-reduce on ImageNet (S7) against lower accuracy after 150 epochs in Moshpit's heterogeneous setup (S3).

### F4. Communication cost per method (from the sources; arithmetic for our sizes is inference)

- **All-reduce DiLoCo (synchronous):** one outer gradient per round; bandwidth-optimal all-reduce sends about 2(N − 1)/N × S per peer (the standard ring all-reduce cost; my statement, not from a source read here; S9 notes all-reduce needs "at most about twice the bandwidth of pairwise gossip", §5.2). (inference) For S = 0.2 to 0.6 GB (fp16, 100M to 300M) and N = 4: about 0.3 to 0.9 GB up and down per peer per round; at 20 Mb/s upload that is 120 to 360 s per round.
- **Syncer or server (S1, S2, S11, S12):** each learner sends one update and receives one model per round (or one fragment per step in S1); the syncer receives and sends N updates. (inference) With N = 4 home peers and the syncer on one of them, that peer moves about 4 × S each way per round (0.8 to 2.4 GB), the hotspot D-PSGD's Table 1 describes (O(n) on the busiest node, S6).
- **Pairwise gossip (S8, S9, S10):** S up and S down per peer per round; "per-byte volume is essentially the same as DiLoCo" (S8 App. C). The gain is no global barrier, not fewer bytes.
- **Moshpit group all-reduce (S3):** O(max(s, M)(M − 1)/M) per peer per round plus O(log N) DHT requests (Eq. 4); d rounds for an exact average with a full grid.
- **Compression evidence that applies to all of the above:** int4 outer gradients +0.09% relative validation loss, 2 bits +32%, 1 bit +83% (S1 Table 10, 2B with heavy simulated failures); quantization differences "bounded by 0.12%" with one-outer-step overlap (S13 §3.4).

### F5. How the algorithms behave when peers leave, join or straggle

| Method | Leave mid-round | Straggler | Join / rejoin | Tested how |
|---|---|---|---|---|
| Synchronous all-reduce DiLoCo | round blocks or must restart (S9 §5.2) | everyone waits for the slowest (S10 §3.2 timing model; S7 abstract: synchronous all-reduce SGD performs "poorly in a heterogeneous environment") | download current model | S9 utilization simulator only |
| Moshpit (S3) | groupmates "skip a round of averaging" (§3.1); global mean preserved (Thm 3.1) | only its group waits | download "latest parameters" and optimizer statistics from "a random up-to-date peer" (App. F) | scalar averaging with failure probability (Fig. 3); preemptible ALBERT run |
| DeDLOC (S4) | group all-reduce limits failure to the group (§3.2) | accumulates fewer gradients; global batch tracked in the DHT | catch-up from an up-to-date peer (§3.3) | real volunteer run (40 people, 91 devices) |
| SWARM (S5) | requests rerouted to other stage peers; failed peer "temporarily banned" (§3.2) | routed less work (throughput-weighted) | reload stage state from neighbours (App. E) | 400 preemptible T4s |
| AD-PSGD (S7) | not studied in parts read | localized to its neighbours; "orders of magnitude" better than all-reduce with one 100× slow worker (§5) | not studied | vision |
| Async Local-SGD (S2) | not studied | DyLU gives slow workers fewer steps; grace period merges near-simultaneous arrivals | not studied | simulated speeds |
| Decoupled DiLoCo (S1) | excluded from the fragment's merge (weight 0) | quorum K plus grace window; token-weighted | learner recovery from a peer learner within H syncer steps (E.3) | event tapes for up to 2.4M simulated chips; one real heterogeneous run |
| NoLoCo, Factored Gossip, GASLoC (S8 to S10) | argued: affects only the pair; "assuming failed exchanges can be skipped or rescheduled" (S10 §3.2) | pairs wait for each other only; GASLoC lowers the slow peer's H_i (§3.2) | not studied | simulated latencies (S8 App. G), bandwidth-throttled straggler (S10 Fig. 3), 5% failure in a utilization simulator (S9) |
| FoMoE, DiPaCo holder groups (S17, S18) | not studied | not studied | moved experts reinitialize optimizer state (FoMoE, 04a) | none |
| Learning@home (S16) | unanswered expert excluded, gate renormalized (04b) | asynchronous by design | runtime re-announces in the DHT | MNIST with 10% expert failure (figure only) |

What happens when a group loses its only copy (R5, algorithmic side):
- SWARM keeps training "as long as there is at least one active participant per stage"; a stage with none stalls the pipeline (S5 §3.2).
- Learning@home persists expert weights to the DHT so they can be restored (S16 §3.3).
- Decoupled DiLoCo keeps the canonical fragments on the syncer, so a learner's loss never loses a fragment; checkpoints cover the syncer (S1 E.2).
- Moshpit and DeDLOC keep full replicas on every peer; nothing is held by one peer only (S3, S4).
- (inference) For Chorus slices, an expert whose two holders both drop in a round loses that round's training for the expert under every method read; with one survivor, a quorum-of-1 rule (as S1 uses per fragment) would merge the survivor's update alone. No paper measures what a holder group of 1 out of a planned 2 does to quality; FoMoE's O_e = 1 results (S17) are the nearest proxy, but they are for a planned single holder, not a dropout.

### F6. Precedents for averaging an expert within the group of peers that holds it

1. **FoMoE (S17)**: experts and their router rows aggregated "within expert replica groups"; dense parts over all workers. Direct precedent, synchronous, 54M proxy, central coordinator.
2. **DiPaCo (S18)**: each module's outer gradient averaged over the paths that contain it, with shard-size weights and sqrt(path count) norm rescaling. Modules, not experts within a layer; synchronous.
3. **SWARM (S5)**: gradients all-reduced within each pipeline stage's peer group; synchronous per step; stage, not expert.
4. **Counter-example, Learning@home (S16)**: one holder per expert, updated in place asynchronously, no averaging.
5. Not found: any asynchronous or gossip variant of holder-group averaging; any study of holder dropout within a group.

## Candidates for Gate N1b

This section describes the evidence on each candidate. It does not recommend a Chorus design.

### Evidence grid

"Pilot-like" means the evidence includes something near the pilot: 100M to 300M parameters, 3 to 5 peers, heterogeneous or departing peers, home-link bandwidth. Read status is in each source block.

| Candidate | Needs a central holder? | LM pretraining from scratch? | Scale with numbers | vs synchronous local averaging | vs centralized / DP | Churn or stragglers in training runs | Pilot-like |
|---|---|---|---|---|---|---|---|
| Async Local-SGD, DN + DyLU (S2) | yes, server (a) | no (continued from a 24k-step checkpoint) | 20M to 150M, 4 to 16 workers | parity per update (−0.14% to +0.06%) | only same-step large-batch (−0.3% to −0.9%; +0.25% at 16 workers) | simulated speeds; no departures | partly: 150M, 4 workers; but not from scratch, simulated |
| same, independent reimplementation (S12) | yes | yes | 70M to 410M, 16 workers | +19% to +31% tokens vs DiLoCo | +24.8% tokens vs reference at 160M | simulated speeds | partly: 160M, from scratch; 16 workers |
| Decoupled DiLoCo (S1) | yes, syncer (a); rotation not described | yes | 2B to 9B dense; 2.8B and 3.8B-active MoE | Table 5 only: K = 1 + grace matches K = 8 on downstream averages (2B) | downstream parity at 2B to 9B and MoE; loss numbers only as deltas | yes: simulated failures (event tapes), heterogeneous TPUs, scavenging | no: data-centre scale; only MoE evidence for async |
| HeLoCo (S11) | yes, synchronizer (a) | yes | 15M, 5 workers, far from converged | −1.8% (no staleness) to +15.4% (severe) at equal tokens | none | simulated speeds, non-IID | partly: 5 workers; model far smaller and under-trained |
| HALoS (S12) | yes, hierarchical servers (a) | yes | 70M to 410M | +2.3% tokens (160M) vs reference; −4.1% to +4.2% vs DiLoCo | as left | simulated speeds; diverged with uneven grouping | partly; violates R1 by design |
| Group all-reduce (Moshpit, DeDLOC) (S3, S4) | no | yes (ALBERT MLM) | 18M (ALBERT-large) | not measured | final loss "same within the margin of error" (figure only) | real preemptible and volunteer peers | partly: real churn, but synchronous large-batch SGD, not local steps |
| Pairwise gossip local SGD: Factored Gossip LocalM1M2 (S9) | no | yes | 1.5B, 8 and 16 workers | +1.3% (M = 8), widening at M = 16 | +3.5% (M = 8, 10B tokens); +9.0% (M = 16) | none in training; 5% failure only in a utilization simulator | no |
| GASLoC 1-/2-Peer (S10) | no | yes | 134M and 551M, 8 to 32 workers | +0.6% to +3.7% (134M); 0% to +5.2% (551M) | 551M 2-Peer = DDP at 8 replicas | one bandwidth-throttled straggler (wall-clock only, figure) | partly: 134M; 8 workers minimum |
| NoLoCo (S8) | no | yes | 125M to 6.8B | −1.45% to +0.42% (with pipeline routing) | +0.8% to +7.7% vs FSDP | simulated latencies only | partly: 125M; disputed by S9 without routing |
| One-round-delayed merge (Eager, S13) | no (all-reduce) | yes | 500M (M = 2), 1B | +0.75% (eager) | +0.4% to +0.75% vs DP at 1B | none | partly: tells us what a one-round lag costs, not churn |
| Holder-group averaging (FoMoE, S17) | coordinator (a) as published | yes | 54M proxy | not applicable (synchronous) | no number | none | the only sliced-MoE evidence; synchronous only |

### What the evidence says about each, briefly

- **Async Local-SGD (DN + DyLU)** has the most direct sync-vs-async LM numbers at a size near the pilot (150M, 4 workers), with parity per update, but in continued pretraining and with simulated speeds; an independent from-scratch reimplementation finds a 19% to 31% token cost. It needs a single holder of model, momentum and buffer.
- **Decoupled DiLoCo** has by far the most extensive churn and straggler evidence and the only asynchronous MoE result, at 2B to 9B in data centres, with downstream accuracies rather than loss. It needs a syncer; a rotating syncer is untested.
- **Gossip variants (Factored Gossip LocalM1M2, GASLoC, NoLoCo)** are the only server-free asynchronous-in-membership options with LM pretraining numbers. They cost about 1% to 4% against DiLoCo at 8 to 32 workers, growing with worker count; no paper trains through actual departures; NoLoCo's stability is disputed. They leave no single canonical model between merges.
- **Group all-reduce (Moshpit, DeDLOC)** has the only evidence from real volunteer and preemptible churn, but it was used for synchronous large-batch SGD, not H-step local training, and the LM evidence is ALBERT-large with figure-only quality.
- **HeLoCo, HALoS** add staleness corrections for a central holder; HeLoCo's evidence is at 15M and far from convergence; HALoS needs servers.

### What a Gate N1b would need, by the standards the sources themselves use (inference, not a design)

1. **Two comparisons at equal compute, from the same seeds** (Stage 0 used 7, 11, 19): the asynchronous run against the synchronous mode (Stage 0's rounds, D38) and against centralized training. The async papers report against DiLoCo (S2, S9, S10), against DP at the same global batch (S8, S9, S10), or in tokens to a target loss (S12). Stage 0's centralized arm is the "more steps" baseline (01), which none of the async papers uses, so the gate must state which baseline it uses.
2. **Both equal-tokens and equal-wall-clock readings.** HeLoCo's comparison with synchronous training flips sign between them (S11 Table 1, row (1,6,6,6,6): HeLoCo 5.43% worse at equal tokens, 5.80% better at equal wall-clock); the gate needs a pre-registered primary reading.
3. **A recorded heterogeneity and churn schedule**, replayable so that the asynchronous run can be compared and rerun: Decoupled DiLoCo's event tapes (S1 E.1) and Async Local-SGD's "faked training time based on real-world device statistics" (S2 §3) are the two precedents. The schedule should include peers leaving mid-round, not only slow peers; none of the gossip papers did this.
4. **The staleness distribution actually seen** (S11 reports per-worker update shares and mean staleness; S2 shows that even simultaneous arrivals applied one at a time cost +1.4% to +1.8%).
5. **For slices (R5, R6):** holders per expert per round as realized under churn, and the quality of experts whose group shrank to one or zero; no source measures this.
6. **The outer optimizer and merge as part of the gate's definition**, because the sources show the asynchronous result depends on them (Nesterov unstable with staleness in S2, S11, S13; RDA needed at M = 16 in S1 Table 9; NoLoCo's step disputed in S9).
7. **A downstream check after SFT**, given S15's report that a synchronous DiLoCo pretraining gap became a large post-training gap at 550M, against S1's parity at 5B.
8. **Scale caveat:** every asynchronous result near 100M to 300M is either continued pretraining (S2), a reimplementation inside a server hierarchy (S12), or a gossip method tested only at 8 workers or more (S10). None has 3 to 5 peers with real departures.

## Could not verify

- **Decoupled DiLoCo Table 14, 2B column:** printed text averages 52.3 (DP) and 51.6 (Decoupled), but the seven text tasks in the same column average to 55.1 and 54.4 (my arithmetic), the values Table 12 prints for the same runs. The 5B and 9B columns are consistent with their tasks. Not resolved; I use 55.1 and 54.4.
- **Decoupled DiLoCo Table 15 "Validation loss delta":** the reference run for the deltas is not stated in the text read.
- **Decoupled DiLoCo Table 5:** caption says "TPUv6e and TPUv5p", §5.4 text says "four learners on TPUv5e and four on TPUv5p". Not resolved.
- **HALoS Table 1 target:** the text describes training Pythia-160M "from scratch on the first 12.9B tokens" and then training each method to "the same validation loss"; which method produced the reference loss (presumably synchronous) and whether the 70M and 410M columns use the same protocol are not stated in the parts read.
- **HeLoCo abstract figures:** "up to 7.5%" (asynchronous baselines, fixed token budget) matches the homogeneous row's 7.50 against asynchronous Nesterov, while the table's maximum in that column is 8.23 ((1,1,6,6,6)); "up to 3.3% at a fixed wall-clock budget" against MLA matches the token-budget column's 3.33 (the wall-clock column has the same 3.33 in that row). Reported as the table shows.
- **Venues not confirmed at source:** D-PSGD (NeurIPS 2017) and AD-PSGD (ICML 2018) are from my general knowledge; HALoS at ICML 2025 is from a search result (PMLR v267 page, not opened) and an HTML keyword line; Factored Gossip "Accepted at ICML 2026" is from the arXiv comment only.
- **NoLoCo's pairing mechanism:** the outer-step subgroups are "randomly chosen" (§3.2); whether they come from a shared seed (as the routing does in App. A) was not checked in the code.
- **Factored Gossip's pairwise matching:** "one round of random-matching pairwise averaging" (Table 2); who draws the matching is not stated in the parts read.
- **Momentum Look-Ahead (MLA)** (Ajanthan et al., ICLR 2025 workshop): cited in Decoupled DiLoCo's references and used as a baseline by HeLoCo; no arXiv version found; not read.
- **Hivemind's averager and Moshpit:** whether Hivemind's current decentralized averager implements Moshpit All-Reduce was not checked in code.
- **SWARM Appendix A (fault tolerance)**, AD-PSGD Appendix A (wait-free implementation), D-PSGD's NLP supplementary results: referenced, not read.

## Gaps

- **No source tests a rotating synchronizer.** Whether Decoupled DiLoCo-style or Async Local-SGD-style asynchrony can run with the syncer role passing among 3 to 5 intermittently online peers is unanswered by the literature read; it would need a prototype.
- **No asynchronous or gossip method has been combined with holder-group (sliced MoE) averaging**, and no source measures quality when a holder group shrinks mid-round (R5).
- **No LM result with real departures at 100M to 300M** under any asynchronous or gossip method; Decoupled DiLoCo's failure runs are 2B to 5B with simulated failures, and the gossip papers simulate failures only in utilization models.
- **Small-worker-count regime:** gossip results start at 8 workers (S9, S10) or use pipeline routing (S8); with 3 to 5 peers a pairwise round is a near-complete mix, and how that compares to all-reduce was not found.
- **Character-level or sub-15M asynchronous LM results:** not found.
- **Equal-wall-clock quality on home links:** S9 and S8 report time from simulators or throttled data-centre links; no measurement on actual home connections was found in this strand.
- **Not read:** Momentum Look-Ahead (no arXiv version found); SeedFlood (arXiv 2602.18181, zeroth-order gossip, mainly fine-tuning per search snippet; not opened); Epidemic Learning (De Vos et al., cited by S8; not opened); Photon's and DES-LOC's asynchrony (none, per 01); SPARTA (cited by S9; not opened); Gensyn GWTF (cited by S8; not opened); "Taming Momentum in a Distributed Asynchronous Environment" (1907.11612, cited by S15; not opened).
- **Other strands own:** DHT bootstrap and NAT traversal (the DHT and relay points above are mechanism only), storage of checkpoints, bandwidth measurements, systems maintenance.

## Query log

All times local (TST), 2026-10-13.

| Time | Tool or site | Query or action |
|---|---|---|
| 17:18 | n/a | Read the brief, ROADMAP, SRS §9, Stage 0 notes 01 (full), 04a §2 (FoMoE), 04b §7 to §8, 06 FoMoE check, report §3.1 |
| 17:19 to 17:20 | arxiv.org | abs page + PDF for 2401.09135, 2604.21428, 2103.03239, 2106.10207, 1705.09056, 1710.06952, 2301.11913, 2606.00271, 2502.12996, 2501.18512 (`sleep 3` between requests); `pdftotext -layout` |
| ≈17:21 | WebSearch (standard) | "asynchronous DiLoCo language model pretraining stale updates 2025 arXiv" |
| ≈17:21 | WebSearch (standard) | "gossip averaging decentralized LLM pretraining no all-reduce 2025" |
| ≈17:21 | WebSearch (standard) | "asynchronous local SGD heterogeneous workers language model 2026 arXiv" |
| ≈17:21 | WebSearch (standard) | "NoLoCo no all-reduce low communication arXiv Gensyn" |
| ≈17:21 | WebSearch (standard) | "HALoS hierarchical asynchronous local SGD geo-distributed LLM" |
| ≈17:21 | WebSearch (standard) | "decentralized mixture of experts training expert averaged among replicas asynchronous volunteers 2026" |
| ≈17:21 | WebSearch (extended) | "peer-to-peer asynchronous DiLoCo consumer GPUs internet training 2026 arXiv gossip" |
| 17:21 to 17:22 | arxiv.org | abs page + PDF for 2506.10911, 2506.04531, 2606.11081, 2606.22768, 2511.13761, 2504.18454, 2412.07210, 2607.02544, 2002.04013 |
| 17:24 to 17:25 | arxiv.org | HTML of 2604.21428v1 (two-column PDF interleaved); converted with a local `html.parser` script |
| 17:27 to 17:28 | arxiv.org | HTML of 2401.09135v2, 2103.03239v4, 2106.10207v2, 2301.11913v2, 2606.00271v1, 2502.12996v1, 2506.10911v2, 2506.04531v1, 2606.11081v1, 2606.22768v1 (`sleep 3` between requests) |
| 17:29 to 17:34 | local files | Reading: S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16; triage of S19 items |
| 17:33 | local files | Stage 0 note 04b block 4 (DiPaCo) re-read for the holder-group precedent |
| ≈17:35 | WebSearch (standard) | "Pluralis "asynchronous" DiLoCo heterogeneous GPUs arXiv paper momentum look-ahead" (lead: Momentum Look-Ahead, ICLR 2025 workshop) |
| 17:35 to 17:36 | export.arxiv.org API | `search_query=all:"momentum look-ahead"` (1 result: HeLoCo; no MLA arXiv version); an earlier http query returned nothing |
| 17:36 (14:36 UTC) | api.github.com via `gh api` (authenticated, read-only) | `repos/` for gensyn-ai/noloco, utnslab/HALoS, yandex-research/moshpit-sgd, yandex-research/DeDLOC, yandex-research/swarm, google-deepmind/asyncdiloco, exalsius/nanochat-diloco, PluralisResearch/node0, mryab/learning-at-home, learning-at-home/hivemind (fields `license.spdx_id`, `pushed_at`, `archived`, `created_at`) |
| 17:30 to 17:44 | local Python (`-I`) | arithmetic for the (inference) gaps: two scripts in the session scratchpad (`calc1.py`, `calc2.py`) |

Not covered in this strand:

- No code was read (only repository metadata). Whether NoLoCo's pairing uses a shared seed, and how Hivemind's averager behaves on a failed groupmate, would need the code.
- Not opened: Momentum Look-Ahead (no arXiv version found), SeedFlood (2602.18181), Epidemic Learning, SPARTA, GWTF, "Taming Momentum in a Distributed Asynchronous Environment" (1907.11612), FedBuff, Papaya, HGA-FL, FedAH; DiLoCoX; INTELLECT-2/3 asynchronous RL (out of scope for pretraining averaging).
- Sections not read: SWARM App. A; AD-PSGD App. A; D-PSGD supplementary NLP results; NoLoCo App. D to F; Factored Gossip §1 to §3, D, E; GASLoC §1, §2, §3.1 and appendices; HeLoCo §1, §2 and appendices; HALoS §1 to §3, appendices; EDiT tables (garbled; HTML not fetched).
- No citation chasing (OpenAlex or Semantic Scholar) for this strand; discovery was by 8 web searches, the arXiv API and the reference lists of the papers read (Decoupled DiLoCo App. A, NoLoCo App. C, Factored Gossip App. B to C).
- Venues were not checked in OpenAlex.
