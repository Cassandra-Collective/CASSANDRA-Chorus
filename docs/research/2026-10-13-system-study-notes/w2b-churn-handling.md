# W2b: churn, stragglers, timeouts and lost holders (question 6) · system-study notes

Status: complete draft, 2026-10-13 ≈18:45 TST (skeleton 17:56). Fourteen source blocks, findings F1 to F9, could-not-verify, gaps, query log.

Strand: question 6 of `docs/research/2026-10-13-system-study-brief.md` only. Builds on the wave-1 notes (w1a to w1d); does not repeat them. No design is recommended for Chorus.

Method: code read from shallow clones under the session scratchpad (`sysstudy/sources/w2b/c/`), never run, built or installed; papers fetched from arxiv.org with `curl` and converted with `pdftotext -layout` (`sysstudy/sources/w2b/p/`). Locators are file and line at the commit given, or section at the arXiv version given. "(inference)" marks my reasoning. Classification of central elements: (a) a server we would run; (b) a public static-file host; (c) a public third-party network for live coordination.

## Sources

A note on the request to see w1b's "Coverage gaps", items 3 and 7: w1b has no section with that title. The items in w1b that this strand closes are: "Not covered in this strand", item 1 (no code read: NoLoCo's pairing, Hivemind's averager on a failed groupmate) and "Could not verify", items 7 (NoLoCo pairing), 10 (Hivemind averager and Moshpit) and 11 (SWARM Appendix A). I took those to be the intended items. A second candidate reading is w1b's `## Gaps`, items 3 ("No LM result with real departures at 100M to 300M") and 7 (the list of unread sources); item 3 is addressed under Findings (F6) and item 7's sources are outside question 6 except where noted. Both readings lead to the same reading work here.

### B1. Hivemind: decentralized averager, Optimizer, and remote mixture-of-experts

- **Maintainers:** learning-at-home (Max Ryabinin, Alexander Borzunov and others). https://github.com/learning-at-home/hivemind. Licence and maintenance are in w1a S7 and w1c S12 (MIT; `pushed_at` 2026-01-11T21:13:45Z); not repeated.
- **Commit read:** `4bd43b77895019b20d18d81d0d0c1a5ab9a10847` (commit date 2026-01-04T23:36:23Z), shallow clone 2026-10-13 17:55 TST.
- **Read status (files read):** `hivemind/averaging/allreduce.py` (all, 377 lines); `hivemind/averaging/partition.py` (lines 20 to 60, 95 to 285); `hivemind/averaging/averager.py` (lines 50 to 175, 380 to 760); `hivemind/averaging/matchmaking.py` (lines 25 to 75, 149 to 177, 371 to 412, plus a grep of all timeout, leader and disband lines); `hivemind/averaging/key_manager.py` (lines 20 to 119); `hivemind/optim/optimizer.py` (lines 30 to 70, 136 to 150, 345 to 410, 510 to 730); `hivemind/optim/state_averager.py` (lines 540 to 566, 658 to 698); `hivemind/optim/progress_tracker.py` (grep); `hivemind/moe/client/moe.py` (lines 25 to 140, 194 to 290, 340 to 442); `hivemind/moe/server/dht_handler.py` (all); `hivemind/moe/server/checkpoints.py` (function index and lines 37 to 75); `hivemind/moe/server/server.py` (lines 38 to 58, 155 to 180, `_generate_uids` grep); `hivemind/utils/timed_storage.py` (lines 71 to 93).
- **Read-status addendum:** audit 3 (2026-10-13) read `hivemind/optim/optimizer.py` lines 177 to 178 and 209 to 210 at `4bd43b7` and confirmed the defaults `matchmaking_time` 15.0 and `averaging_timeout` 60.0 and the fallbacks of `next_chunk_timeout` and `allreduce_timeout` to them.
- **Setting:** a library for volunteer training over the internet; data-parallel collaborative training (Optimizer) and remote experts (MoE). No experiments in the code.

**A groupmate failing during averaging (all-reduce).**
- The all-reduce is a butterfly: the i-th peer of the group averages the i-th part of the vector (`allreduce.py` line 49), so every peer is both a sender and a reducer.
- **Failed sender.** A sender that has not started sending by `sender_timeout` is banned (`_handle_missing_senders`, lines 192 to 199); one that errors or stalls mid-stream is banned too (lines 309 to 315, 335 to 359). A ban calls `on_sender_failed`, which will "Exclude that sender's data for averaging any parts that it did not submit yet" (`partition.py` lines 248 to 255). The part's average divides by the weights actually accumulated (`partition.py` lines 242 to 244, 260). (inference) Parts the failed sender had already contributed keep its data, later parts do not, so different parts of one vector can be averaged over different subsets of the group.
- **Failed reducer.** If the peer averaging some part fails, every other peer marks that reducer failed and uses "our local part instead" for the missing parts (`register_failed_reducer`, `partition.py` lines 128 to 136; called in `allreduce.py` lines 241 to 245). Those parts are simply left un-averaged for this round; the run logs "Averaging: received X% results" (`partition.py` lines 173 to 174). (inference) The error from that one connection is raised inside a background task and only logged at debug level (`allreduce.py` lines 183 to 190), so the round still completes for the survivors with part of the vector unaveraged.
- **Timeouts.** Defaults: `sender_timeout` equals `next_chunk_timeout`, `reducer_timeout` is twice that (`averager.py` lines 84 to 89, 154 to 157); `allreduce_timeout` bounds the whole round (line 83, applied lines 456 to 465). In `hivemind.Optimizer`, `next_chunk_timeout` defaults to `matchmaking_time` (15 s) and `allreduce_timeout` to `averaging_timeout` (60 s) (`optimizer.py` lines 177 to 179, 209 to 210). The docstring says `averaging_timeout` should be "around of 2x the actual time it takes to run all-reduce" (line 95).
- **Updates are applied in place, tensor by tensor**, as each averaged tensor arrives (`averager.py` lines 556 to 559). (inference) If a round aborts part way, the tensors already averaged stay averaged and the rest stay local.
- **Retry or give up.** On `AllreduceException`, `MatchmakingException` and P2P errors the step retries if `allow_retries` is set and the deadline has not passed, otherwise it ends with the exception (`averager.py` lines 469 to 485).

**Group formation and stragglers (matchmaking).**
- Leader and follower protocol over the DHT. When the matchmaking time runs out, a leader with at least `min_group_size` members (default 2, `averager.py` line 119) runs the all-reduce "with what we have"; with fewer it disbands (`matchmaking.py` lines 161 to 170, 295 to 299). A follower whose leader does not answer within `request_timeout` moves on to the next candidate leader (lines 238 to 243). A late peer simply misses the group.
- The leader shuffles the member order randomly and draws a random group ID (`matchmaking.py` lines 375 to 378).
- **Moshpit-style group keys.** After each group, every member appends bits derived from a random generator seeded by the group ID and its own index (`key_manager.py` lines 94 to 105), so former groupmates move to different buckets. With the default `initial_group_bits=""` the key never changes and every peer stays in one bucket (line 104). (inference) Hivemind's averager is Moshpit All-Reduce when initial group bits are set, and plain group all-reduce otherwise. This settles w1b's "Could not verify" item 10 at the code level.

**What the training loop does when averaging fails (`hivemind.Optimizer`).**
- Default mode is "exactly **equivalent to synchronous training**" with the target batch size (`optimizer.py` line 36).
- If gradient averaging fails or times out, the peer logs "Averaging gradients failed" and steps with its own gradients ("Proceeding with local gradients", lines 595 to 610, 632 to 639). The docstring advises raising `averaging_timeout` if this happens "at least 25% of the time" (lines 122 to 123).
- If parameter (state) averaging fails, the peer logs "Averaging failed" and continues (`state_averager.py` lines 548 to 556).
- **A peer that falls behind** (its epoch differs from the swarm's) discards its local gradients and downloads parameters and optimizer state from a peer (`optimizer.py` lines 400 to 403, 655 to 673). The download loop retries forever on errors (lines 693 to 703).
- **Donors.** Peers announce themselves as state donors under `<prefix>.all_averagers` with priority equal to their epoch (`averager.py` lines 600 to 618; `optimizer.py` lines 502, 712). A downloader tries donors in priority order (`averager.py` lines 701 to 732) and refuses a state whose epoch is behind its own (`state_averager.py` lines 672 to 674). If no donor is listed, the download returns nothing (`averager.py` lines 696 to 699) and the peer continues from what it has (`state_averager.py` lines 667 to 669).
- **Swarm membership** for progress counting is DHT metadata that expires (`metadata_expiration` default 60 s, `progress_tracker.py` lines 58, 91); (inference) a peer that vanishes stops counting towards the target batch after at most that long.

**Experts that do not answer (`RemoteMixtureOfExperts`).**
- Parameters: `k_best`, `k_min` (default 1), `forward_timeout`, `timeout_after_k_min`, `backward_k_min` (default 1), `backward_timeout`, `detect_anomalies`, `allow_zero_outputs` (`moe.py` lines 39 to 44, 54 to 61).
- **Forward.** The client calls the chosen experts in parallel and waits until each sample has `k_min` answers, then waits at most `timeout_after_k_min` more, then cancels the rest (`_collect_responses`, lines 372 to 428, "cancel stragglers" line 380). Experts that failed get "zero outputs" and a mask of 0 (lines 198 to 199). Their logits are set to minus infinity before the softmax (lines 131 to 133), so the gate renormalises over the experts that answered. If fewer than `k_min` responses arrived, the forward raises `TimeoutError` (lines 248 to 249). (inference) That check counts responses over the whole batch, not per sample, though the docstring says "make sure at least this many experts returned output". (inference) Because line 248 raises first, `allow_zero_outputs` (zeros when no expert answers, lines 261 to 274) only takes effect with `k_min` = 0; with the default `k_min` = 1, no answer at all fails the forward pass.
- **Backward.** Experts that fail during backward "will be treated as constants (i.e. gradients through them are zeros)" (line 199); fewer than `backward_k_min` survivors raise `TimeoutError` (lines 344 to 345). A non-finite output with `detect_anomalies` counts as a failure (lines 431 to 442).
- **One holder per expert, by design.** A server declares each expert UID in the DHT as a single value naming its own peer (`dht_handler.py` lines 69 to 70); in DHT storage a newer expiration replaces an older value (`timed_storage.py` lines 80 to 84). When generating UIDs a server checks the DHT so that UIDs are "not yet occupied by other peers" (`server.py`, `_generate_uids` docstring, line 359). Declarations are refreshed every `update_period` (30 s) and expire after `max(2 × update_period, …)` (`dht_handler.py` lines 24 to 28). (inference) A dead server's experts stay listed until expiry; clients calling them see failures that the mask absorbs.
- **Persistence.** Expert weights are saved to the server's **local** `checkpoint_dir` (`checkpoints.py` lines 37 to 75, `checkpoint_last.pt`) and reloaded from it at start (`server.py` lines 160 to 167, 216 to 217). The only DHT write in `hivemind/moe` is the UID-to-peer declaration (`dht_handler.py` line 77, by grep). See B2 for the paper's different statement.

**Deliberate multiple holders?** In the Optimizer every peer holds the full model and optimizer state, so every part has as many holders as there are peers. In the MoE layer, no: one server per expert UID, and UID generation avoids collisions.

**Only holder disappears.** Averaging: the part a failed reducer was averaging stays local for that round only (nothing is lost; every peer kept its own copy). MoE: the expert is unavailable until some server serves that UID again; with local checkpoints, only the same machine (or whoever holds its disk) can restore it (inference from `checkpoints.py` and `dht_handler.py`).

**Central elements:** none in averaging or expert calls; DHT bootstrap peers are w1a's subject. Classification: none of (a), (b), (c) if the DHT runs on our machines only.

**Fit with R5 (inference):** the averager averages whatever tensor list it is given within whoever matches under a key, so an expert's holders could match under an expert-specific prefix. The code shows two behaviours relevant to R5: a holder that fails mid-round is excluded from the parts it had not sent, and if fewer than `min_group_size` = 2 holders show up, no all-reduce happens and each keeps its local copy. The MoE layer is the opposite of R5: one holder per expert.

**Question it raises for us:** when one of an expert's two holders fails mid-round, Hivemind would leave the survivor with a partly averaged expert (some parts averaged with the failed peer's early contribution, others local). Is a partly averaged expert acceptable, or must a round be all or nothing per expert?

### B2. Learning@home (DMoE paper), for what the code above does not show

- **Authors:** Max Ryabinin, Anton Gusev. "Towards Crowdsourced Training of Large Neural Networks using Decentralized Mixture-of-Experts". arXiv 2002.04013, **v3** (Wed 21 Oct 2020); NeurIPS 2020 per w1b S16. https://arxiv.org/abs/2002.04013
- **Read status:** sections read: §3.1 ("Fault tolerance", "Volunteer hardware", gating paragraph), §3.3 ("DHT Node" paragraph), §4.2 experiment description and the text after Figure 6. w1b S16 already covered the asynchronous update path; not repeated.
- **Failure handling:** experts that fail to respond are excluded from averaging, "similar to using Dropout" (§3.1). If a node leaves, "another can take its place by retrieving the latest expert checkpoints from the DHT" (§3.1); a runtime "regularly saves latest expert weights into the same DHT" (§3.3).
- **Disagreement with the code:** in Hivemind at `4bd43b7`, expert weights are checkpointed to local disk and the DHT holds only UID-to-peer records (B1). (inference) The paper's DHT persistence is not in the maintained code read; a lost expert server's weights are recoverable only from its own disk.
- **Measured effect of failures:** each expert fails to respond with probability 0.1 (§4.2); results are figures only (Figs. 5, 6). The authors report the 10% failure rate "has a positive effect" on WikiText-2 and attribute it to a dropout-like effect (text after Fig. 6). No number in the text.
- **R5 fit (inference):** one holder per expert, persistence by checkpoint; the opposite of R5.
- **Central elements:** the DHT used for expert lookup (classification as in B1); no others in the parts read.
- **Question it raises for us:** the paper and the code disagree on where expert weights persist; for Chorus, where does an expert's latest state live between rounds if both its holders go offline?

### B3. Moshpit SGD code (`yandex-research/moshpit-sgd`)

- **Authors of the code:** the Moshpit SGD authors (Ryabinin, Gorbunov, Plokhotnyuk, Pekhimenko); paper read in w1b S3. https://github.com/yandex-research/moshpit-sgd
- **Commit read:** `949b60b8461bf694a3b8e54b57952002eba81de1` (2025-02-04T14:21:20Z).
- **Read status (files read):** `averaging_experiments/averager.py` (lines 1 to 70, 110 to 142); `language_modeling/collaboration.py` (lines 20 to 32, 93 to 170); `language_modeling/requirements.txt` and `language_modeling/utils.py` (grep only).
- **Failure handling in the averaging simulation:** in `MoshpitAverager`, peers marked not alive keep their own values; alive peers average with `nanmean` along the round's grid axis, so a missing groupmate just shrinks the group (`averager.py` lines 125 to 142). The all-reduce baseline does nothing in any round with a failure: `if np.all(alive_mask)` average, else return the weights unchanged (lines 8 to 11). Gossip baselines renormalise their mixing rows over live peers (lines 25 to 37).
- **The ALBERT run's training loop** uses Hivemind 0.9.5's `DecentralizedAverager` (`requirements.txt` line 5; `utils.py` `SimpleAverager`). If the averaging step fails: "Averaging step failed, using local updates only." (`collaboration.py` lines 145 to 148). A peer behind the swarm's step reloads state from peers (lines 108 to 113). Defaults: `averaging_step_timeout` 30 s, `target_group_size` 64 (lines 25, 27).
- **Deliberate multiple holders / lost holder:** full replicas everywhere; nothing is held by one peer only.
- **Central elements:** initial peers only (`initial_peers`, line 22).
- **R5 fit (inference):** the simulation encodes the rule "a failed groupmate's value is dropped and the rest average", the per-group analogue of a 2-holder group falling to 1, where the survivor keeps its own value.
- **Question it raises for us:** with 2 holders, Moshpit's rule leaves the survivor with its own value; is one round of an unaveraged expert acceptable, and for how many consecutive rounds?

### B4. DeDLOC code (`yandex-research/DeDLOC`)

- **Authors:** the DeDLOC authors (paper read in w1b S4). https://github.com/yandex-research/DeDLOC
- **Commit read:** `10a9df8c2720b96bdbbfab997e8650e2ab45e41f` (2022-01-13T22:25:30+03:00).
- **Read status (files read):** `albert/arguments.py` (lines 18 to 56); `sahajbert/run_first_peer.py` (lines 40 to 62, 115 to 150); grep of `albert/run_aux.py`, `albert/run_first_peer.py` for the optimizer class.
- **Straggler and failure settings:** `averaging_expiration` 5 s, "Averaging group will wait for stragglers for at most this many seconds"; `averaging_timeout` 30 s, "Give up on averaging step after this many seconds"; `target_group_size` 256; `metadata_expiration` 30 s (`albert/arguments.py` lines 23 to 28, 51 to 54). Training uses `hivemind.CollaborativeOptimizer` (`albert/run_aux.py` line 243), the predecessor of B1's Optimizer.
- **Recovery after everyone leaves:** the "first peer" (coordinator) periodically calls `load_state_from_peers()` to pull the swarm's current state and pushes model and optimizer state to a Hugging Face repository with `git push` (`sahajbert/run_first_peer.py` lines 123 to 150; "repo in which coordinator will upload the model and optimizer states", lines 52 to 55). (inference) This is the only copy that survives every volunteer going offline.
- **Central elements:** the first peer (a long-running process; (a) if we ran it around the clock); the Hugging Face repository (b).
- **R5 fit (inference):** full replicas plus a periodic public copy; no partial holders.
- **Question it raises for us:** DeDLOC's public copy depended on a long-running first peer; without one, which peer publishes the round's state, and when?

### B5. Petals (code) and "Distributed Inference and Fine-tuning of Large Language Models Over The Internet" (paper)

- **Maintainers / authors:** bigscience-workshop (code). Paper: Alexander Borzunov, Max Ryabinin, Artem Chumachenko, Dmitry Baranchuk, Tim Dettmers, Younes Belkada, Pavel Samygin, Colin Raffel (arXiv abs-page `citation_author` metadata, fetched 2026-10-13 17:56). https://github.com/bigscience-workshop/petals ; https://arxiv.org/abs/2312.08361
- **Versions read:** code at `22afba627a7eb4fcfe9418c49472c6a51334b8ac` (2024-08-25); maintenance state is in w1a S8 (latest release v2.2.0, 2023). Paper **v1** (Wed 13 Dec 2023, only version).
- **Read status:** code files read: `src/petals/server/block_selection.py` (all, 95 lines); `src/petals/server/server.py` (lines 77 to 91, 125 to 127, 268 to 269, 328 to 402, plus grep); `src/petals/client/config.py` (all); `src/petals/client/routing/sequence_manager.py` (lines 138 to 200, 340 to 406, 536 to 543, plus grep); `src/petals/client/inference_session.py` (lines 318 to 395, plus grep); `src/petals/client/sequential_autograd.py` (grep). Paper sections read: §3.2, §3.3, §3.4 (failure paragraph), §4.1 with Table 1, the "Additional experiments" paragraph of §4.2, Appendix D, Appendix E. Not read: §1, §2, §3.1, §3.5, §4.2 tables, Appendices A to C, F (figures only).
- **Setting:** inference and parameter-efficient fine-tuning of frozen pretrained models (BLOOM, Llama 2) over volunteer GPU servers. Servers do **not** update their block weights during fine-tuning; clients hold the trainable adapters (§3.4: servers "do not update the server-side parameters").

**Several servers for the same block, on purpose.**
- The paper assumes "every block is hosted on several servers" (§3.2) and the load balancer makes it so.
- **Joining:** a server computes, per block, the total throughput of servers holding it, and picks the contiguous window whose sorted throughputs are lexicographically smallest, so it "would always cover a block with the smallest t_i" (Appendix D, rule (1); code `block_selection.py` lines 12 to 33).
- **Rebalancing:** every `random() × 2 × mean_balance_check_period` seconds (default 120 s, so 0 to 240 s) a server checks whether moving would improve the swarm (`server.py` lines 84 to 85, 369 to 380). It simulates its move and the other servers' greedy responses, and moves only if the bottleneck throughput improves enough: `actual_quality < balance_quality` with default 0.75 (`block_selection.py` lines 40 to 95; `server.py` line 84). The paper states a threshold of p = 20% (Appendix D). (inference) 0.75 corresponds to requiring about a 33% improvement, so code and paper differ; see "Could not verify".
- **A server never abandons a block it alone holds:** "Switching blocks would make the swarm disjoint" returns False when removing this server's throughput would leave some block at zero (`block_selection.py` lines 59 to 60).
- The paper's claim: the heuristic lets servers "quickly close the gaps" even if "up to 100%" of a block's servers leave (Appendix D, last paragraph).

**What a client does when a server leaves or times out.**
- Defaults: `request_timeout` 180 s, `connect_timeout` 5 s, `update_period` 60 s, `max_retries` unlimited unless `PETALS_MAX_RETRIES` is set, exponential backoff from `min_backoff` 1 s up to `max_backoff` 60 s, `ban_timeout` 15 s with doubling for repeated failures (`config.py` lines 24 to 31; `sequence_manager.py` line 113, `Blacklist(base_time=config.ban_timeout, backoff_rate=2.0)`).
- On a failed request the client bans the server temporarily and removes it from its routing table; if some block then has no server, it triggers a DHT refresh (`on_request_failure`, `sequence_manager.py` lines 388 to 401). When refreshing, banned servers are dropped "unless there are no peers left", because if all are banned "the error may actually be client-caused" (lines 356 to 370).
- **Inference (generation):** the client keeps the inputs it sent to each stage ("client-side cache", §3.2; `inference_session.py` line 56 "Used in case of server failures to regenerate attention caches on new servers"). On failure it finds a new route for the failed span and replays the history to rebuild the attention cache there (`_update_sequence`, lines 364 to 391; retry loop lines 324 to 357).
- **Fine-tuning forward/backward:** a failed pass is discarded and repeated through a new route (§3.4; `sequential_autograd.py` retry loops at lines 58 to 103 and 139 to 183).
- **No server holds the block:** `MissingBlocksError` "No servers holding blocks … are online" (`sequence_manager.py` lines 189 to 190, 536 to 543). (inference) With the default unlimited retries, the client keeps retrying with backoff until a server appears.

**Measured effects.**
- **Fault-tolerant inference, Table 1 (§4.1, v1):** BLOOM 7.1B, 4 stages, one GTX 1080 Ti per stage in one machine, failures simulated by resetting stages; steps per second at failure rates 0 / 1e-4 / 1e-3 / 1e-2. For 128 tokens: caching with restarts 17.1 / 16.7 / 12 / 0.18; cache-less 3.44 at every rate; Algorithm 1 11.4 / 11.4 / 10.6 / 3.38. For 1024 tokens: caching with restarts 15.5 / 11.8 / 0.48 / did not finish within 1 hour; cache-less 0.89 throughout; Algorithm 1 10.7 / 10.7 / 7.76 / 2.17. (The `-layout` text interleaves the rows; I re-extracted page 8 without `-layout` to assign values to rows.)
- **Load balancing under churn, Appendix E (figure only):** 206 CPU-only virtual instances with simulated throughputs, availability following a daily sine wave (about 100 to 110 active at peak, 15 to 25 at the trough). Full balancing "maintains connectivity throughout" and stays within "10 to 15%" of an upper bound most of the time; balancing only at join "quickly loses throughput when random servers leave"; random assignment "has zero throughput most of the time", unable "to form a complete pipeline".
- A "qualitative evaluation of fault tolerance by shutting down random servers" checked that outputs and gradients stay correct (§4.2, "Additional experiments"); no number.

**Only holder disappears.** Nothing is lost permanently: servers hold frozen pretrained blocks downloaded from the Hugging Face Hub (w1d S5), and clients hold their own trainable parameters and input caches. The block is unavailable until a server rebalances onto it or a new one joins (inference from Appendix D and `block_selection.py`).

**Central elements:** public swarm bootstrap peers and health API (w1a S8; (c) from our side); Hugging Face Hub for weights (b). A private swarm needs its own initial peers.

**Fit with R5 (inference):** the closest systems precedent for a rule that keeps more than one holder per part: joining servers go to the least-covered blocks, rebalancing closes gaps, and a sole holder never leaves its block voluntarily. But the rule maximises bottleneck throughput, not a minimum holder count; nothing in the code read enforces "at least 2 holders". And the parts are read-only, so losing a holder loses no training state.

**Question it raises for us:** Petals can afford a block with zero holders because the weights are on the Hub; an expert in training has state that exists only on its holders. Does R5's second holder protect state (unlike Petals) or only availability (like Petals)?

### B6. SWARM parallelism (paper Appendix A and code)

- **Authors:** Max Ryabinin, Tim Dettmers, Michael Diskin, Alexander Borzunov (arXiv metadata). ICML 2023 (repository README citation: PMLR volume 202). https://arxiv.org/abs/2301.11913 ; code https://github.com/yandex-research/swarm (licence and maintenance in w1b S5).
- **Versions read:** paper **v2** (Thu 29 Jun 2023). Code at `f66855f7266338b0cbad345e12e84c1229c03047` (2023-12-11).
- **Read status:** paper sections read: Appendix A answer "How much failure can SWARM handle?" (both paragraphs), Appendix C Algorithm 1 (stochastic wiring) and Algorithm 2 header plus the paragraph on straggling nodes, §4.4 with Table 5. w1b S5 read §3.2, §4.3, Appendix E; not repeated. The PDF's two-column layout interleaves, so I read these parts from a second `pdftotext` extraction without `-layout`. Code files read: `README.md` (lines 1 to 20); `swarm/pipeline/src/moe/client/balancer.py` (lines 21 to 146); `swarm/pipeline/src/moe/client/balanced_expert.py` (lines 78 to 154); grep of `swarm/pipeline/src/optim/collaborative.py`.
- **Setting:** pipeline-parallel pretraining over preemptible cloud T4s (400 in the main run, w1b S5).

**Several peers per stage, on purpose.** Every stage is served by a set of peers holding identical weights; the paper's fault tolerance rests on it: forward and backward passes survive "as long as there is at least one peer at the required stage" because activations can be resent "to another worker that has identical model weights by construction" (Appendix A).

**Peer leaving mid-step, stragglers, timeouts.**
- **Stochastic wiring (paper):** a trainer keeps, per stage, a priority queue of servers ordered by expected completion time from an exponential moving average of measured times; on `ServerFault` or `Timeout` it bans the server and retries with another (Appendix C, Algorithm 1, lines 11 to 13 and 31 to 32).
- **Code:** `ExpertBalancer.use_another_expert` picks the server with the smallest expected completion time (`balancer.py` lines 101 to 129). Any error bans the server except a gRPC `DEADLINE_EXCEEDED`, which only moves on to the next server ("response was too slow, choose the next expert", lines 135 to 144). A ban lasts until the server re-announces with a later DHT expiration (lines 55 to 61, 90 to 98). The trainer's forward and backward calls retry in an unbounded loop until some server answers (`balanced_expert.py` lines 119 to 129, 143 to 152).
- **A peer that leaves mid-step:** its accumulated gradients are replaced, since other workers "replace those accumulated by the disconnected peer" so the step keeps its number of examples (Appendix A). The data loader state "can be recomputed from the last known SGD step" (Appendix A).
- **Straggling peers in rebalancing:** peers wait "for straggling nodes … for a predefined timeout"; a node that reports late "is omitted from the current iteration" (Appendix C, paragraph before Algorithm 2).
- **Within-stage averaging** goes through a vendored copy of an older Hivemind averager and `CollaborativeOptimizer`; on a failed round it logs "Skipped averaging: averaging round failed" and continues; a peer more than `step_tolerance` (default 1) steps behind reloads state from peers (`collaborative.py` lines 83, 119, 184, 189 to 194, 219 to 220, 261). (inference) The failure semantics are those of B1's averager at an earlier version; not re-read line by line.

**Rebalancing and its measured effect.**
- Paper: every T seconds each peer writes its request-queue size to the DHT under its stage; one peer moves from the least loaded to the most loaded stage and downloads that stage's weights and optimizer statistics (Appendix C, Algorithm 2 and the paragraph after Algorithm 1). In the §4.3 run, "SWARM nodes run rebalancing every T = 300 seconds" (§4.3).
- **Code:** the README says "rebalancing between pipeline stages" is "not yet added to the repository" (`README.md` lines 8 to 9). So the cross-stage rebalancing is **paper only**; stochastic wiring is in the code.
- **Table 5 (§4.4), a simulation replaying the 32-hour peer-count trace of the T4 run**, removing departing peers from uniformly random stages, 10 seeds: percent of optimal throughput, overall / first hour / last hour: no rebalancing 82.7 / 99.0 / 45.4; T = 300 s 95.8 / 99.4 / 88.9; T = 60 s 97.6 / 99.8 / 91.7. (The table's cells are split across lines in both text extractions; this row assignment is inference from their order and from the text, which says T = 60 improves on T = 300.) The authors: without rebalancing the pipeline "drifts further" from optimal over time (§4.4).
- Figure 6 (figure only): with more stages (4 to 32) both strategies lose throughput because "the variances are too large while the number of peers is relatively too small" (§4.4).

**Only holder disappears.** SWARM works "without any issues" with "at least one operational peer at every pipeline stage" and one trainer (Appendix A). State lives on "all active nodes of a given stage" (Appendix A), so a newcomer downloads it from them. (inference) A stage whose last peer leaves stalls the pipeline, and its parameters and optimizer state are lost unless saved elsewhere; neither text read describes a checkpoint for that case.

**Central elements:** the DHT (stage membership, load reports); classification depends on who runs it (w1b S5).

**Fit with R5 (inference):** SWARM's survival condition is "at least one peer per stage", with several by design and peers moved to the most loaded stage. It is load-driven, not a holder-count rule, but it is the training precedent for "a part held by a group, averaged within that group, refilled by moving a peer".

**Question it raises for us:** SWARM moves a peer to a stage by having it download the stage's state from survivors. If an expert's group falls to one holder, can a third peer be assigned mid-run to fetch the expert from that holder before it too leaves?

### B7. Psyche (Nous Research): round timing, dropped clients, missing results

- **Maintainers:** Psyche Foundation / Nous Research. https://github.com/PsycheFoundation/nousnet (licence and maintenance in w1c S1).
- **Commit read:** `0bdb13d94a05675da93d69ffa5d4c4e5a680736c` (2026-03-20), the same commit as w1c S1.
- **Read status (files read, beyond w1c S1):** `shared/coordinator/src/coordinator.rs` lines 238 to 262 (config fields), 474 to 482, 554 to 588, 633 to 668, 677 to 702, 984 to 1130, 1174 to 1189; `shared/coordinator/src/data_selection.rs` lines 1 to 80; `shared/client/src/state/steps.rs` lines 60 to 100, 860 to 890, 1040 to 1075; `shared/client/src/client.rs` lines 136 to 150, 208 to 216, 640 to 656; `config/consilience/state.toml` lines 1 to 20; grep of `config/*/state.toml` for timing fields. w1c S1 already read and cited `train.rs` 540 to 690, the witness quorum and the consensus selection; not repeated.
- **Setting:** data-parallel training over the internet with a coordinator (Solana program or TCP server) and full model copies on every client (w1c S1).

**Round structure and timeouts (the straggler rule).**
- Run states: WaitingForMembers, Warmup, RoundTrain, RoundWitness, Cooldown, plus Paused and Finished (`coordinator.rs` lines 330 to 353). Each phase ends on a timer checked when someone ticks the coordinator (`check_timeout`, lines 1110 to 1113).
- **Training phase:** ends when `max_round_train_time` elapses (`tick_round_train`, lines 1002 to 1010), or earlier when every witness has submitted (lines 548 to 549). A trainer whose result is not out by then is simply not in the witnesses' bloom filters, and its batch reaches no consensus (inference from w1c S1: batches without consensus are skipped by every client).
- **Configured values in the repository:** `config/consilience/state.toml` (run ID "consilience-40b"): `warmup_time` 3600 s, `cooldown_time` 120 s, `max_round_train_time` 360 s, `round_witness_time` 5 s, `min_clients` 16, `init_min_clients` 16, `witness_nodes` 0 (lines 1 to 18). `witness_nodes` 0 means "all clients, up to 32" (`coordinator.rs` lines 477 to 481). Development configs use 30 s / 2 s / `min_clients` 2 (e.g. `config/kill-test-short-epoch-checkpoint/state.toml` lines 4 to 10). (inference) These are the settings shipped in the repository; whether the live Consilience run used exactly these was not checked.

**A client failing mid-round.**
- **One holder per batch.** Each round's global batch is split into one contiguous batch per trainer, assigned after a seeded shuffle; the map is `BatchId -> NodeIdentity`, one node per batch (`data_selection.rs` lines 7 to 60). Verifier and tie-breaker roles that would duplicate work are asserted off (`assert_eq!(…, 0) // TODO`, lines 22 to 23). (inference) If a trainer drops mid-round, its batch's contribution is missing; with no consensus commitment, every client skips it, so the step uses a smaller effective batch.
- **Being marked dropped.** Any client may send `health_check` naming peers; it is accepted only from round height 2 on, and only for peers the coordinator itself finds unhealthy (`coordinator.rs` lines 554 to 575); those peers go from Healthy to `Dropped` (lines 576 to 584). A client can also leave voluntarily (`withdraw`, lines 633 to 643).
- **Removal:** at the end of each witness phase and at cooldown, non-healthy clients are moved to `exited_clients` with the height they left at (`move_clients_to_exited`, lines 1024, 1082, 1174 to 1189).
- **Too few clients left:** at the end of a witness phase, if clients fall below `min_clients`, or witnesses fall below quorum, the epoch goes to Cooldown early (lines 1054 to 1063); in Warmup, too few clients send the run back to WaitingForMembers (lines 994 to 996). If no witness submitted at all, the coordinator cannot tell "only witness nodes disconnected or everyone disconnected" and withdraws everyone (lines 1026 to 1034). After cooldown the run waits for members again (line 1100). New clients join only at that point (w1c S1).

**A client missing an agreed result (confirming w1c S1).** w1c found that applying a consensus commitment whose payload a client lacks returns an `ApplyError` (`train.rs` lines 616, 623, 630). That error reaches the main loop through `run.apply_state(*new_state).await?` (`client.rs` line 213); the `?` returns it from the client's loop. A client whose step disagrees with the coordinator's run state also errors (`StepError::Desync`, `steps.rs` lines 872 to 878). A joiner that cannot fetch parameters from peers stops with "Peers were unreachable for P2P parameter requests. Try joining again" (`client.rs` line 653). (inference) A client that misses one agreed payload leaves the run and must rejoin at the next epoch; it does not apply a smaller set.

**Recovery after a crash.** A client that crashes is dropped by health checks or by missing results; it rejoins between epochs and downloads the model from peers or from the Hub checkpoint. If no client from the previous epoch remains, the coordinator switches the joiners to the Hub (or GCS) checkpoint, since "there will be no peers for P2P sharing" (`coordinator.rs` lines 945 to 959; w1c S1). After a completed epoch the checkpoint mode switches back to peer-to-peer (lines 1084 to 1092).

**Deliberate multiple holders.** Of the model, yes: every client holds the full model. Of a round's work, no: one trainer per batch. Verification by recomputation, which would duplicate batches, is unimplemented at this commit (w1c S1).

**Only holder disappears.** A batch: its update is lost for that step and skipped by all. The model: survives while any client is online, then on the Hub or GCS checkpoint written by checkpointer clients (w1c S1, w1d S2).

**Central elements:** the coordinator: Solana (c) or a TCP server (a) (w1c S1). Checkpoints on Hugging Face (b) or GCS. Unchanged from w1c.

**Fit with R5 (inference):** Psyche's rule for a lost contribution is "skip it, identically everywhere", and its rule for a client that cannot apply the agreed set is "leave". Both depend on the coordinator's record of which results count. There is no partial-holder notion.

**Question it raises for us:** Psyche makes a client that lacks an agreed payload leave rather than diverge. If an expert's agreed update for a round is held by a holder that went offline before others downloaded it, should the other holder skip that update everywhere or stop?

### B8. PCCL (Prime Collective Communications Library): paper, documentation and code

- **Authors:** Michael Keiblinger, Mario Sieg, Jack Min Ong, Sami Jaghouar, Johannes Hagemann (Prime Intellect) (arXiv metadata). Code: https://github.com/PrimeIntellect-ai/pccl (MIT, maintenance in w1c S7).
- **Versions read:** paper arXiv 2505.14065 **v1** (Tue 20 May 2025, only version). Code at `2af926aca81353415334fbd78434a6386b43c063` (2025-09-12T08:53:03Z).
- **Read status:** paper sections read: §2.5 (all, including 2.5.1 to 2.5.3), §2.6.1, §3.3.1 (all), the paragraph after Algorithm 6 in §4.1 (abort and restore). w1c S7 read §2.1 to §2.5.3, §3.3.1 first part, §8, §9 for membership and hashing; not repeated. Code and docs read: `docs/md/05-ImplementationNotes/03_MasterOrchestration.md` (all, 70 lines); `docs/md/04-API Overview/02_ErrorHandling.md` (all); `docs/md/04-API Overview/01_PCCL_API_Overview.md` (lines 228 to 300, plus grep); grep of `ccoip/src/cpp` and `tinysockets/` for timeouts and keepalive (`tinysockets/src/multiplexed_socket.cpp` lines 29 to 43; `tinysockets/src/server_socket.cpp` lines 25, 379).
- **Setting:** a collective-communication library for training over the internet, with a master process; tested by its authors in CI and in WAN all-reduce benchmarks.

**A groupmate failing during a collective.**
- "If a peer disappears mid-collective, PCCL cancels the current operation, marks the peer as gone" and lets the application "retry the collective without that peer" (§2.5).
- **All or nothing per collective:** on an I/O failure the operation "is aborted and unwinds and restores the buffer to its pre-operation state"; peers poll the master connection for an abort signal during the reduce (§4.1, paragraph after Algorithm 6). Contrast with Hivemind (B1), which keeps whatever parts were averaged.
- `pcclRankConnectionLost` means "a peer vanished mid-collective. You typically re-try the same reduce" (API overview, error handling of `pcclAllReduce`). `pcclAllReduceMultipleWithRetry` retries failed reduces and returns only when all operations succeed or "the local world size has dropped below 2" (API overview, `pcclAllReduceMultipleWithRetry`).
- If membership falls below a user threshold, "training can pause or wait for new arrivals" (§2.5).
- **Detection:** peer-to-peer sockets set TCP keepalive after 30 s idle (`multiplexed_socket.cpp` lines 29 to 43); the master's server socket uses a 60 s keepalive (`server_socket.cpp` lines 25, 379). (inference) A silent peer is detected by a socket error or keepalive expiry, not by an application-level timeout; I found no other timeout in the files grepped.

**Peers joining and leaving.**
- New peers wait in a registered state until accepted peers vote them in (§2.5.1). Membership changes, collectives and shared-state syncs never overlap: on a failure mid-collective, "PCCL aborts the operation, reconfigures membership", and only then starts the next collective (§3.3.1).
- For asynchronous (one-step-delayed) DiLoCo, a joiner syncs the outer state, resets its inner model, and does one extra shared-state sync to "eavesdrop" on the all-reduce it missed; the sync uses send-only or receive-only so that newcomers' state is never chosen (§3.3.1). Otherwise, if more peers joined than were present, "the pre-existing peers will loose hash popularity and the undesired state is chosen" (§3.3.1).
- The authors attribute fault tolerance to restricting legal transitions; earlier attempts "failed to achieve fault tolerance because the API was too permissive" (§2.5.3).
- **Measured:** CI stress tests of about 8 hours in which "Peers are spawned and killed randomly every 500-1000 milliseconds"; passing means the shared state advances correctly (§2.6.1). No training-quality number under churn.

**Recovery after a crash, and the only holder.**
- **Master crash:** "Master Crash = End of Run". There is "no built-in 'master re-election' or replication"; the recommended recovery is to restart the master, relaunch peers, and "Load from checkpoint" (`03_MasterOrchestration.md` lines 8 to 13).
- **Shared state is not retained:** CCoIP is "not designed to 'retain' shared state"; "If a run does indeed crawl to a halt, the shared state is lost", so peers should checkpoint to disk (line 15).
- **Last distributor leaves:** if the last peer that distributed the shared state leaves, "the shared state is effectively lost". New peers' revision counters then mismatch and no peer can synchronize "successfully again until the master is restarted" (lines 41 to 42). A peer reloading from disk restores the run only if its revision is exactly the expected one; otherwise the master must be restarted (lines 43 to 48).
- **Outlier peers** whose hashes differ from the popular one re-fetch from a peer with the popular state (lines 37 to 38, 50); if no peer offers its content for election, "all peers of the peer group will be kicked" (line 38).

**Deliberate multiple holders:** every accepted peer holds the bit-identical shared state (w1c S7); the master elects the popular version. No partial holders.

**Central elements:** the master process: **(a)** if we ran it; its crash ends the run (docs above). Peers need open ports or port forwarding (`03_MasterOrchestration.md` lines 65 to 71); no relays.

**Fit with R5 (inference):** PCCL's peer groups (it has a peer-group concept, `test_peer_groups.cpp` exists; not read) could in principle carry one group per expert. Its documented semantics for a lost last holder are stark: state lost until restart from a checkpoint. The library makes a collective all-or-nothing and requires the application to retry.

**Question it raises for us:** PCCL's rule is that a collective either completes for all current members or restores everyone's buffer. For an expert whose second holder dies mid-average, is "restore and retry with one member" (PCCL) or "keep the partly averaged parts" (Hivemind) the behaviour we want?

### B9. `prime-diloco` (INTELLECT-1's framework): elastic process group and retries

- **Maintainers:** Prime Intellect. https://github.com/PrimeIntellect-ai/prime-diloco (Apache-2.0; see w1c S5 for the repository-name correction).
- **Commit read:** `de5b9317da5f57247f11abed2fca259076795460` (2025-04-10), the same as w1c S5.
- **Read status (files read):** `src/zeroband/comms.py` (lines 17 to 26, 281 to 334 by grep and reading, 393 to 440); `src/zeroband/diloco.py` (lines 78 to 135); `src/zeroband/config.py` (line 74); grep of `src/zeroband/train.py` for live recovery. w1c S5 read `comms.py` lines 86 to 107, 336 to 360 and the INTELLECT-1 paper §2.4; not repeated.
- **Timeouts:** heartbeat every 2 s and a node "considered dead if no heartbeat is received" for 10 s by default (`comms.py` lines 21 to 26); the global key-value store timeout is 300 s and the global process-group timeout 600 s (lines 17 to 19). The paper's run used 6 s eviction (w1c S5, §2.4.3).
- **Peer leaving mid-round:** before each pseudo-gradient sync, the process group is re-resolved without admitting joiners (`diloco.py` line 84). If the all-reduce fails, the group is rebuilt and the sync retried, up to `retry_all_reduce` = 3 times (`diloco.py` lines 92 to 121; `config.py` line 74). After the last failure: "Resorting to calculating pseudo-gradient without reduce", i.e. the node applies its own pseudo-gradient alone (lines 122 to 132).
- **Leader failure:** non-leaders wait for the leader (global rank 0) to resolve the world, with the comment "TODO: Have a timeout here in case the leader is dead" (`comms.py` lines 407 to 414). (inference) If the rank-0 process that hosts the store dies, the others block.
- **Rebuild failures** recurse: "Error recreating process group … Retrying..." (lines 427 to 429).
- **Join and recovery:** a joiner receives model, outer optimizer, optimizer and scheduler state from a configured source rank (`train.py` lines 233 to 279; w1d S3).
- **Deliberate multiple holders / lost holder:** every DiLoCo replica holds the full model; nothing is held by one node only, except the key-value store on rank 0.
- **Central elements:** the rank-0 store (a) (w1c S5).
- **Fit with R5 (inference):** its fallback for a failed average is "apply your own pseudo-gradient", the same as Hivemind's "Proceeding with local gradients" (B1), at full-model granularity.
- **Question it raises for us:** `prime-diloco` retries a failed average three times before falling back; how long may a Chorus round wait for a missing holder before the survivor proceeds alone?

### B10. NoLoCo code: how outer-step groups are drawn (closes w1b's open item)

- **Authors:** Gensyn (paper read in w1b S8). https://github.com/gensyn-ai/noloco (MIT, w1b S8).
- **Commit read:** `a1b4a425bdc4050a356cf9f4bae7c383419703ab` (2026-03-26T12:17:56+02:00).
- **Read status (files read):** `src/noloco/sparse_optimizer_c.py` (all, 147 lines); `src/noloco/EL_optimizer.py` (all, 110 lines); `src/noloco/dipaco_pipeline.py` (lines 30 to 80, 140 to 175); `src/noloco/train.py` (lines 78 to 92, grep); the `optimizer:` block of every YAML file under `configs/no_reduce_exp/` (grep); `README.md` (grep).
- **Which code is NoLoCo's outer step:** the configs whose settings match the paper's NoLoCo description (H = 50, groups of n = 2; w1b S8) are the `*_noloco_mean_*` files, which select `noloco.sparse_optimizer_c.SparseOptimizerCBuilder` with `number_of_local_steps: 50`, `local_group_size: 2`, `outer_momentum: 0.5`. The files named `*_noloco_*` without `mean` select `PipelineDiLoCoOptimizerBuilder` with H = 100 and momentum 0.3, the paper's DiLoCo settings. (inference) The file names do not map one-to-one to the paper's method names; I identified NoLoCo by its settings.
- **How groups are drawn:** every `number_of_local_steps` steps, each worker computes `create_random_permutation(world_size, self._step)`, a NumPy `default_rng(seed + 1)` permutation seeded by **the local step counter**, then splits it into groups of `local_group_size` by striding, and finds its own group (`sparse_optimizer_c.py` lines 6 to 8, 19 to 25, 102 to 109). No process decides the pairing; every worker computes the same one from the step number. No run seed enters it. (inference) Every run with the same world size uses the same sequence of pairings.
- **The pipeline routing** is drawn the same way: the seed is `step + index` (training step plus micro-batch index), combined with the stage rank (`dipaco_pipeline.py` lines 42 to 43, 71 to 72, 157 to 158, 169 to 170). w1b recorded a "shared `seed`" from the paper's Algorithm 1; in the code it is the step counter.
- **The exchange within a group:** the group's first rank receives every member's previous outer weights and outer gradient with blocking `dist.recv`, averages them, and sends the means back; members `dist.send` then `dist.recv` (`sparse_optimizer_c.py` lines 28 to 56). The update then applies Nesterov-like momentum plus a pull towards the group mean (lines 57 to 66).
- **Partner unreachable, stragglers, churn:** none handled. The world is fixed by `torch.distributed.init_process_group` with the gloo backend and no timeout argument (`train.py` lines 81 to 85); the group size must divide the world size (`sparse_optimizer_c.py` line 83). (inference) A partner that stalls blocks its group's root, and through blocking send/recv everyone in that group, until torch.distributed's default timeout, which then raises; nothing in the code read skips or re-pairs. NoLoCo's churn tolerance is argued in the paper (w1b S8), not implemented in this repository.
- **Deliberate multiple holders / lost holder:** full replicas (data parallel) with pipeline stages replicated across the data-parallel dimension; a lost replica is not handled.
- **Central elements:** none in the algorithm; experiments use torch.distributed's rendezvous (a cluster launcher).
- **Fit with R5 (inference):** shows that a pairing rule computable by every peer from a counter needs no coordinator, but it assumes a fixed world in which every drawn partner is present. With churn, a deterministic pairing from the round number would pair peers with absent partners unless the draw is over the peers known to be present.
- **Question it raises for us:** if pairs or holder groups are drawn from the round number, over which set of peers is the draw made when some are offline?

### B11. Agora (Pluralis): stage replicas, averaging failures, self-termination, measured churn

- **Authors:** Gil Avraham, Violetta Shevchenko, Hadi Mohaghegh Dolatabadi, Karol Pajak, James Snewin, Harry Xi, Rodney O'Donnell, Thalaiyasingam Ajanthan, Sameera Ramasinghe, Chamin Hewa Koneputugodage, Shamane Siriwardhana, Alexander Long (arXiv metadata). Code: https://github.com/PluralisResearch/agora (Apache-2.0; w1c S11).
- **Versions read:** paper arXiv 2607.13332 **v1** (Tue 14 Jul 2026, only version). Code at `37d29a966528675635161007d7b43388012a98b2` (2026-07-04).
- **Read status:** paper sections read: §3.3.1 paragraphs "Rule-based worker self-termination", "Weight averaging", "All-reduce algorithm" and the fault-tolerance sentence; Algorithm 3 with its caption; §3.3.2 paragraphs "Worker discovery" and "Load-balanced forward pass and deterministic backward pass"; §3.5.2 "Stability testing results" and Figures 5 and 6 captions; §3.5.3 (all); §3.6.1 "Stage placement"; §3.6.2 "Health checks"; §5.1 setup paragraph on node counts; §5.3.2 (participation dynamics) with Figure 15 caption; §6.4 (all, with Tables 7 to 9 and Figures 44 and 45 captions). w1c S11 read §3 intro, §3.1, §3.2, parts of §3.3.1, §3.6.1, §3.6.2 for membership; not repeated. Code: grep of `agora/src/agora/configs/default.yaml` and `configs/reparam_llama/default.yaml` and `agora_server/src/agora_server/core/all_reduce/ar_runner.py` for timeouts. Section numbers below are from v1; w1c's "§5.7.1, §6.4" referred to the same paper's failure results, which in v1 sit in §3.5.3 and §6.4.
- **Setting:** Pluralis-8B, pipeline-parallel pretraining with five body stages plus head and tail; consumer GPUs from the public plus operator nodes; 40 days, 500B tokens (§5.1; w1c S11).

**Several holders per stage, on purpose.**
- "each stage is replicated across a changing set" of workers, each "holding one replica of exactly one stage" (§3.2). The Authorizer assigns stages so that no stage is under-served: without it, "frequently chosen stages would accumulate redundant replicas while others remained under-served" (§3.6.1, "Stage placement").
- The Health Monitor "checks that every stage retains enough serving replicas to keep the pipeline from stalling" and alerts operators (§3.6.2, "Health checks").
- In the run, only Pluralis-hosted workers ran the first 5,000 steps, "every stage running on 8 Pluralis nodes"; afterwards "the head and tail stayed on Pluralis nodes alone" (8 and 16 nodes), and "each body stage kept 4 Pluralis nodes", contributors making up the rest (§5.1). (inference) The operator kept a floor of its own replicas on every stage, so no stage depended only on volunteers.
- Figure 15d (figure only): each body stage held "about a fifth of the nodes throughout", so "no stage was starved or overloaded" (caption).

**A groupmate failing during averaging.**
- Same-stage replicas average a rotating 5% of their weights every 20 steps in the background (Algorithm 3 caption, "Pluralis-8B values"). Only operator nodes are reducers; contributors only send, because if a reducer left mid-average, "its slice could not be reduced" and every peer would keep "its own local values for that slice" (§3.3.1, "All-reduce algorithm").
- A sender past its per-chunk timeout "is banned and excluded from the round"; if the averaged slice does not come back, "the peer falls back to its local values", so the round finishes "with a partially reduced state" (§3.3.1). Algorithm 3, line 16: "on reducer timeout: keep local values for its slice".
- Timeouts in the run: matchmaking window 40 s, 2 MiB chunks, "sender / reducer timeouts 30 s / 60 s" (Algorithm 3 caption); the same values appear in `configs/reparam_llama/default.yaml` (lines 21, 48 to 49). The code's all-reduce runner (`ar_runner.py` lines 111 to 136, 263, 298, 339 to 350) carries the same sender/reducer timeout logic and docstrings as Hivemind's `AllReduceRunner` (B1). (inference) Agora's averaging is a derivative of Hivemind's; the failure semantics of B1 apply.
- Matchmaking: peers wait "up to a bounded matchmaking window" for the stage to register; the group is then fixed and "ordered deterministically so that every peer derives the same layout" (§3.3.1).

**A peer leaving mid-round, stragglers, timeouts (trainer side).**
- Trainers re-read each stage's workers from the DHT "about every 30 seconds"; a worker that goes offline "stops updating its entry in the DHT and is dropped"; trainers "temporarily ban workers that have failed to process a batch" and handle failures "using retries and temporary peer-banning policies" (§3.3.2, "Worker discovery" and the paragraph after).
- Forward passes go to the least-loaded replica; the backward "follows the same path the microbatch took during the forward pass" (§3.3.2). (inference) A microbatch whose forward replica leaves before its backward cannot be completed on another replica; the paper pins the backward deliberately because replicas drift between averaging rounds (§4.2.1 "Pinning the backward pass", seen by grep only, not read in full).

**Self-termination instead of eviction.** A worker that "fails two of its last three all-reduce rounds terminates itself", because a replica that keeps missing averaging "drifts from the stage consensus"; also on CUDA failure, invalid gradients, or "loss of peer-to-peer connectivity" (§3.3.1, "Rule-based worker self-termination"). It may rejoin through admission and the sync phases (same paragraph).

**Measured effects.**
- **Contributor failure injection** (5 stages, 16 workers, 5 simulated contributors at 100 to 200 ms RTT and 150 Mbit/s, Pluralis-8B payload; 1, 3 or 5 contributors preempted mid-send): "no noticeable effect on all-reduce completeness when observed from the remaining peers"; "Overall >90% of the required all-reduce payload is successfully communicated across rounds" (§3.5.3; Figure 6 caption).
- **Worker (reducer) failure injection** (7 stages, 12 workers; 4 workers preempted during send or during the reduced-chunk return): "only transient instability", partial all-reduces, then "perfect subsequent all-reduce rounds" (§3.5.3; Figure 7 caption).
- **Bandwidth stress** (CPU surrogate): at 200 Mbit/s, "<15% failure rate in all-reduce"; more failures at 100 and 50 Mbit/s; all-reduce time ">2.5×" baseline at 120 ms RTT; yet "partial all-reduce completeness still remains high" (§3.5.2, "Stability testing results").
- **Averaging failures against convergence (§6.4):** a 1B model, 16 workers per stage, forked near step 4,400, with injected gather hangs, gather exits, return hangs and return exits (Table 7) on a schedule from none through "1 in 5 rounds", "Every 2nd round", to every round (Table 9). Frequent failures made the loss trajectory "noticeably shallower around 3.1"; after faulty workers were pruned and reducer participation reached 100% "at approximately step 14k", the loss went "from roughly 3.04 to 2.97 by the end of the run" (§6.4). The authors read "an empirical operating threshold near 85%" of reducer participation, below which convergence "substantially" suffers (§6.4; Figure 45 caption). In a separate stress phase, about 19% (7 of 36) of stressed workers exceeded the averaging timeout and self-terminated, "yet the loss … overall stays on track" (Figure 44 caption).
- **Real churn in the run:** "669 nodes joined and 607 left over the run", at most 60 contributors admitted at a time, about 61 live on average (§5.3.2; joins and drops count events, footnote 6).

**Only holder disappears.** Not allowed to happen to head and tail (operator-only) and guarded for body stages by an operator floor of 4 replicas each (§5.1). Contributors load state from operator-written checkpoints and from peers (w1c S11). Nothing read describes a stage losing all replicas.

**Central elements:** Authorizer, Health Monitor, operator reducers and head/tail nodes (a); operator-written checkpoints on S3 (b-like) (w1c S11).

**Fit with R5 (inference):** Agora is the closest volunteer-training precedent for a minimum number of holders per part, but its floor is met by the operator's own always-on nodes (4 per body stage, 8 and 16 on head and tail), which R1 rules out for us. Its measured threshold (about 85% reducer participation) concerns averaging participation within a stage of 16 workers, not a group of 2.

**Question it raises for us:** Agora's floor of holders per stage is the operator's own fleet. With no fleet of ours, what keeps an expert's holder count from falling to zero when both its holders are volunteers on intermittent power?

### B12. Decoupled DiLoCo: one addition to w1b S1

- **Source:** arXiv 2604.21428 **v1** (Thu 23 Apr 2026). Read status for this strand: §3.2 "Adaptive Quorum Window" paragraph and Figure 3 caption only (PDF text; symbols in the equation were lost in extraction). Everything else is in w1b S1.
- **Addition:** the grace window that lets a K = 1 quorum wait for more learners is bounded by the slack that overlapping communication creates: "gathering a quorum, the grace window, and synchronizing a fragment must fit within" the overlap window of compute steps (§3.2; Figure 3 "adaptive quorum grace window fitting within the available slack"). (inference) The straggler rule is therefore time-boxed by construction: a learner later than the slack is left out of that fragment's merge, as w1b S1 recorded.
- **Holders:** every learner holds the full model; the syncer holds the canonical fragments (w1b S1). Lost learner: recovered from a peer learner (w1b S1, E.3). Lost syncer: restart from checkpoint only (w1b S1, E.2).

### B13. Bamboo: deliberate replication of each pipeline stage on its neighbour (cloud spot instances; contrast case)

- **Authors:** John Thorpe, Pengzhan Zhao, Jonathan Eyolfson, Yifan Qiao, Zhihao Jia, Minjia Zhang, Ravi Netravali, Guoqing Harry Xu (arXiv metadata). arXiv 2204.12013 **v1** (Tue 26 Apr 2022, only version). https://arxiv.org/abs/2204.12013
- **Read status:** sections read: abstract, §1 (paragraphs "Redundant Computation", "Reconfiguration", "Results"), §3 (Figure 3 and the checkpointing strawman), §5.1 (all, including "Level of Redundancy" and "Takeaway"), §5.2 "Lazy BRC and Recovery", §6 "Reconfiguration Triggering" and "Reconfiguration Policy". Read from a `pdftotext` extraction without `-layout` (two-column PDF). Not read: §7 tables (garbled), §2, §4.
- **Setting:** data-centre GPUs on AWS EC2 spot (preemptible) instances, built on DeepSpeed; not volunteer computing.
- **Deliberate multiple holders:** "Bamboo replicates the model partition on each worker node": each node stores its successor's layer shard ("its own model partition … on its predecessor node", §5.1) and runs forward redundant computation for it eagerly in pipeline bubbles, backward redundant computation lazily only after a preemption (§1, §5.1, §5.2). Exactly 2 holders per stage, by design.
- **Holder disappears:** the predecessor runs a failover schedule; "all the lost gradients must be re-computed" for the current iteration, then the shadow executes the victim's instructions "until a reconfiguration occurs" (§5.2).
- **Both holders disappear:** "Once consecutive instances are preempted, RC can no longer provide resilience"; Bamboo places consecutive nodes in different zones to make that rare (§1; §5.1 "Takeaway"), reconfigures, and keeps periodic checkpoints for "a rare fatal failure" (§6).
- **Why not more holders:** more redundancy would bring overheads "too significant to hide" (§1; §5.1 "Level of Redundancy").
- **Measured effect (cloud):** checkpoint-and-restart for GPT-2 on 64 spot p3.2xlarge instances spent 77% of training time on restarts and wasted work (§3, Figure 3). Bamboo "outperforms traditional checkpointing by 3.7×" in throughput and "reduces costs by 2.4×" against on-demand instances (abstract; §1 gives 3.6× cost reduction in "Results", a discrepancy within the paper). Bamboo needs a pipeline about "1.5×" deeper for the extra memory (§4 "User Interface").
- **Central elements:** Kubernetes-based framework and etcd for cluster state (§1, §6): (a).
- **Fit with R5 (inference):** a direct precedent for "2 holders per part, chosen so they are unlikely to fail together", with the explicit limit that losing both holders forces a rollback to a checkpoint.
- **Question it raises for us:** Bamboo separates the two holders across zones; are a pilot's two holders of an expert likely to fail together (same household, same power cut)?

### B14. Oobleck: f + 1 pipeline replicas for f simultaneous failures (cloud; contrast case)

- **Authors:** Insu Jang, Zhenning Yang, Zhen Zhang, Xin Jin, Mosharaf Chowdhury (arXiv metadata). arXiv 2309.08125 **v2** (Tue 7 Nov 2023). https://arxiv.org/abs/2309.08125
- **Read status:** sections read: abstract, §1 (contributions paragraphs), §2.2 and §2.3 (paragraphs on checkpointing and redundant computation, Figure 1 caption), §3 opening and §3.2 (fault-tolerance guarantee, Figure 2), §3.4 lifecycle paragraph, §5 opening paragraph (before §5.1, pipeline reinstantiation). Read from a non-layout extraction; the Greek symbol for the failure threshold is lost in the text, so I write f.
- **Setting:** data-centre GPU clusters and spot-instance traces; models from 340M to 6.7B (§7 opening).
- **Deliberate multiple holders:** Oobleck instantiates "at least f + 1 logically equivalent pipeline replicas" to tolerate "any f simultaneous failures" (abstract). Worst case: losing all replicas of one stage loses model state; in general it tolerates more failures provided "one copy of the entire model states is retained" (§3.2, Figure 2 text).
- **Holder disappears:** affected pipelines are re-instantiated from precomputed templates and "nodes copy missing layers from unaffected pipeline replicas" (§5 opening; §3.4). A job runs until "Oobleck cannot maintain f + 1 pipeline replicas" (§3.4).
- **Comparison with Bamboo:** Bamboo's redundant computation lowers throughput even without failures and still restarts "if two adjacent nodes fail" (§2.2). Oobleck reports "up to 29.6×" over Bamboo and Varuna as failures become frequent (abstract; §1).
- **Central elements:** a cluster-level execution engine (a); not examined further.
- **Fit with R5 (inference):** frames the holder count as a fault-tolerance parameter: with f + 1 copies of every part, any f simultaneous losses leave a copy to re-copy from. R5's "at least 2 holders" is the f = 1 case of this rule.
- **Question it raises for us:** Oobleck re-copies a lost part from a surviving replica before resuming; does a Chorus expert with one surviving holder get a new second holder in the same round or the next?

## Findings for question 6

Every statement below points to a source block (B1 to B14) or a wave-1 block, where the locators are. "(inference)" marks my reasoning. No design is recommended.

### F1. A groupmate failing during averaging: three behaviours in the code

| Behaviour | Systems (block) | What survivors end up with |
|---|---|---|
| **Partial round.** A failed sender is excluded from the parts it had not yet sent; a failed reducer's slice stays at each peer's local value; the round still completes | Hivemind averager (B1); Agora, whose all-reduce runner is a Hivemind derivative (B11) | Some parts averaged over the full group, some over fewer senders, some not averaged at all |
| **All or nothing, then retry.** The collective aborts, every buffer is restored, membership is reconfigured, the collective is retried without the peer | PCCL (B8); `prime-diloco` rebuilds the process group and retries up to 3 times (B9) | Either a complete average over the remaining members or no change |
| **Skip.** The failed member's contribution is dropped for that round, identically everywhere | Moshpit simulation, where absent peers keep their own values and the rest average (B3); Moshpit paper, groupmates "skip a round" (w1b S3); Psyche, where a batch with no witness consensus is skipped by every client (B7, w1c S1) | Survivors' average (Moshpit) or a smaller effective batch (Psyche) |

- **When averaging fails outright, every training loop read falls back to the peer's own update:** "Proceeding with local gradients" (Hivemind Optimizer, B1); "using local updates only" (Moshpit's ALBERT loop, B3); "Resorting to calculating pseudo-gradient without reduce" (`prime-diloco`, B9); "Skipped averaging" (SWARM's optimizer, B6). None of these blocks the run.
- **Psyche is the exception on the receiving side:** a client that lacks the payload of a result the witnesses agreed on does not apply a smaller set; it errors out of its loop and must rejoin at the next epoch (B7). So Psyche keeps every client's model identical at the cost of losing that client.
- **Where the sources disagree (inference from B1, B8, B11):** Hivemind and Agora accept partially averaged rounds; PCCL's authors argue that fault tolerance only became tractable by forbidding such intermediate states (§2.5.3 in B8). Agora measured that partial rounds are tolerable while reducer participation stays above about 85% (B11, §6.4). No source compares the two semantics on the same task.
- **Group too small:** Hivemind needs `min_group_size` (default 2) or the leader disbands and each peer keeps its local copy (B1). PCCL's retry helper gives up when the local world falls below 2 (B8). (inference) For a group of exactly 2 holders: if one is missing at matchmaking, Hivemind forms no group and each keeps its local copy; if one fails mid-round, the survivor keeps its own values except for any parts it was reducing to which the failed peer had already contributed. In PCCL the survivor's buffer is restored and a retry with one member is pointless, so the round amounts to no averaging.

### F2. Peers leaving mid-round, stragglers, timeouts: every tolerant system time-boxes the round

| System (block) | Straggler or failure rule | Default or run values found |
|---|---|---|
| Hivemind Optimizer (B1) | matchmaking window; sender stall bans; reducer stall leaves slice local; whole-round timeout | `matchmaking_time` 15 s; `averaging_timeout` 60 s; `next_chunk_timeout` = matchmaking time; reducer timeout = 2 × sender |
| DeDLOC (B4) | wait for stragglers, then give up | `averaging_expiration` 5 s; `averaging_timeout` 30 s |
| Moshpit ALBERT loop (B3) | step timeout, then local update | `averaging_step_timeout` 30 s |
| Agora (B11) | sender ban, reducer fallback, self-termination after 2 failed rounds in 3 | matchmaking 40 s; sender / reducer 30 s / 60 s |
| SWARM (B6) | deadline exceeded: try next server; other errors: ban until re-announce; rebalancing omits late reporters | not found in the files read |
| Petals client (B5) | ban with doubling, exponential backoff, unlimited retries by default | request 180 s; ban 15 s; backoff 1 to 60 s |
| Psyche (B7) | training phase ends on a timer; late results miss the witnesses; health checks drop peers | Consilience config: train 360 s, witness 5 s, `min_clients` 16 |
| `prime-diloco` (B9) | heartbeat eviction; retry all-reduce; then local update | heartbeat 2 s, dead after 10 s (6 s in the INTELLECT-1 run, w1c S5); 3 retries |
| PCCL (B8) | abort on socket error; retry | TCP keepalive 30 s (peer sockets), 60 s (master); no application timeout found |
| Decoupled DiLoCo (w1b S1, B12) | quorum K plus grace window bounded by the communication slack | K = 1 in the paper's runs |
| NoLoCo code (B10) | none: blocking send/recv in a fixed world | torch.distributed default |

- (inference) The common pattern is: a round has a deadline; whoever is late is left out of that round; the late peer either catches up by downloading state (Hivemind, SWARM, DeDLOC, PCCL) or leaves and rejoins later (Psyche, Agora's self-termination).
- Two places in the code read can wait indefinitely: non-leaders in `prime-diloco` waiting for a dead rank-0 leader ("TODO: Have a timeout here", B9), and NoLoCo's blocking pair exchange (B10), up to the library default.

### F3. Recovery after a crash

- **From peers:** Hivemind donors announced in the DHT, chosen by epoch priority, refusing older states (B1); SWARM stage peers (B6); Psyche peers serving layers, or the Hub checkpoint if no previous-epoch client remains (B7); `prime-diloco` live recovery from a configured rank (B9); PCCL re-fetch from the peer holding the popular hash (B8); Agora admission while the model downloads (w1c S11).
- **When no peer holds the state:** Hivemind returns nothing and the newcomer continues from what it has (B1); DeDLOC's first peer had pushed model and optimizer state to a Hugging Face repository (B4); Psyche falls back to the Hub or GCS checkpoint (B7); PCCL documents the state as "effectively lost" and requires a master restart and a disk checkpoint with the exact expected revision (B8); Hivemind MoE experts reload only from the server's own local disk (B1, B2).
- **Coordinator crash:** PCCL "Master Crash = End of Run" (B8); `prime-diloco`'s leader death blocks the others (B9); Decoupled DiLoCo's syncer restarts from a checkpoint (w1b S1). (inference) In every system with a coordinator, losing it is handled by restart from a saved copy, not by hand-over.

### F4. What happens when the only holder of a block, stage, expert or batch disappears

| Part (system, block) | Holders by design | When the last holder goes |
|---|---|---|
| Expert (Hivemind MoE, B1; Learning@home, B2) | 1; UID generation avoids sharing | Calls fail and are masked out of the gate; expert unavailable until its server returns; weights only on that server's disk (the paper's DHT persistence is not in the code) |
| Block (Petals, B5) | several, by load balancing | `MissingBlocksError`; client retries; servers rebalance onto the gap; nothing lost because weights are on the Hub |
| Stage (SWARM, B6) | several | Pipeline stalls; state survives only "on all active nodes of a given stage"; no checkpoint path found in the parts read |
| Stage (Agora, B11) | several, with an operator floor of 4 to 16 | Not reached: operator nodes hold every stage |
| Stage (Bamboo, B13) | 2 (own node + predecessor) | Both lost: reconfigure and roll back to a checkpoint |
| Stage (Oobleck, B14) | f + 1 pipeline replicas | All replicas of a stage lost: model state lost; guarantee holds up to f simultaneous failures |
| Shared state (PCCL, B8) | every accepted peer | Last distributor leaves: state lost until master restart and a disk checkpoint |
| Batch (Psyche, B7) | 1 trainer per batch | Its update is skipped by every client that step |
| Full model (Hivemind Optimizer, Moshpit, DeDLOC, Psyche, `prime-diloco`, Decoupled DiLoCo) | every peer | Lost only if every peer is gone; then only a published checkpoint remains (B1, B4, B7, w1d S4) |

### F5. Systems that keep several holders of the same part on purpose

- **Yes, as a coverage or throughput rule, in volunteer or preemptible settings:** Petals (joining servers take the least-covered blocks; rebalancing when the bottleneck improves enough; a sole holder never leaves its block, B5); SWARM (several peers per stage; cross-stage rebalancing in the paper, not in the released code, B6); Agora (the Authorizer places nodes on under-served stages; the Health Monitor checks "enough serving replicas"; the operator's own nodes form a floor, B11).
- **Yes, as a fault-tolerance invariant, in data-centre or cloud settings:** Bamboo (exactly 2 holders per stage, placed in different zones, B13); Oobleck (f + 1 replicas for f simultaneous failures, B14). Both enforce it with a central cluster manager.
- **Yes, for MoE, synchronously and without churn:** FoMoE's O_e holders per expert (w1b S17).
- **Explicitly no:** Hivemind MoE (one server per expert UID, B1); Psyche (one trainer per batch, B7).
- (inference) No volunteer system read enforces a hard minimum holder count per part without nodes the operator runs itself. Petals and SWARM optimise throughput, which tends to keep parts covered but guarantees nothing; Agora's guarantee is its own fleet; Bamboo's and Oobleck's guarantees need a cluster manager that can allocate replacements.

### F6. Measured effects of holders dropping out

- **Training quality under averaging failures:** Agora's §6.4 ablation (1B, 16 workers per stage, injected failures): convergence slowed while reducer participation stayed below about 85% and recovered once failing workers were removed (B11). This is the only training-quality measurement under churn found in this strand; it is for stages of 16 replicas, not groups of 2.
- **A real volunteer run with churn:** Agora's Pluralis-8B run absorbed 669 joins and 607 departures with an operator floor on every stage (B11). DeDLOC's sahajBERT run (w1b S4) is the other real volunteer run; both are far larger groups than ours.
- **Throughput or availability only:** Petals Table 1 (fault-tolerant inference at failure rates up to 1e-2) and Appendix E (load balancing under a daily sine-wave of servers; random placement "has zero throughput most of the time", B5); SWARM Table 5 (no rebalancing falls to 45.4% of optimal in the last hour of a 32-hour trace replay, against 88.9% and 91.7% with rebalancing, B6); Bamboo (checkpoint-restart wasted 77% of time on 64 spot instances; 3.7× throughput over checkpointing, B13); Oobleck (up to 29.6× over Bamboo and Varuna, B14).
- **Quality with expert failures:** Learning@home, 10% non-response, figure only, reported as harmless or even helpful on WikiText-2 (B2).
- **w1b's gap item 3** ("no LM result with real departures at 100M to 300M") stays open: Agora's results are at 1B and 8B, and nothing measures a group of holders shrinking from 2 to 1 or 0.

### F7. Where sources disagree with themselves or with their code

- Learning@home's paper says expert weights are saved into the DHT for persistence (§3.1, §3.3); Hivemind's code saves them to local disk and stores only UID-to-peer records in the DHT (B2, B1).
- Petals' paper gives a rebalancing threshold p = 20% (Appendix D); the code's default `balance_quality` 0.75 corresponds to about 33% (inference, B5).
- SWARM's paper describes cross-stage rebalancing and reports it in §4.3 and §4.4; the repository README says rebalancing is "not yet added" (B6).
- NoLoCo's paper describes a shared `seed` for routing (w1b S8); the code seeds both routing and outer-step pairing with the step counter (B10).
- Bamboo's abstract gives a 2.4× cost reduction against on-demand instances; its §1 gives 3.6× (B13).
- Hivemind keeps partially averaged rounds; PCCL forbids them (F1).

### F8. Central elements met in this strand, classified

| Element | Systems | Class |
|---|---|---|
| DHT among peers (matchmaking, membership, donors) | Hivemind, Moshpit, DeDLOC, SWARM, Petals, Agora | none of (a), (b), (c) if run only among our machines; (c) if public (w1a) |
| Long-running first peer or coordinator | DeDLOC first peer (B4) | (a) if run around the clock |
| Coordinator or master | Psyche on Solana (c) or TCP (a) (B7); PCCL master (a) (B8); `prime-diloco` rank-0 store (a) (B9); Decoupled DiLoCo syncer (a) (w1b S1) | as stated |
| Admission, health monitoring, operator replicas | Agora (B11) | (a) |
| Cluster manager | Bamboo (Kubernetes, etcd), Oobleck (B13, B14) | (a) |
| Published checkpoints | DeDLOC and Psyche on Hugging Face; Psyche GCS; Petals weights on the Hub | (b) |
| Public swarm bootstrap and health API | Petals (w1a S8) | (c) from our side |

### F9. Bearing on R5 (all inference)

- R5 asks for at least 2 holders per expert per round. The sources read give two different reasons for keeping several holders, and they lead to different rules:
  1. **Availability or throughput** (Petals, SWARM, Agora): a part with zero live holders stalls work but loses nothing permanent only where a public copy exists (Petals) or the operator holds a floor (Agora).
  2. **Not losing state** (Bamboo, Oobleck, PCCL's warning): with f + 1 holders, f simultaneous losses leave a copy to re-copy from; losing all holders means rolling back to a checkpoint.
- For Chorus slices, an expert's training state between checkpoints exists only on its holders, so the second reason applies (inference from F4). R5's 2 holders is Oobleck's f = 1 case: one loss per round per expert is survivable, two are not, unless a published copy of the expert from an earlier round exists.
- The code read offers three precedents for what the surviving holder does that round: keep a partly averaged expert (Hivemind), restore and average with itself only, i.e. keep its own update (PCCL, Moshpit), or have everyone skip that expert's update (Psyche's rule for batches). No source measures which is better for an expert.
- Bamboo's placement of the two holders in different failure domains (zones) has a home analogue the sources do not test: two holders whose failures are correlated (same household power, same ISP) give less protection than the count suggests.

### Unknown after this strand

- Quality effect of a 2-holder expert group dropping to 1 or 0 holders mid-round, under any averaging rule.
- Whether any volunteer system enforces a minimum holder count without operator-run nodes.
- How holder-group averaging behaves asynchronously (w1b's gap, unchanged).

## Could not verify

- **Petals rebalancing threshold:** the paper's p = 20% (Appendix D) against the code's `balance_quality` = 0.75 (`server.py` line 84); my reading that 0.75 means about a 33% improvement is inference from `block_selection.py` lines 88 to 95. Not reconciled.
- **SWARM Table 5 row assignment:** the T = 300 s and T = 60 s first-hour and last-hour cells are split across lines in both text extractions; I assigned them by order and by the text's statement that T = 60 is better. Petals Table 1 was re-extracted without `-layout` and is less uncertain.
- **Whether SWARM's §4.3 and §4.4 experiments used rebalancing code** that is absent from the public repository.
- **Psyche's live Consilience settings:** the repository's `config/consilience/state.toml` values may not equal those of the run.
- **Hivemind `k_min` counting:** that the check at `moe.py` line 248 counts responses over the whole batch rather than per sample is my reading of the code; not tested.
- **Hivemind `_load_state_from_peers` timeout:** lines 685 to 686 replace a caller-supplied timeout with `next_chunk_timeout` or `request_timeout`; whether this is intended was not traced.
- **Learning@home DHT persistence:** may exist in the older `mryab/learning-at-home` code; only current Hivemind was read.
- **NoLoCo default timeout:** the torch.distributed default timeout for the gloo backend in the version NoLoCo pins was not checked.
- **Agora's backward pinning under failure:** what a trainer does when the forward replica has left before the backward (§4.2.1) was seen by grep only.
- **PCCL peer groups:** `ccoip/tests/end_to_end/test_peer_groups.cpp` exists but was not read, so whether one PCCL run can hold several independent averaging groups (one per expert) is unconfirmed.
- **Bamboo cost figures:** 2.4× (abstract) against 3.6× (§1, "Results"); not reconciled.
- **Agora's 85% threshold** comes from one ablation run (§6.4); no repeat or variance is reported in the parts read.

## Gaps

- **No source measures what happens to quality when an expert's (or any part's) holder group of 2 falls to 1 or 0 mid-round,** under any averaging rule. Agora's §6.4 is the nearest, with groups of 16.
- **No volunteer system read enforces a hard minimum holder count** without the operator's own nodes; Bamboo and Oobleck enforce one with a cluster manager in the cloud.
- **Node0 code** was cloned (`32bd084de15dbdc8e30723ad66db7d01acf70c03`) but not read; Agora's code was read only by grep for timeouts.
- **Not read in this strand:** Templar and Covenant churn handling (outside the named list); Gensyn GWTF; in-memory checkpoint replication systems for data centres (for example Gemini) and expert-replication schemes for MoE load balancing (for example shadow experts); Varuna; DiLoCoX; Petals Appendix F and SWARM Figure 6 (figures only); Bamboo §7 tables (garbled).
- **Decoupled DiLoCo** received only the grace-window addition; its failure simulations are in w1b S1.
- **No measurement on home connections** of any failure-handling mechanism; all timings are from data-centre, cloud or simulated links.
- **GitHub maintenance data** was not re-queried with `gh api` in this strand; commit SHAs and dates come from the clones, and licences and `pushed_at` from wave 1.

## Query log

| Time (TST, 2026-10-13) | Tool or site | Action |
|---|---|---|
| 17:53 | local | Read the brief and wave-1 notes w1b (full), w1c (S1, S5 to S12, findings, could-not-verify, gaps), w1a (S7, S8), w1d (S1 to S5, Q5b) |
| 17:54:57 to 17:55:56 | github.com (`git clone --depth 1`) | hivemind, petals, swarm, moshpit-sgd, nousnet (Psyche), pccl, prime-diloco, noloco, node0, agora, DeDLOC; HEADs recorded per source block |
| 17:56:13 to 17:57:10 | arxiv.org abs pages (`curl`, `sleep 3` between) | 2301.11913, 2505.14065, 2607.13332, 2312.08361, 2209.01188, 2204.12013, 2309.08125 (first fetch failed, refetched ≈17:57:15), 2002.04013: titles, versions, `citation_author` metadata |
| 17:57:32 to 17:58:48 | arxiv.org PDFs (`curl`, `sleep 3` between); `pdftotext -layout` | 2301.11913v2, 2505.14065v1, 2607.13332v1, 2312.08361v1, 2204.12013v1, 2309.08125v2, 2002.04013v3, 2604.21428v1. 2209.01188 (Petals 2022) abs page only; PDF not fetched |
| ≈17:58 to 18:05 | local clone | Hivemind averaging, optim and MoE files (B1); Learning@home PDF passages (B2); Moshpit and DeDLOC scripts (B3, B4); notes B1 to B4 written |
| ≈18:05 | advisor | Review of approach; fixes applied (read status of B3, `allow_zero_outputs`, coverage-gap mapping) |
| ≈18:06 to 18:12 | local clone and PDF | Petals code and 2312.08361v1 §3.2 to §4.1, App. D, E; page 8 re-extracted without `-layout` for Table 1 (B5) |
| ≈18:13 to 18:17 | local clone and PDF | SWARM README, balancer, balanced expert, optimizer grep; 2301.11913v2 re-extracted without `-layout`; App. A, App. C, §4.4 (B6) |
| ≈18:17 to 18:21 | local clone | Psyche coordinator, data selection, client loop, configs (B7) |
| ≈18:21 to 18:25 | local clone and PDF | PCCL docs, API notes, socket keepalive grep; 2505.14065v1 §2.5, §2.6.1, §3.3.1, §4.1; `prime-diloco` comms, diloco, config (B8, B9) |
| ≈18:25 to 18:28 | local clone | NoLoCo optimizers, pipeline routing, configs (B10) |
| ≈18:28 to 18:33 | local clone and PDFs | Agora §3.3 to §3.6, §5.1, §5.3.2, §6.4 and config grep (B11); Decoupled DiLoCo §3.2 grep (B12); Bamboo and Oobleck re-extracted without `-layout` (B13, B14) |
| 18:34 to ≈18:45 | local | Findings, could-not-verify, gaps written after a network interruption; file re-read once to confirm B1 to B14 intact |

WebSearch and WebFetch were not used in this strand; all sources were already named in the brief, the wave-1 notes, or the reference lists and repositories read. `gh api` was not queried: commit SHAs and dates come from the clones (`git rev-parse HEAD`, `git log -1 --format=%cI`); licences and `pushed_at` are wave 1's.

**Not covered:** Node0 code (cloned, not read); Templar and Covenant churn; Petals 2022 paper (2209.01188, abstract page only); SWARM §4.3 run details beyond the rebalancing period; Petals Appendix F and SWARM Figure 6 (figures only); Bamboo §7 and Oobleck §7 result tables; Varuna, Gemini, GWTF, DiLoCoX, MoE expert-replication schemes; Hivemind DHT behaviour when bootstrap peers vanish (w1a's subject); any measurement on home connections.
