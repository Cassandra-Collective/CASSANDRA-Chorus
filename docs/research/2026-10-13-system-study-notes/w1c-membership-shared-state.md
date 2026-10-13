# Strand w1c: membership, the current model, and who writes shared state (questions 3 and 7)

| | |
|---|---|
| Date | 2026-10-13 (machine clock "TST") |
| Scope | Questions 3 and 7 of `docs/research/2026-10-13-system-study-brief.md` only. Discovery and NAT, averaging algorithms, storage limits, code trust, bandwidth, maintenance and churn are other strands |
| Method | Raw sources only: arXiv PDFs via `pdftotext -layout`; READMEs and docs via raw.githubusercontent.com; code read from shallow clones (never run, built or installed); GitHub data via `gh api`. WebSearch only to discover sources. "(inference)" marks my reasoning |
| Status | Complete for this strand (15 source blocks, findings, could-not-verify, gaps, query log). Quotations checked mechanically for the 15-word limit; no em or en dashes |

## Sources

### S1. Psyche (Nous Research; Psyche Foundation)

- **Maintainers:** Psyche Foundation / Nous Research. Software.
- **Repository:** https://github.com/PsycheFoundation/nousnet. `gh api repos/PsycheFoundation/psyche` (2026-10-13 17:19 TST) returned `full_name` "PsycheFoundation/nousnet", so the old path redirects. `license.spdx_id` Apache-2.0; `pushed_at` 2026-03-24T20:46:58Z; `archived` false.
- **Version read:** shallow clone, HEAD `0bdb13d94a05675da93d69ffa5d4c4e5a680736c`, commit date 2026-03-20T19:58:10Z.
- **Read status (files read):**
  - Docs (the in-repo "Psyche book"): `psyche-book/src/explain/index.md` (all), `explain/general-workflow.md` (all), `explain/model-sharing.md` (all), `explain/rewards.md` (all), `explain/glossary.md` (all), `enduser/authentication.md` (all), `explain/gcs-checkpoints.md` (lines 1 to 40), `development/running-offchain.md` (lines 1 to 30), `architectures/centralized/README.md` (lines 1 to 39).
  - Code: `shared/coordinator/src/coordinator.rs` (constants lines 18 to 24; lines 500 to 770; lines 917 to 1000), `shared/coordinator/src/committee_selection.rs` (lines 1 to 140), `shared/coordinator/src/commitment.rs` (all), `shared/client/src/state/train.rs` (lines 540 to 690), `shared/client/src/state/steps.rs` (lines 596 to 640), `shared/client/src/client.rs` (lines 180 to 200), `architectures/decentralized/solana-coordinator/programs/solana-coordinator/src/lib.rs` (lines 160 to 367), `.../instance_state.rs` (lines 76 to 84, 397 to 427), `shared/network/src/lib.rs` (lines 135 to 142, 340 to 385, 984 to 1010). Plus a grep of the whole tree for `verification_percent`, `tie_breaker_tasks`, `Committee::Verifier`, `Committee::TieBreaker`.
- **What it is:** a system for data-parallel training over the internet: a coordinator state machine, clients that train and exchange DisTrO-compressed results peer to peer over iroh, and witnesses.

**Membership.**
- One coordinator per run is "a source of truth for global state" (`explain/index.md` line 5). It exists in two forms: a Solana program, or "a regular TCP server" (same line). The TCP form is described as "mostly used to test local runs and as a dev oriented tool" (`explain/index.md` line 11).
- Clients join between epochs. On Solana a client calls `join_run`; it goes onto a pending list, and the coordinator's `tick` admits pending clients once `init_min_clients` is reached and an extra waiting time has passed (`coordinator.rs` lines 917 to 980, `tick_waiting_for_members`). At most `SOLANA_MAX_NUM_CLIENTS` = 256 clients (`coordinator.rs` line 18).
- Who may join is set on chain. A run's `join_authority` key issues `authorization`s to user master keys, which name delegate keys; a run is "Permissioned" (whitelisted keys) or "Permissionless" (`enduser/authentication.md` lines 11 to 23). A run's `main_authority` is "the only key that is allowed to modify the run's configuration" (line 11); in the program, `update`, `set_paused`, `update_client_version` and `set_future_epoch_rates` require `main_authority` as signer (`lib.rs` lines 184 to 241, 325 to 345).
- `tick` is permissionless: "anybody using Solana can tick the Coordinator forwards" (`general-workflow.md` line 208; `lib.rs` line 243 uses `PermissionlessCoordinatorAccounts`).
- Removal: witnesses' bloom filters give each trainer a score; a trainer is healthy if the score reaches the witness quorum (`coordinator.rs` lines 724 to 747). Any client can send a `health_check` naming a peer; if the coordinator's own check finds that peer unhealthy it is marked `Dropped` (`coordinator.rs` lines 554 to 587).
- The peer-to-peer layer admits only the coordinator's current participants: the client sets its iroh allowlist to `participating_endpoint_ids(new_state)` on every state update (`client.rs` lines 193 to 194).

**Current model, merging and checking.**
- There is no stored "current model" in the coordinator. Every client starts an epoch from the same checkpoint and then applies, every step, the same set of other clients' results, which "keeps everyone's copy of model identical within an epoch" with no extra full synchronization step (`explain/model-sharing.md` line 7).
- Which results are applied is computed by every client from public inputs. For each batch ID, the client calls `select_consensus_commitment_by_witnesses(commitments, witnesses, witness_quorum)` with the on-chain witness records of the previous round (`train.rs` lines 548 to 605). That function scores each commitment by how many witnesses' `broadcast_bloom` contain its hash, keeps those at or above the quorum, and takes the highest (`coordinator.rs` lines 749 to 769). Batches with no consensus are skipped (`train.rs` lines 600 to 603).
- Quorum: for 1, 2 or 3 witnesses it is 1, 2 and 2; above that it is two thirds (`WITNESS_QUORUM_RAIO` = 2/3, `coordinator.rs` line 24 and lines 710 to 722). At most 32 witnesses (`SOLANA_MAX_NUM_WITNESSES`, line 19).
- Witnesses and data assignment come from a seed the coordinator provides (`general-workflow.md` lines 67 and 73). On Solana the seed is the first 8 bytes of a SHA-256 over exactly two inputs, the block clock's unix timestamp and slot (`instance_state.rs` lines 76 to 85).
- What a client checks: each broadcast's commitment is an ed25519 signature over a SHA-256 data hash (`commitment.rs`; signing at `client.rs` lines 437 and 466). On receiving a payload, the client recomputes its hash and drops it if it does not match the commitment (`steps.rs` lines 607 to 619). A code comment reads "TODO: verify shape of distro_results" (`steps.rs` line 600).
- What is **not** checked at this commit: the docs list a "Verifying" task that recomputes results "to identify and punish malicious participants" (`explain/index.md` line 57), but in the coordinator the `Verifier` and `TieBreaker` committee branches are `todo!()` (`coordinator.rs` lines 701 to 702), and data selection asserts `verification_percent` is 0 with a `// TODO` (`data_selection.rs` lines 22 to 23). The client also trusts a peer's self-reported warm-up counter: "we are relying on honest communication of this value here" (`train.rs`, comment inside lines 634 to 640).
- So (inference) witnesses attest that a result was **received and matched its signed hash**, not that it was computed correctly. A participant who trains honestly on garbage, or submits a well-formed but poisoned update, is applied by every peer.

**Who writes shared state.**
- On chain: the run creator (`main_authority`) writes configuration; the `join_authority` writes authorizations; any participating client writes join, witness (if selected), health-check and checkpoint transactions; anyone may tick.
- Checkpoint pointer: "a client or a set of clients can optionally run as checkpointers" and upload to Hugging Face, then "send the URL for this checkpoint to the coordinator" (`model-sharing.md` line 17). The glossary calls checkpointers "Designated, trusted participants" (`glossary.md` line 31). In code, however, the Solana `checkpoint` instruction only checks that the signer is a client of the current epoch (`instance_state.rs` lines 397 to 414, error `SignerNotAClient`), and the coordinator overwrites the pointer with the last one received (`coordinator.rs` lines 598 to 600, comment "this will overwrite the checkpoint with the last checkpointed one").
- After the first epoch new joiners download the model from peers, layer by layer from different clients (`model-sharing.md` lines 9 and 19 to 21). If no previous-epoch client is present, the coordinator falls back to the Hub checkpoint (`coordinator.rs` lines 946 to 959).
- Upload credentials: the checkpointer holds its own Hugging Face token (example `--hf-token` in `architectures/centralized/README.md` line 33) or a GCS bucket with billing (`gcs-checkpoints.md` lines 1 to 40).

**What it keeps central, classified.**
- Coordinator on Solana: **(c)**. Coordinator as TCP server: **(a)**, and the docs call that mode a development tool.
- Checkpoints on Hugging Face (or GCS): **(b)** for Hugging Face; GCS needs a billing account (owner-paid storage, inference: closer to (a) in cost, but not a server we run).
- iroh relays: three modes, `Disabled`, `N0` (iroh's default public relays) and `Psyche` (two Psyche-run relay hosts, US East and US West) (`network/src/lib.rs` lines 135 to 142, 350 to 353, 984 to 1006). n0 relays are **(c)**; Psyche-run relays would be **(a)** for whoever runs them.
- Address lookup: `DiscoveryMode::N0` uses n0's DNS and pkarr publisher (`network/src/lib.rs` lines 369 to 373): **(c)**. A `Local` mode exists for tests.

**What a mistake or a malicious participant could do (code read; consequences are inference).**
- A client in the epoch can repoint the checkpoint URL that new joiners use (the program checks only membership). Honest mistake: a typo or a private repo strands newcomers when no previous-epoch peer is online.
- A client can submit a validly signed but harmful update; with verification unimplemented, it is applied by all.
- A witness can omit peers from its bloom filter. With 3 or more witnesses one withholding witness cannot remove a result alone (3 witnesses: quorum 2; 4: quorum 2; above that, two thirds). With 2 witnesses the quorum is 2, so one withholding witness removes a batch's result (inference from `coordinator.rs` lines 710 to 722).
- The `main_authority` key can change the run's model, config and progress at any time through `update` (inference from `lib.rs` lines 184 to 194; whether `update` refuses while active was not read).

**Fit with R1 to R7 (inference).**
- R1: partly. The Solana coordinator is not a server we run, but needs a public chain (c). The TCP coordinator is a server (a).
- R2: not as built: Solana is not on the R2 list.
- R3: partly: relays can be disabled; with them disabled, connectivity rests on direct connections (strand 2).
- R4: not met: rounds are synchronous steps with a witness barrier (a synchronous design).
- R5 and R6: not addressed: every client trains the full model (data parallel). No slice or expert-holder notion was found in the files read.
- R7: shows a ledger option concretely: membership, witnesses and the checkpoint pointer on chain.

**How its setting differs from ours.** Permissionless or permissioned runs of up to 256 clients with a public chain as referee; data parallel with compressed per-step results; no expert slicing.

**Question it raises for us.** The "merge rule every peer computes" is already how Psyche defines its model (every client applies the witness-selected results). What replaces the chain's witness records as the agreed public input if there is no ledger: signed per-peer files on a public host?

### S2. Templar (software; Bittensor subnet 3)

- **Maintainers:** Templar / Covenant AI. Software.
- **Repository:** https://github.com/one-covenant/templar. `gh api repos/tplr-ai/templar` (2026-10-13 17:19 TST) returned `full_name` "one-covenant/templar"; `license.spdx_id` MIT; `pushed_at` 2026-10-04T16:14:55Z; `created_at` 2024-12-05T17:10:20Z; `archived` false.
- **Version read:** shallow clone, HEAD `0fefc2ad763cd4cfda080e58267fe562455f3b45`, commit date 2026-10-04T17:14:54+01:00.
- **Read status (files read):** `README.md` lines 1 to 140; `src/tplr/chain.py` lines 133 to 200 plus the function index; `src/tplr/comms.py` lines 220 to 280, 516 to 544, 1631 to 1700, 2225 to 2340 plus the function index; `neurons/miner.py` lines 290 to 300 and 715 to 800; `neurons/validator.py` function and keyword index (grep), lines 406 to 409, 458 to 510, 959 to 973, 1084 to 1164 headers; `src/tplr/neurons.py` lines 559 to 599, 839 to 1010, 1194 to 1224.
- **Status note:** the README says "Templar is dormant" and the protocol "is not currently active" (lines 22 to 24); subnet 3 now runs a different competition.
- **What it is:** the code behind the Templar runs and Covenant-72B: miners train and publish compressed pseudo-gradients to their own object-storage buckets; validators score them and post weights to the Bittensor chain.

**Membership.**
- Registration on Bittensor gives each participant a UID and hotkey (inference from the use of `metagraph.hotkeys` and UIDs throughout `chain.py`).
- Which miners' updates count each window is chosen by a validator: `post_peer_list` uploads "the list of miners that should participate in the upcoming training windows" to the validator's own bucket (`comms.py` lines 2254 to 2309, docstring). Miners read the list from "the highest-staked validator's bucket" (`get_peer_list` docstring, `comms.py` line 2340 onwards), found as `metagraph.S.argmax()` (`comms.py` line 2239).
- The peer list has primary and reserve peers (`comms.py` lines 2283 to 2289). Validator weights are split 75% to gather peers and 25% to reserve peers of the non-burned weight (`validator.py` lines 1088 to 1090, docstring of `update_weights`).

**Current model, merging and checking.**
- Every miner gathers the listed peers' compressed gradients for the window and applies them in an outer step (`miner.py` lines 747 to 792). Only objects whose storage `LastModified` time falls between the chain block's timestamp and that plus `time_window_delta_seconds` are accepted; others return `TOO_EARLY` or `TOO_LATE` (`miner.py` lines 718 to 730; `comms.py` lines 527 to 544).
- (inference) So the update each miner applies is a deterministic function of public inputs: the leader validator's peer list, the chain's block time, and objects in public buckets. Peers that fail to download some objects will diverge, which is why a sync check exists.
- Checking: validators compare a few parameter values each miner publishes with their own model (`compare_model_with_debug_dict`, `neurons.py` lines 1194 to 1204, "Compare weights with published debug snippets"). Validators also slash for missing gradients, poor sync and index overlap (`validator.py` lines 500 to 508, 1585 to 1681).
- Joining: a new miner loads the latest checkpoint, preferring the highest-staked validator's (`neurons.py` lines 577 to 590, `prefer_highest_staked=True`), then replays every later window by downloading the "pre-computed `aggregated_gradients` object uploaded by the *leader* validator" (`neurons.py` lines 849 to 851) from that validator's bucket (key "aggregator", lines 952 to 960). Only for the last window does it fall back to a live gather from peers (lines 853 to 856 and 982 onwards).

**Who writes shared state.**
- Each participant writes only its own bucket. The client takes **write** credentials for its own puts (`comms.py` line 102, `get_own_bucket("gradients", "write")`) and commits the **read** credentials to the chain (`miner.py` lines 296 to 298; `validator.py` lines 417 to 421). The commitment is the bucket's account ID, access key ID and secret access key, concatenated (`chain.py` lines 140 to 146).
- Validators write the peer list, the start window, aggregated gradients and checkpoints to their own buckets, and weights to the chain (`validator.py` line 2393 `set_weights`, line 3059 `post_peer_list`, lines 2790 and 2799 `ckpt.save_local_async` and `ckpt.upload`). Checkpoint readers choose the highest-staked validator's bucket (`src/tplr/dcp_checkpoint.py` lines 610 to 617, `_choose_read_bucket`).

**Central elements, classified.**
- Bittensor chain (registration, bucket-credential commitments, validator weights, block time used as clock): **(c)**.
- Cloudflare R2 buckets, one per participant, paid by that participant (Gauntlet §5; Covenant-72B §3): **(b)**-like public object storage, but each is a bucket its owner pays for (inference: not a server, but a paid account per participant).
- The highest-staked validator: decides the peer list and publishes the aggregate and checkpoints that joiners use. It is a participant role, but in practice one machine whose availability every joiner depends on (inference from `comms.py` line 2239 and `neurons.py` lines 849 to 860). If we ran that role it would be **(a)** a machine running around the clock.

**What a mistake or a malicious participant could do.**
- A miner: upload late, malformed or poisoned updates; copy another's update. Gauntlet's defences are the put window, format checks, LossScore, the assigned-versus-random-data test, the sync score and norm normalisation (Gauntlet §3 to §4). Gauntlet §4 names residual risks: undetected malicious behaviour, and "a single bad value sent before the peer can be downweighted".
- The leading validator: decides what everyone merges and what joiners replay. (inference) An honest bug in its peer list or aggregate propagates to all miners and every joiner; the code read contains no cross-check of the aggregate against the per-peer objects.
- Published read credentials expose only reading of that participant's bucket (inference from `chain.py` lines 140 to 146 and Gauntlet §5).

**Fit with R1 to R7 (inference).** R1 partly (no server we run, but a validator machine and a public chain); R2 not met (Bittensor is (c)); R3 met in a sense: no relays at all, since all exchange goes through object storage; R4 not met: synchronous windows; R5 and R6 not addressed (full dense replicas); R7: shows "signed per-peer storage" in a concrete form, per-participant buckets whose read keys are published on a ledger.

**How its setting differs from ours.** Permissionless and incentivised; 8×B200 per peer in Covenant-72B; per-participant paid R2 buckets; a chain as clock, registry and referee.

**Question it raises for us.** If each pilot participant writes only to a storage location they own, what public, append-only place lists those locations and the round's peer list without a ledger: a file in the owner's repository, signed by the owner?

### S3. Covenant-72B: Pre-Training a 72B LLM with Trustless Peers Over-the-Internet

- **Authors:** Joel Lidin, Amir Sarfi, Erfan Miahi, Quentin Anthony, Shivam Chauhan, Evangelos Pappas, Benjamin Thérien, Eugene Belilovsky, Samuel Dare (Covenant AI; Mila).
- **Date and venue:** preprint. arXiv 2603.08163; v1 2026-03-09T09:44:13Z, v2 2026-03-10T09:34:33Z (arXiv API, 2026-10-13). **Version read:** v2.
- **Read status:** sections read: Abstract, §1, §2.1, §2.2, §3, §4.1 (first part), §4.4, Appendix A, and the Figure 4 and 5 captions.
- **What it is:** report of a 72B dense pretraining run on Bittensor subnet 3 with permissionless peers.

**Membership, current model, merging, checking.**
- Gauntlet introduces "a validator that scores submitted pseudo-gradients and selects which participants contribute" to each round's aggregation (§2.2).
- All replicas aggregate the selected compressed pseudo-gradients and advance, "leading to the same global model" on all replicas (§2.1, Eq. 2).
- The validator also checks liveness and "synchronization with the main model" (§2.2). Submissions are scaled relative to their median norm "so that no single participant can dominate" (§2.2).
- Exchange: participants upload to their own Cloudflare R2 storage "and provide credentials to the storage bucket"; the validator "asynchronously selects the top-scoring pseudo-gradients, and all participants download them directly from these buckets" (§3). This "avoids requiring direct peer-to-peer connectivity" (§3).
- Coordination runs "on top of the Bittensor blockchain under Subnet 3" (§3).

**Numbers (setting: permissionless, data-centre peers, at least 8×B200 per peer, 72B dense).**
- Contributors capped at 20 per round; mean 16.9 contributing peers (§4.4, Fig. 4 caption). Mean 24.4 active peers per step (Appendix A). At least 70 unique peers contributed over the run (Fig. 5 caption).
- H = 30 inner steps; compression more than 146× (§4.1).

**Central elements:** Bittensor (c); R2 buckets per participant (b-like, paid per participant); validator (a role; (a) if we ran it).

**Fit with R1 to R7 (inference):** as Templar (S2).

**How its setting differs from ours.** Data-centre peers, permissionless, 72B dense.

**Question it raises for us.** Covenant needed a validator to choose contributors because participants were untrusted. For 3 to 5 trusted friends, is a fixed rule enough (for example: count every update that a listed participant posts within the round's window and that passes format and norm checks), making the validator role unnecessary?

### S4. Incentivizing Permissionless Distributed Learning of LLMs (Gauntlet)

- **Authors:** Joel Lidin, Amir Sarfi, Evangelos Pappas, Samuel Dare, Eugene Belilovsky, Jacob Steeves.
- **Date and venue:** preprint. arXiv 2505.21684 v1, 2025-05-27T19:11:22Z (arXiv API). **Version read:** v1.
- **Read status:** sections read in this strand: §2, §3.1, §3.2, §3.3, §4, §5 (§1, §2, §6, §7 were read in `docs/research/2026-10-11-literature-notes/04a-spes-and-citers.md`). Algorithm 1 text was partly garbled in extraction and is not relied on.
- **What it is:** the incentive and validation mechanism used by Templar.

**Membership, current model, merging, checking.**
- Rounds have a "put window": submissions made outside it "are ignored" (§2).
- The validator keeps a score for every participant, "periodically posted on the public blockchain" (§2).
- Primary evaluation: LossScore, the loss change on a data sample after applying one peer's pseudo-gradient (§3.1, Eq. 2); ranked with OpenSkill.
- Proof of computation: each peer gets a unique data subset each round; the validator compares the loss score on that subset with one on random data, to catch copying and duplicate registrations (§3.1, Eq. 3).
- Fast evaluation on more peers: put-window timing, missing submission, wrong format, and a sync score from "2 values per tensor" that each peer publishes; threshold 3 (§3.2).
- Aggregation: in Templar-1B the top G peers by score get weight 1/G, all others zero (§3.3).
- Signed updates allow "fast checkpoint catchup" by "repeated application of the signed updates" (§3.1, "Signed Descent").
- Byzantine tolerance: contributions are normalised "so that each peer contributes equally" (§4). Residual risks: undetected malicious behaviour and "a single bad value sent before the peer can be downweighted" (§4).
- Storage: each peer "creates their own bucket and posts the read-access keys to the blockchain" (§5). The disadvantage: "all communication must pass through the cloud provider" (§5).

**Who writes shared state.** Each peer: its own bucket. The validator: scores on chain (§2, §3.3).

**Central elements:** blockchain (c); per-peer cloud buckets (b-like).

**How its setting differs from ours.** Permissionless and incentivised; the threat is cheating for rewards, which a trusted pilot does not have (inference).

**Question it raises for us.** Which of Gauntlet's checks guard against honest mistakes too (put window, format and shape checks, norm normalisation, sync score) and so would still be worth having among friends?

### S5. INTELLECT-1 Technical Report, and the `prime` framework (now `prime-diloco`)

- **Paper authors:** Sami Jaghouar, Jack Min Ong, Manveer Basra, Fares Obeid, Jannik Straube, Michael Keiblinger, Elie Bakouch, Lucas Atkins, Maziyar Panahi, Charles Goddard, Max Ryabinin, Johannes Hagemann (Prime Intellect, Hugging Face, Arcee AI, Together AI) (PDF title block). Preprint. arXiv 2412.01152 v1, 2024-12-02T05:52:32Z (arXiv API, 2026-10-13). **Version read:** v1.
- **Paper read status:** sections read: §2.4 (2.4.1 to 2.4.5), §2.5, §2.6, §3.1 (first paragraph), §4, §5, and the Figure 2 caption. Also a grep of the whole text for "trust", "verif", "malicious", "permission", "contributor", "orchestrat", "master", "heartbeat", "join".
- **Code:** https://github.com/PrimeIntellect-ai/prime-diloco. Its README line 2: "prime (previously called ZeroBand) is a framework for efficient, globally distributed training". `gh api` (2026-10-13 17:19 TST, org listing): `license.spdx_id` Apache-2.0, `pushed_at` 2026-07-17T22:02:52Z. Shallow clone HEAD `de5b9317da5f57247f11abed2fca259076795460`, commit date 2025-04-10. Files read: `README.md` (grep for coordination terms, lines 2 to 19 and 131 to 148), `src/zeroband/comms.py` lines 86 to 107 and 336 to 360 plus a function index.
- **Correction to `docs/prior-work.md` (2026-10-07):** it listed the INTELLECT-1 framework as `PrimeIntellect-ai/prime` (MIT). On 2026-10-13 the repository named `PrimeIntellect-ai/prime` describes itself as "Official CLI and Python SDK for Prime Intellect" (`description` field, `license.spdx_id` MIT, `created_at` 2024-12-29), while the training framework's description is on `PrimeIntellect-ai/prime-diloco` (Apache-2.0). (inference) The earlier entry probably pointed at the renamed CLI repository.

**Membership.**
- A "master key-value store" holds membership: every node sends a heartbeat "at 2-second intervals"; nodes silent "for 6 seconds are automatically evicted" (§2.4.3). A leaving node sends a "deathrattle" for immediate removal (§2.4.3). The README gives a different default timeout, 10 seconds (`ZERO_BAND_EDM_HEARTBEAT_TIMEOUT_SECONDS`, README line 148); the paper's 6 s is presumably the run setting (inference).
- In code the global `TCPStore` is hosted by the process with global rank 0 (`is_master=self._global_leader`, `comms.py` lines 95 to 100; `_global_leader = global_rank == 0`, line 247). A second store, `god_store`, is opened on the base port with `is_master=False` (lines 101 to 106), so some other process must host it; which one was not traced.
- The leader resolves joiners and dead nodes between outer steps (`_resolve_world`, `comms.py` lines 336 to 360).
- Joining: a new node downloads the checkpoint "from any available active peer" (§2.4.2); the run used the blocking variant, where active nodes pause; transfers took "30-60 minutes" and nodes were added "every few days" (§2.4.2). The README says peers serve the checkpoint from a "sidecar HTTP server" (line 18).
- Networking: all nodes were on a Tailscale VPN (§2.5).

**Current model, merging, checking.** DiLoCo with an all-reduce of pseudo-gradients among the current process group (§2.4.1, §2.4.5); every replica holds the same model (inference from data-parallel design, §2.4.1 item 3). The paper describes no verification of contributions: the grep found no occurrence of "trust", "malicious" or "permission", and "verif" only in a reference title.

**Who writes shared state.** The leader's key-value store holds membership; every node writes its heartbeat. Checkpoints are served by peers (§2.4.2).

**Central elements:** the master key-value store, hosted by a participant process (rank 0) but needed continuously: **(a)** if we ran it (inference). Tailscale: its coordination service is third-party **(c)** (inference; Tailscale's architecture was not read).

**Setting:** 10B dense, up to "eight non-colocated data centers spanning three continents" (§3.1), 30 compute contributors (Figure 2 caption); data-centre nodes; trusted (no verification described).

**Fit with R1 to R7 (inference).** R1 not met as run (a leader store must be up for the whole run); R3 not met as run (Tailscale); R4 synchronous all-reduce; R5, R6 not addressed; R7: trust in all contributors is implicit.

**Question it raises for us.** If a leader's key-value store is the membership authority, can the role move between our intermittently online machines without losing the run (the paper does not address leader failure)?

### S6. INTELLECT-2 and the Prime Intellect protocol

- **Paper:** "INTELLECT-2: A Reasoning Model Trained Through Globally Decentralized Reinforcement Learning", "Prime Intellect Team" (Sami Jaghouar, Justus Mattern, Jack Min Ong and ten others, PDF title block). Preprint. arXiv 2505.07291 v1, 2025-05-12T07:24:33Z (arXiv API). **Version read:** v1. **Read status:** sections read: §2 (overview), §2.1 (first two paragraphs), §2.2 to §2.2.3, §2.3 to §2.3.3 (text; Figure 3 garbled), §2.4.1 to §2.4.3 (Figures 4 and 5 text partly garbled).
- **Code:** https://github.com/PrimeIntellect-ai/protocol. `gh api` (2026-10-13 17:19 TST): `archived` **true**, `license.spdx_id` Apache-2.0, `pushed_at` 2025-11-10T04:53:32Z. Shallow clone HEAD `d389f2035ec2c3c485c6b3e270625f86c7609d50`, commit date 2025-11-09. Files read: `README.md` (all, 89 lines). The separate `PrimeIntellect-ai/smart-contracts` repository is also `archived` true (org listing, `pushed_at` 2025-07-06).
- **What it is:** asynchronous RL post-training with untrusted inference workers and trusted training nodes.

**Membership.**
- The protocol has a "decentralized ledger", a discovery service, an orchestrator, validators and workers (§2.4.1). The README says "Ethereum-based contracts manage the protocol's economic layer" (line 30) and workers need "minimal testnet ETH" (line 79).
- Flow: a worker registers on the ledger and uploads its metadata and IP to the discovery service; a validator checks it and updates the ledger; the orchestrator "reads registrations and verifications from the ledger" and sends a signed invite (§2.4.2 and Figure 4 text). Workers send heartbeats to the orchestrator; a node that misses too many is "removed from the decentralized ledger" (§2.4.2).
- "The orchestrator and discovery service are currently centralized", creating "potential single points of failure" and "trust assumptions" (§2.4.3). All components except the workers and the ledger "are hosted in a Kubernetes cluster" (§2.4.1).

**Current model, merging, checking.**
- Model updates are "computed on trusted centralized nodes", while rollouts are generated "on trustless decentralized nodes" (§2.1).
- New weights reach workers through SHARDCAST relay servers; workers check a SHA-256 of the assembled checkpoint against the trainers' reference checksum (§2.2.3). Peer-to-peer weight transfer was rejected because it would expose worker IPs; they "opted to centralize weight distribution through trusted relay servers" (§2.2.3).
- Rollouts are checked by "a trusted validator node" that recomputes activations by prefill and compares them with the worker's TOPLOC commitments (§2.3.1), plus termination, sampling, fixed-data-sampling and value-bound checks (§2.3.2, §2.3.3). Rejected files get their creator "slashed and evicted" (§2.4.2).
- Workers upload rollouts "using a signed URL" from the orchestrator (§2.4.2, Figure 5 text).

**Who writes shared state.** Trusted trainers write the model; workers write only rollout files through signed URLs the orchestrator issues; validators flag files accepted; the ledger records registrations, pool membership and contributions (§2.4.1, §2.4.2).

**Central elements:** orchestrator, discovery service, relay servers, validators: **(a)** (Prime Intellect's Kubernetes cluster). Ledger: Ethereum-based **(c)**. Storage via signed URLs: (b)-like object storage controlled by the orchestrator.

**Fit with R1 to R7 (inference).** Not a fit for pretraining: model updates stay on trusted central nodes. Relevant to R7 only as an example of **signed-URL writes**: participants never hold a standing write credential; a coordinator hands out a per-upload URL. That pattern needs a live issuer, i.e. a server (a).

**Question it raises for us.** The signed-URL pattern limits what a participant can write but needs an always-on issuer; is there a static-host equivalent (per-participant fine-grained tokens scoped to one path) that keeps the limit without the issuer?

### S7. Prime Collective Communications Library (PCCL), technical report

- **Authors:** Michael Keiblinger, Mario Sieg, Jack Min Ong, Sami Jaghouar, Johannes Hagemann (Prime Intellect) (PDF title block). Preprint. arXiv 2505.14065 v1, 2025-05-20T08:11:42Z (arXiv API). **Version read:** v1.
- **Code:** https://github.com/PrimeIntellect-ai/pccl; `gh api` org listing (2026-10-13 17:19 TST): `license.spdx_id` MIT, `pushed_at` 2025-09-12T08:53:07Z. Code not read.
- **Read status:** sections read: §2.1 to §2.5.3, §3.3.1 (first part), §8, §9.

**Membership.** "A lightweight master process that orchestrates membership and consensus" (§2.2). New peers stay "registered" until "existing accepted peers vote to integrate it" (§2.5.1). Every state transition "requires unanimous agreement among involved peers ('micro-consensus')" (§2.3.1). The authors justify "the rather 'authoritarian' master node" as what made fault tolerance tractable (§2.5.3).

**Current model and checking.** PCCL keeps "bit-identical state across all accepted peers": each peer submits a hash of its tensors and "the master identifies any outlier peers", which then fetch data from an up-to-date peer (§2.4). The hash is deterministic across GPU generations "from the GTX 980 Ti to the B200" (§2.4). After a full stop, "resumption will only be allowed from the previous shared state hash" (§8).

**Who writes shared state.** The master holds membership and the topology; peers hold the shared state and compare hashes.

**Central elements:** the master process: **(a)** if we ran it continuously. The paper does not say what happens if the master fails (grep for "single point", "master ... fail/crash/down" found nothing).

**Fit (inference).** Shows that a cheap hash comparison lets peers confirm they hold bit-identical models, which is the check a "merge rule every peer computes" needs. The master remains a live coordinator.

**Question it raises for us.** If every peer publishes the hash of the model it computed for round t, does a mismatch between friends' hashes give us the "any peer can check" property without a master?

### S8. Gensyn OPEN-1B: `open-transformers` and `gensyn-audit` (bitwise replay of training steps)

- **Maintainers:** Gensyn. Software.
- **Repositories and API data** (`gh api repos/...`, 2026-10-13 17:34 TST):
  - https://github.com/gensyn-ai/open-transformers: `license.spdx_id` Apache-2.0, `created_at` 2026-09-15T14:22:34Z, `pushed_at` 2026-09-16T13:04:58Z. Shallow clone HEAD `d7b7b674cd851f7a16815229f060658180cb772b` (2026-09-15).
  - https://github.com/gensyn-ai/gensyn-audit: `license.spdx_id` Apache-2.0, `created_at` 2026-09-15T14:52:44Z, `pushed_at` 2026-09-16T18:23:25Z. HEAD `b9b1a0bb0b0593683973702d74d62e7487a94c94` (2026-09-16).
  - https://github.com/gensyn-ai/ree ("Reproducible Execution Environment"): `license.spdx_id` null, `pushed_at` 2026-10-05T12:52:46Z. Not read.
- **Read status (files read):** `open-transformers/README.md` lines 1 to 146 and 265 to 298; `gensyn-audit/README.md` (all, 47 lines).
- **What it is:** OPEN-1B is a 1.61B dense model trained by Gensyn on "48 × H100" (README line 144), whose every optimizer step has a published hash that anyone can re-execute. The training itself was centralised; the novelty for us is the checking.

**How the model is defined and checked.**
- Every step "has a recorded state hash", and anyone can re-execute a step "and get back the exact same bytes" (README lines 6 to 9).
- Five things are pinned: kernels (fixed-order reductions in `repop`), initialisation (counter-based Philox on CPU), data ("a pure function of (seed, shard manifests, `seq_len`)"), gradient reduction that "does not depend on how many GPUs ran it", and deterministic clipping (README table, lines 46 to 52).
- A chained state hash: "a blake2b digest over weights, optimizer moments and param groups", the step's gradients and a batch digest, "each step's hash folding in the previous one" (lines 54 to 56).
- An audit kit is "world-readable": the harness wheel, `repop` wheels, a `trajectory.json` of hashes and a `kit.json` manifest "binding them by SHA-256" (lines 65 to 70). The replay prints "`MATCH` or `MISMATCH`" (line 82).
- Limits stated: a match shows the pinned replay reproduced the hash; it "does not establish how an earlier training run was executed", and the hash does not cover RNG, the data-stream cursor and some metadata (lines 103 to 112).
- `gensyn-audit` "independently replays Gensyn Open 1B training steps" and verifies them against "the run's published commitments" (`gensyn-audit/README.md` lines 3 to 4); the current audit needs "an Apple Silicon Mac" (line 8); audits are claimed through Gensyn's website (lines 17 to 23).
- Trust warning relevant to shared state: "**Checkpoint directories are code, not data.**" because `torch.distributed.checkpoint` unpickles metadata (lines 114 to 117).
- Licence discrepancy: `gensyn-audit` README says RepOp is under the "Gensyn Reproducibility License v1.0", allowing use "to audit Open-1B's training" (lines 43 to 47); `open-transformers` README says the published `repop` wheels "declare MIT" and "the `repop` source tree is not public" (lines 267 to 270). Not resolved.

**Central elements:** training by Gensyn (not decentralised); hashes, kits and checkpoints on Google Cloud Storage (README line 73, `storage.googleapis.com/gensyn-audit-public`) and Hugging Face (line 3): **(b)**. Audit claims through `open1b.gensyn.ai`: (a) for Gensyn.

**Fit (inference).** Not a coordination system. It is the strongest primary evidence found that "a model defined by a rule every peer computes identically" can be made **checkable bit for bit** across different hardware, at a cost: custom kernels for every byte-sensitive op. For CASSANDRA Chorus (inference) this suggests two levels of "identical": (1) bitwise, which needs RepOps-style kernels; (2) agreement within a tolerance, which plain PyTorch on mixed GPUs can give.

**Question it raises for us.** Must every friend's merge produce bit-identical weights (so a published hash can be compared), or is a tolerance check enough for a trusted pilot?

### S9. Gensyn RL Swarm, its `SwarmCoordinator` contract, and SAPO

- **RL Swarm:** https://github.com/gensyn-ai/rl-swarm; `gh api` (2026-10-13 17:19 TST): `license.spdx_id` MIT, `pushed_at` 2026-01-05T21:15:30Z. Shallow clone HEAD `9c95410b1ac0d0a6005513c276b6b84f6db13bcd` (2026-01-05). **Files read:** `README.md`, grep hits only (for chain, contract, testnet, peer, identity, login) at lines 5, 8, 15, 158 to 194, 225 to 252, 261, 304; not read in full.
- **Contract:** https://github.com/gensyn-ai/rl-swarm-contracts; `license.spdx_id` null (the source file header says `SPDX-License-Identifier: MIT`); `pushed_at` 2025-09-29T21:35:10Z. HEAD `695736ef22961130daab9e3ca83758cae528af74`. **Files read:** `src/SwarmCoordinator.sol` lines 1 to 28, 273 to 320, 431 to 460, 512 to 545, plus a grep index of functions, mappings and roles.
- **SAPO paper:** "Sharing is Caring: Efficient LM Post-Training with Collective RL Experience Sharing", Gensyn AI Team (Jeffrey Amico and 14 others, alphabetical). Preprint, arXiv 2509.08721 v1, 2025-09-10. **Read status:** abstract only, plus a keyword grep (no hits for "blockchain", "on-chain", "smart contract", "hivemind" or "DHT").

**Membership and state.**
- RL Swarm is "open source and permissionless"; joining the Gensyn Testnet gives "an on-chain identity" (README line 5). Identity: an Alchemy-hosted wallet created by email sign-in, linked on chain to a local `swarm.pem` peer key (README lines 231 to 233).
- The contract stores: peer ID to wallet mappings (`registerPeer`, open to anyone, lines 304 to 316); the current round and stage, advanced only by an account with `STAGE_MANAGER_ROLE` (`updateStageAndRound`, line 273); a list of bootnodes managed by `BOOTNODE_MANAGER_ROLE` (lines 355 to 391); per-round votes for "winners" and self-submitted rewards, each checked only for the sender owning the peer ID (lines 437 to 438, 541 to 542). The owner role is granted all three roles at initialisation and the contract is upgradeable (lines 170 to 177).
- SAPO: "each node manages its own policy model(s) while 'sharing' rollouts" (abstract). (inference) There is no shared current model to agree on; only rollouts are exchanged.

**Central elements:** Gensyn Testnet chain **(c)**; the stage-manager account that advances rounds: **(a)** a process someone runs; Alchemy-hosted wallets (third-party service).

**Fit (inference).** Not a model-merging system. It shows a ledger used as a registry, a round clock pushed by one privileged account, and a bootnode list, all of which a trusted pilot could hold in an owner-published file instead.

### S10. Verde: Verification via Refereed Delegation for Machine Learning Programs

- **Authors:** Arasu Arun, Adam St. Arnaud, Alexey Titov, Brian Wilcox, Viktor Kolobarić, Marc Brinkmann, Oguzhan Ersoy, Ben Fielding, Joseph Bonneau (Gensyn AI; NYU; a16z crypto research). Preprint. arXiv 2502.19405 v1, 2025-02-26. **Version read:** v1.
- **Read status:** sections read: Abstract, §1 (two-column text, partly interleaved), start of §2. Not read: protocol details, RepOps evaluation.
- **What it is:** a dispute protocol: a client gives the same ML job to k > 1 providers; if outputs differ, a referee narrows the dispute to one step and then one operator and re-executes only that (§1).
- **Who decides:** "a neutral referee (which could be the client themselves)" (§2); the approach could serve in decentralized training "with an on-chain smart contract serving as a referee" (§1).
- **Guarantee:** if at least one provider is honest, its output is accepted; "if all trainers are dishonest" the guarantee fails (§2). Refereed delegation costs "at least a factor 2" because the job runs at least twice (§1).
- **Precondition:** bitwise reproducibility across hardware, provided by RepOps (Abstract; §1 "Challenge 2").

**Fit (inference).** Relevant to "any peer can check": with bitwise-reproducible merges, any friend could act as referee for a disputed round by re-executing a single step. Without reproducibility, disputes cannot be settled this way.

### S11. Agora: Collective and Permissionless Internet-Scale Pretraining (Pluralis), with the `agora` and `node0` code

- **Paper authors:** Gil Avraham, Violetta Shevchenko, Hadi Mohaghegh Dolatabadi, Karol Pajak, James Snewin, Harry Xi, Rodney O'Donnell, Thalaiyasingam Ajanthan, Sameera Ramasinghe, Chamin Hewa Koneputugodage, Shamane Siriwardhana, Alexander Long (Pluralis Research). Preprint. arXiv 2607.13332 v1, 2026-07-14T23:32:18Z (arXiv API). **Version read:** v1.
- **Paper read status:** sections read: Abstract, §3 intro, §3.1 (with Figure 1 caption), §3.2, §3.3 intro, §3.3.1 (state loading and weight averaging paragraphs, lines 455 to 705 of the text), §3.6.1 (Authorizer, all), §3.6.2 (Health Monitor, first part), §5.1 (lines 1836 to 1845). Plus a grep for checkpoint, object storage, reducer, Pluralis node.
- **Code:** https://github.com/PluralisResearch/agora: `license.spdx_id` Apache-2.0, `created_at` 2026-05-12, `pushed_at` 2026-07-04T08:42:17Z (`gh api`, 2026-10-13 17:34 TST). HEAD `37d29a966528675635161007d7b43388012a98b2`. **Files read:** `README.md` grep (lines 85, 186, 216, 245 to 255, 317 to 339, 445). https://github.com/PluralisResearch/node0: Apache-2.0, `pushed_at` 2025-09-23T04:44:01Z; HEAD `32bd084de15dbdc8e30723ad66db7d01acf70c03`; **files read:** `README.md` grep (lines 27 to 29, 72, 78 to 80, 159 to 167, 183 to 219).
- **Prior-work check:** the abstract confirms the snippet-level numbers in `docs/prior-work.md` §5 that touch membership: 8.6B parameters, 500B FineWeb-Edu tokens, 40 days, 330 contributor nodes, "predominantly consumer GPUs". The "5% of weights every 20 steps" figure appears in the Figure 1 text ("5% of weights · async · every 20 steps"); averaging details are for strand 4.

**Membership.**
- "The Authorizer ... is a singleton component and the gatekeeper that admits workers and trainers" (§3.1). It is "a single admission and trust authority" (§3.6.1), an HTTP service with PostgreSQL and Redis (§3.6.1, Architecture).
- Checks at entry: capability (RAM, VRAM, bandwidth, latency), integrity ("a legitimate, unmodified build of the client"), reachability, and accountability (authentication) (§3.6.1, Node admission). Admission is rate-limited through a queue, and the Authorizer assigns each node's pipeline stage (§3.6.1).
- After admission, peers authenticate each other locally: the Authorizer signs a credential binding identity, public key and expiry; each peer checks that signature and a handshake signature (§3.6.1, Peer authentication). Credentials "are short-lived and must be renewed periodically", which is the revocation mechanism (§3.6.1).
- Per-round averaging groups form by DHT matchmaking: peers announce themselves "up to a bounded matchmaking window"; the group is then fixed, with members "ordered deterministically so that every peer derives the same layout" (§3.3.1, All-reduce algorithm).
- "While this run was not decentralized and required specific Pluralis nodes", the goal is a protocol with "no central orchestration" (§3.3).

**Current model, merging, checking.**
- No single current model: each stage is replicated across workers, which average "5%" of weights periodically (Figure 1 text) by all-reduce within the stage (§3.3.1). Only Pluralis nodes act as reducers, "while contributors act only as senders" (§3.3.1). A sender that times out "is banned and excluded from the round" (§3.3.1).
- Checking is at admission (code integrity) rather than per update, in the sections read (inference: §3.6.1 lists no per-update scoring).

**Who writes shared state.** Run metadata lives in a DHT, "one instance per stage, plus one shared by the trainers" (§3.3). Checkpoints in cloud object storage are "saved periodically by Pluralis nodes" (§3.3.1, Figure 2 caption); contributors load from them (§3.3.1). Pluralis nodes alone held the head and tail stages after the public opening (§5.1).
- Node0 and Agora clients authenticate with a Hugging Face token that "doesn't need any read/write permissions as it will only be used for authorization" (`node0/README.md` line 80; `agora/README.md` line 85).

**Central elements:** Authorizer, Health Monitor, Metrics Monitor, Dashboard: **(a)** ("managed services · Pluralis-hosted", Figure 1 text). Reducer and head/tail nodes run by Pluralis: (a). Checkpoints on cloud object storage (S3; §5.2 table "Cloud object storage (S3)"): (b)-like, written only by the operator. Per-stage DHTs over participants: peer-to-peer (bootstrap peers via `--initial_peers`, agora README line 186).

**Fit with R1 to R7 (inference).** R1 not met (several operator services). R3: contributors must expose a public port (Node0 README line 72), no relays described in the parts read. R4: asynchronous within-stage averaging. R5, R6: pipeline stages, not experts; no full copies. R7: shows the "signed credential from one root key" pattern for membership, plus operator-only writes to checkpoints.

**Question it raises for us.** Agora's Authorizer signs short-lived peer credentials so peers can reject outsiders without contacting it. Could the owner's code-signing key (allowed central by R2) sign the pilot's membership list, so every peer can verify membership offline, with no live Authorizer?

### S12. Hivemind DHT signed records (`RSASignatureValidator`)

- **Code:** https://github.com/learning-at-home/hivemind at commit `4bd43b77895019b20d18d81d0d0c1a5ab9a10847` (committer date 2026-01-04T23:36:23Z; `gh api repos/learning-at-home/hivemind/commits/master`, 2026-10-13 17:36 TST). `gh api repos/learning-at-home/hivemind` (2026-10-13 17:44:55 TST): `license.spdx_id` MIT, `pushed_at` 2026-01-11T21:13:45Z, `archived` false.
- **Files read:** `hivemind/dht/crypto.py` (all, 91 lines), `hivemind/dht/validation.py` lines 7 to 15 (fetched raw).
- **What it shows:** "protected records" whose key or subkey contains the owner's RSA public key; changes to them "must be signed with the corresponding private key (so only the owner can change them)" (`crypto.py` docstring, lines 13 to 18). A record with no owner key "is not protected" and is accepted (lines 46 to 47). Every record carries an `expiration_time` (`validation.py` line 11).
- **Fit (inference):** the "peer-to-peer only" option with per-peer signed records exists in a maintained library: a peer can publish "my update for round t is at hash h" under its own key, and others can verify it. Records expire, so durable state still needs a host (b). Agora is built on Hivemind (agora README line 445).

### S13. Hugging Face Hub documentation: tokens, organisation roles, signed commits

- **Source:** https://github.com/huggingface/hub-docs at commit `ef42b8f94576e58f9c32d5eed2f250a180dcc477` (2026-10-13T14:01:18Z), raw files under `docs/hub/`. Fetched 2026-10-13 17:36 to 17:37 TST.
- **Files read:** `security-tokens.md` (all, 134 lines), `organizations-security.md` (all, 47 lines), `security-gpg.md` lines 1 to 30, `storage-buckets-security.md` (all, 42 lines), `security-pickle.md` line 5 and grep, `repositories-settings.md` grep.
- **What it shows:**
  - Token roles: `fine-grained` "access to specific resources, such as a specific model or models in a specific organization"; `read`; `write` (`security-tokens.md` lines 14 to 18). A leaked token lets "anyone ... read or write your private repos in the meantime" (line 59). Token approval and revocation policies for organisations are Team and Enterprise features (lines 105 to 134).
  - Organisation roles: `no_access`, `read`, `contributor`, `write`, `admin` (`organizations-security.md` line 11). `contributor` gives "write rights to the subset of the Organization's repos that were created by the user" (line 17). `write` lets users "create, delete, or rename any repo in the Organization namespace" (line 19). Resource Groups for finer control are Team and Enterprise features (lines 7 to 9).
  - Push authentication is not authorship: git "does not authenticate the actual commit authors" (`security-gpg.md` line 3); GPG-signed commits can be marked verified (lines 23 to 25).
  - Pickled weights allow "arbitrary code execution attacks" (`security-pickle.md` line 5).
- **Fit (inference):** the free `contributor` role gives each pilot participant their own repositories inside an owner-administered organisation, which they alone (with admins) can modify. That is "per-participant storage on a public host" without a ledger. What it does not give: protection of a shared repository against a `write`-role member, or any check on content.

### S14. GitHub documentation: fine-grained personal access tokens and rulesets

- **Source:** https://github.com/github/docs at commit `d1a0081f2407dbe4a08ba40b9cf3ae5e83659a9f` (2026-10-13T14:05:19Z). Fetched 2026-10-13 17:37 TST.
- **Files read:** `content/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens.md` lines 44 to 56 and 104 to 160 (plus grep); `content/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets.md` lines 17 to 35, 79 to 90, 198 to 204 (plus grep); `about-rulesets.md` lines 17 to 41 (grep).
- **What it shows:**
  - Fine-grained tokens: limited to one resource owner and optionally "to only access specific repositories" (PAT doc line 51); expiry from 1 to 366 days or none (line 158); organisations can require approval (line 54). (Permission granularity is per repository, not per path, in the parts read.)
  - Rulesets can restrict who may create, update or delete matching branches or tags, require signed commits, and block force pushes (rules doc lines 27 to 35, 79, 198 to 202). Push rulesets that block pushes apply to "a private or internal repository" (line 17). Organisation-wide rulesets are for Team and Enterprise plans (`about-rulesets.md` line 17).
- **Fit (inference):** with GitHub alone, a participant with write access to a shared repository can change any file on any branch not protected by a rule; per-path limits were not found in the parts read. Per-participant repositories, or per-participant branches and tags protected by rulesets, are the available ways to bound what one friend can overwrite.

### S15. `huggingface_hub` client: conditional commits and history squashing

- **Source:** https://github.com/huggingface/huggingface_hub, `src/huggingface_hub/hf_api.py` at commit `a704b8488c6ec78f719c576ba77a6035095dae77` (latest `main` on 2026-10-13 17:42 TST). `gh api`: `license.spdx_id` Apache-2.0, `pushed_at` 2026-10-13T13:54:35Z. Software.
- **Files read:** `hf_api.py` lines 4284 to 4300 (`super_squash_history` docstring) and 5033 to 5039 (`create_commit` docstring for `parent_commit`), plus a grep for `parent_commit`.
- **What it shows:**
  - `create_commit(..., parent_commit=...)`: "the commit will fail if `revision` does not point to `parent_commit`", which "ensures the repo has not changed before committing" and helps when the repo "is updated / committed to concurrently" (lines 5035 to 5039). This is a compare-and-swap on a branch head.
  - `super_squash_history`: "Once squashed, the commit history cannot be retrieved. This is a non-revertible operation." (warning in the docstring after line 4284).
- **Fit (inference):** a branch of a Hub repository can serve as a single ordered log that several writers append to without overwriting each other, provided every writer uses `parent_commit`. A client that omits it, or any writer who squashes history, defeats the ordering. Whether the server, rather than the client, enforces anything beyond the optional check was not read.

## Findings for questions 3 and 7

Everything below cites the source blocks above (S1 to S15) by number; locators are in those blocks. "(inference)" marks my reasoning. No design is recommended here.

### Q3a. Who decides membership and the current model, system by system

The cells summarise the source blocks; the (a)/(b)/(c) classifications and entries such as "Not described" or "None described" are my judgements from the parts read (inference).

| System (block) | Who admits a participant | Who fixes a round's or group's members | What defines the current model | What is checked, by whom | Central elements, classified |
|---|---|---|---|---|---|
| Psyche, Solana mode (S1) | `join_authority` key issues on-chain authorizations (or a permissionless authorizer) | The coordinator program's `tick` (anyone may call) admits pending clients at epoch start; health checks drop peers | Each client applies, per batch, the commitment that reaches the witness quorum in on-chain witness bloom filters, starting from a common checkpoint | Payload hash against its signed commitment, by every client; witness attestation of receipt. Recompute verification is `todo!()` at the commit read | Solana (c); Hugging Face or GCS checkpoint (b); iroh relays: n0 public (c) or Psyche-run (a) or disabled; n0 DNS/pkarr lookup (c) |
| Psyche, TCP mode (S1) | Server's config | The server's coordinator `tick` | As above | As above | Coordinator server (a), described as a dev tool |
| Templar / Covenant-72B (S2, S3, S4) | Bittensor registration (UID, hotkey) | The highest-staked validator posts the peer list to its bucket | Every miner applies the listed peers' compressed pseudo-gradients found in public buckets within a chain-timed put window; joiners replay the leader validator's published aggregates | Validators: LossScore, assigned-vs-random data test, put window, format, sync score from 2 values per tensor, norm normalisation | Bittensor (c); per-participant R2 buckets (b-like, paid); leader validator (a role; (a) if we ran it) |
| INTELLECT-1 / `prime` (S5) | Not described (trusted contributors) | Leader process (global rank 0) hosts the key-value store; heartbeats and deathrattles | All-reduce of pseudo-gradients over the live process group | None described | Leader store (a); Tailscale VPN (c) |
| INTELLECT-2 / protocol (S6) | Ledger registration + validator check + orchestrator's signed invite | Orchestrator, by heartbeats | Trusted central trainers | Trusted validator nodes re-run prefill against TOPLOC commitments; sanity checks | Orchestrator, discovery, relays, validators (a); Ethereum-based ledger (c) |
| PCCL (S7) | Accepted peers vote newcomers in | Master process, by micro-consensus | Bit-identical shared state | Peers submit state hashes; master finds outliers, who re-fetch | Master (a) |
| Agora / Pluralis-8B (S11) | Singleton Authorizer: hardware, code-integrity and reachability checks; signed short-lived credentials | Per-round DHT matchmaking window; members ordered deterministically | No single model: stage replicas averaged periodically | Admission checks; peers verify credentials locally | Authorizer and monitors (a); operator reducer nodes (a); operator-written checkpoints on S3 (b-like) |
| RL Swarm (S9) | Anyone registers a peer ID on chain | Round clock advanced by a stage-manager account | No shared model (each node keeps its own) | None on the model | Gensyn Testnet (c); stage manager (a) |
| OPEN-1B (S8) | Not applicable (central training) | Not applicable | A published chained state hash per step | Anyone replays a step and compares hashes (bitwise) | Kits and hashes on GCS and Hugging Face (b) |

### Q3b. Systems whose model is a rule every peer computes from public inputs

- **Psyche (S1)** is the clearest case found of a "merge rule every peer computes identically". There is no stored model on the coordinator; every client starts from the same checkpoint and applies the same witness-selected results. The public inputs are the on-chain witness records, the on-chain seed and the peer-to-peer payloads, each checked against its signed hash.
  - A client that lacks the payload for a consensus commitment does not apply a smaller set: the apply step returns an error (`DidNotFinishDeserializingCommitment`, `DidNotBeginDownloadingCommitment` or `UnknownCommitment`, `train.rs` lines 616, 623 and 630). Only batches with no consensus at all are skipped, by every client alike (line 604). (inference) So a Psyche client either applies exactly the agreed set or fails the step.
- **Templar (S2, S3)** has the same structure with different inputs: the leader validator's peer list, the chain's block time, and objects in public buckets. Covenant-72B says all replicas end with "the same global model" (§2.1, Eq. 2).
- **Agora (S11)** derives only the averaging group's layout deterministically ("every peer derives the same layout"); replicas are not identical between averaging rounds.
- **PCCL (S7)** and **OPEN-1B (S8)** are not coordination-free, but they supply the checking half: PCCL compares per-peer state hashes for bit-identity; OPEN-1B publishes a chained hash per step that anyone can reproduce on other hardware.
- (inference) "Computes identically" and "can be checked" are separate properties:
  - Psyche and Templar specify the first: every peer applies the same inputs. Bit-identity across different GPUs is not claimed in the parts read. Templar's validator sync score tolerates divergence below a threshold of 3 (Gauntlet §3.2), which suggests results are close, not bitwise equal.
  - The second property needs either a published hash that others can reproduce bit for bit (OPEN-1B with RepOps kernels; PCCL's deterministic hash; Verde's precondition) or a tolerance comparison (Templar's sync score).
  - Psyche, as read, has the first property without a per-peer published model hash: witnesses attest receipt, and verification is unimplemented.
- (inference) For a merge rule to be checkable by any peer, the inputs must be public and fixed before the merge: who was in the round, which updates count, and the update files themselves. Psyche fixes them on a ledger; Templar fixes them in the leader's bucket plus the chain clock. Nothing found fixes them without either a ledger or a single writer.

### Q3c. What the ledger-based systems put on the ledger

| System | On the ledger (from the code or paper read) | Source |
|---|---|---|
| Psyche | Run config and model description (owner-only `update`); join authorizations; client roster and states; epoch, round and step; the random seed (from block time and slot); witness proofs with participant and broadcast bloom filters and a Merkle root; health-check results; the checkpoint pointer (Hub or GCS repo); reward points | S1 |
| Templar / Covenant | UID and hotkey registrations; each participant's bucket account ID and read keys (as a commitment); validator weights (scores); block numbers and timestamps used as the round clock | S2, S3, S4 |
| Prime protocol (INTELLECT-2) | Compute pools and their ownership; worker registrations and validator verifications; invites; contributions; submit events that trigger validation; slashing | S6 |
| RL Swarm | Peer ID to wallet mapping; current round and stage; bootnode list; per-round "winner" votes and self-reported rewards | S9 |

### Q3d. Is a ledger needed for a trusted pilot of 3 to 5 friends? Function by function (all inference)

For each ledger function above, the question is whether something R2 already allows could carry it: an owner-published configuration, a public static-file host (b), the code-signing key, or the bootstrap peers. None of the sources tested a pilot like ours; this is reasoning from what each ledger function does.

| Ledger function | What it guards against in its system | Candidate non-ledger carrier for a trusted pilot | What is lost |
|---|---|---|---|
| Membership roster and authorizations (Psyche, Prime, RL Swarm, Bittensor) | Sybil identities, unknown joiners | An owner-signed participant list (public keys) in the published configuration; Agora shows peers can verify signed credentials locally (S11) | Live admission without the owner; revocation requires publishing a new signed list |
| Round clock and seed (Psyche seed from block; Templar block time; RL Swarm stage manager) | Participants choosing favourable seeds or windows | Seed derived from the run seed and round number (already how Chorus assigns slices, per the brief) | A trusted wall clock: rounds must be defined by content (all inputs present) or by participants' own clocks |
| Which updates count (Psyche witness blooms; Templar peer list + put window) | Withholding, late or copied updates | A deterministic rule over files present on the host when the round closes, plus each peer's signed statement of what it saw. A git-based host branch used with conditional commits (`parent_commit`, S15) gives one ordered record that several writers append to | Agreement when peers see different file sets if there is no single ordered record. With conditional commits the record is ordered, but a writer can bypass it by omitting the check or squash it irreversibly (S15); a public chain makes its record unchangeable, the host does not |
| Bucket or storage registry (Templar read keys) | Finding participants' storage | Locations listed in the owner-signed configuration | Nothing material for 3 to 5 people (inference) |
| Checkpoint pointer (Psyche) | Newcomers finding the current model | A naming convention on the host (round number in the path) plus the published hash | Psyche shows the risk of a pointer any member can overwrite (S1) |
| Scores, rewards, slashing (all four) | Incentive gaming | No incentive function to replace in a trusted pilot | Nothing for the pilot; becomes relevant at Phase 6 |

- (inference) The function hardest to replace is the agreed, ordered record of **which updates count in a round**. In Psyche the chain's witness records fix it. In Templar one leader writes it. Without either, a static host must make "present by the deadline" well defined. Peers must also not see different sets because uploads are slow or listings stale. A git-based host offers a partial substitute: conditional commits order appends to one branch (S15). Its record is protected only by the participants' honesty and the host's access rules, not by consensus. The trade-off is consensus-backed immutability (chain, (c)) against trust in participants plus host access rules (host, (b)).
- (inference) For 3 to 5 trusted, intermittently online machines, Psyche's evidence also shows the costs of the ledger route. Every state transition is a transaction (tick, witness, health check, checkpoint); a public chain is (c) and is outside R2. So the brief's (c) flag applies to any ledger design.

### Q7. Write access to shared state: the four R7 options compared

Evidence is from S1 to S15; the right-hand judgements are inference unless a source is cited.

| Option | Exemplars read | What a participant must be trusted with | Honest mistake | Malicious participant | What stays central, classified |
|---|---|---|---|---|---|
| **1. Per-participant tokens to one shared repository** (for example an HF organisation repo or a GitHub repo) | Psyche checkpointers upload with their own HF token (S1); HF org `write` role (S13); GitHub fine-grained tokens (S14) | Not to overwrite or delete others' files: an HF `write` member can "create, delete, or rename any repo" in the organisation (S13); a GitHub token is limited to chosen repositories, not paths (S14, parts read) | Overwrites or deletes another's update or the checkpoint; pushes a corrupt file; a leaked token lets anyone write meanwhile (S13 line 59) | Replaces the checkpoint or others' updates; erases history (Hub `super_squash_history` is "non-revertible", S15; GitHub force pushes unless a ruleset blocks them, S14); uploads pickled weights that execute code on load (S13 `security-pickle.md`; S8 "checkpoint directories are code") | The host (b); the owner as organisation admin who issues and revokes access. GitHub rulesets (signed commits, no force push, branch restrictions) narrow the damage (S14) |
| **2. Signed per-peer storage** (each participant writes only its own location; others read and verify) | Templar per-participant R2 buckets with read keys on chain (S2, S4); HF `contributor` role: write only to repos the user created (S13); Hivemind owner-signed DHT records (S12) | Only its own outputs; the merge reads but cannot be overwritten by others | Bad or late upload affects only that participant's contribution; a merge rule can skip it (Templar's put window and format checks, S4) | Can still publish a poisoned but well-formed update, which every peer merges unless checked (Gauntlet §4 residual risks); cannot touch others' files | A public registry of the locations: on chain for Templar (c); in an owner-signed configuration for a pilot (inference). The host (b) |
| **3. Peer-to-peer only** (no shared host; state held and exchanged by peers) | Psyche's P2P checkpoint and result exchange (S1); PCCL shared-state sync (S7); Hivemind DHT with expiring signed records (S12); INTELLECT-1 peer checkpoint transfer (S5) | Correct serving of the state it holds | If all holders are offline, state is unavailable: Psyche falls back to a Hub checkpoint when no previous-epoch client is present (S1); DHT records expire (S12) | Serves wrong data; Psyche guards results with signed hashes (S1); PCCL detects outliers by hash (S7) | A coordinator or master in every exemplar read: Psyche coordinator (c) or (a), PCCL master (a), INTELLECT-1 leader store (a). No exemplar ran with no central element at all |
| **4. A ledger** | Psyche on Solana (S1); Bittensor for Templar (S2 to S4); Prime protocol on an Ethereum-based ledger (S6); Gensyn Testnet (S9) | Correct transactions; the run creator's key can change config (Psyche `update`, S1) | Wrong transaction is permanent but visible; Psyche lets any epoch member repoint the checkpoint (S1) | Bounded by program rules: Psyche checks membership and witness committee proofs (S1); but the chain cannot see off-chain content, so poisoned updates still need off-chain checks (S4) | The chain (c), outside R2 and flagged by the brief; plus off-chain storage (b) for model data in every exemplar |

Additional observations (inference unless cited):
- Every exemplar keeps the model bytes off the ledger. Covenant states that object storage "facilitates validation ... without needing to directly write to the blockchain" (S3, §3). So option 4 always comes with option 1, 2 or 3 for the data.
- Options 1 and 2 differ mainly in blast radius. The HF `contributor` role (S13) and per-participant buckets (S2) confine each friend's writes to their own space. A shared repository with `write` access does not.
- Content checks are independent of the write option in all exemplars: hash against a signed commitment (S1), LossScore and sync score (S4), TOPLOC (S6), bitwise replay (S8). Write-access control decides who can write where, not whether what they wrote is good.
- Pickled checkpoints turn write access into code execution on every reader (S8, S13). That makes the file format part of the write-access question for any option.

## Could not verify

- **Psyche `update` while a run is active.** Whether the Solana `update` instruction refuses changes to config, model or progress during an active run was not read (`instance_state.rs` update path not opened). S1's statement that `main_authority` can change them "at any time" is inference.
- **Psyche verification after 2026-03-20.** The clone is the latest `main` commit (2026-03-20; `pushed_at` 2026-03-24). Whether verification was implemented elsewhere (another branch or repository) was not checked. A WebSearch (log below) found nothing.
- **Psyche peer-to-peer checkpoint integrity.** Whether a joiner checks the layer-by-layer model it assembles from peers against a hash was not read.
- **Psyche relay hostnames.** `USE_RELAY_HOSTNAME` and `USW_RELAY_HOSTNAME` values and their operator were not read.
- **Which process hosts `god_store` in `prime-diloco`** (S5): not traced.
- **Tailscale's coordination and relay architecture** (S5): Tailscale's own documentation was not read, so the (c) classification is inference.
- **Bittensor validator consensus.** Gauntlet cites Yuma consensus only by a footnote link; how several validators' weights combine, and whether miners ever follow a validator other than the highest-staked, was not read.
- **Bitwise identity of Templar miners' models.** Not claimed in the parts read; the sync-score threshold suggests small divergence is expected (inference).
- **RepOp licence.** `gensyn-audit` and `open-transformers` READMEs describe it differently (S8). Unresolved.
- **Hugging Face fine-grained token granularity for writes.** The doc says fine-grained tokens can target "specific resources" (S13); whether write permission can be limited to one repository was not confirmed in the lines read (the token-settings UI was not read).
- **GitHub per-path write limits.** Not found in the parts of the GitHub docs read; this is absence in the parts read, not a confirmed absence.
- **TOPLOC paper (arXiv 2501.16007 v2):** downloaded but not read; its description here comes only from INTELLECT-2 §2.3.
- **Agora inter-replica divergence (§5.7.2) and all-reduce failure results (§5.7.1, §6.4):** not read.
- **`docs/prior-work.md` Psyche entry** (Consilience 40B, "moving from provability to performance"): from a blog post read on 2026-10-07; not re-read in this strand.

## Gaps

- **No system found that defines the model by a checkable merge rule with no ledger and no single writer.** Among the sources read, every system that fixes a round's inputs uses either a ledger (Psyche, Templar) or a single coordinator or leader (INTELLECT-1, PCCL, Agora's Authorizer and reducers, Templar's leader validator). This is a negative result over the sources read, not an exhaustive search.
- **IOTA (Macrocosmos, arXiv 2507.17766)** was not re-read. The 2026-10-11 notes (`04a-spes-and-citers.md`, §2 read) record an orchestrator that assigns each miner a layer.
- **Hivemind and DeDLOC membership in practice** (how a run with only a DHT decides who is in a group, as in Moshpit or DeDLOC) were not read here. Strand 1 (discovery) and strand 4 (averaging) cover them.
- **Gensyn REE** (`gensyn-ai/ree`) and the RepOps evaluation in Verde were not read.
- **The SAPO paper** was read at abstract level only.
- **Psyche's documentation website** (as opposed to the in-repo book) was not fetched; the in-repo book at the commit read was used instead.
- **Discovery searches were few.** Discovery relied mainly on GitHub organisation listings of the named projects plus two WebSearch queries. Systems outside those organisations (for example other Bittensor training subnets, or academic systems using object storage as the exchange layer) may be missed.
- **Costs of the ledger route** (transaction fees, RPC providers, chain availability) were not measured or read for any chain.

## Query log

- 2026-10-13 17:19:05 TST: `gh api repos/{PsycheFoundation/psyche, NousResearch/psyche, tplr-ai/templar, PrimeIntellect-ai/prime, PrimeIntellect-ai/prime-rl, PrimeIntellect-ai/protocol, PrimeIntellect-ai/toploc, gensyn-ai/rl-swarm, PluralisResearch/node0}`. Redirects found: `PsycheFoundation/psyche` resolves to `PsycheFoundation/nousnet`; `tplr-ai/templar` resolves to `one-covenant/templar`. `NousResearch/psyche` is 404.
- 2026-10-13 17:19:23 TST: `gh api orgs/{PsycheFoundation, one-covenant, PluralisResearch, gensyn-ai}/repos?per_page=100&sort=pushed`.
- 2026-10-13 17:19:34 TST: `gh api orgs/PrimeIntellect-ai/repos?per_page=100&sort=pushed`. The repository now named `PrimeIntellect-ai/prime` describes itself as a CLI and SDK; the training framework description ("prime is a framework for efficient, globally distributed training") is on `PrimeIntellect-ai/prime-diloco`.
- 2026-10-13 17:20:14 TST: first `git clone --depth 1` of ten repositories. Only `one-covenant/templar` and `gensyn-ai/rl-swarm` succeeded; the rest failed with "Filename too long" (Windows path limit under the long scratchpad path). Method note: retried with `git -c core.longpaths=true` and short directory names.
- 2026-10-13 17:20:50 TST: shallow clones of `PsycheFoundation/nousnet`, `PrimeIntellect-ai/prime-diloco`, `PrimeIntellect-ai/protocol`, `PluralisResearch/node0`, `PluralisResearch/agora`, `gensyn-ai/rl-swarm-contracts`, `gensyn-ai/gensyn-audit`, `gensyn-ai/open-transformers` succeeded. HEAD SHAs are recorded in each source block. Nothing cloned was run, built or installed.
- 2026-10-13 17:21:19 TST: arXiv API over `http://export.arxiv.org` returned nothing; retried over `https://` at about 17:21:26 (response `updated` 2026-10-13T14:21:26Z) for IDs 2603.08163, 2505.21684, 2412.01152, 2505.07291, 2501.16007, 2607.13332, 2502.19405, 2509.08721, 2505.14065. All nine titles confirmed.
- 2026-10-13 17:21:34 to 17:22:14 TST: PDFs downloaded from `https://arxiv.org/pdf/<ID>v<N>` with `sleep 3` between requests: 2603.08163v2, 2505.21684v1, 2412.01152v1, 2505.07291v1, 2501.16007v2, 2607.13332v1, 2502.19405v1, 2509.08721v1, 2505.14065v1; converted with `/mingw64/bin/pdftotext -layout`.
- 2026-10-13 17:22 to 17:34 TST: reading of the cloned Psyche, Templar, `prime-diloco` and protocol trees and of the downloaded PDFs (files and lines listed per source block).
- 2026-10-13 17:34:21 TST: `gh api repos/{gensyn-ai/open-transformers, gensyn-ai/gensyn-audit, gensyn-ai/ree, gensyn-ai/rl-swarm-contracts, PluralisResearch/agora, PluralisResearch/node0}` (fields `license.spdx_id`, `pushed_at`, `created_at`, `archived`).
- 2026-10-13 17:36:29 TST: `gh api repos/learning-at-home/hivemind/commits/master`, `repos/huggingface/hub-docs` and `.../commits/main`, `repos/github/docs` and `.../commits/main` (for commit SHAs). Then raw fetches from `raw.githubusercontent.com` at those SHAs: `hivemind/dht/crypto.py`, `hivemind/dht/validation.py`.
- 2026-10-13 17:36:53 TST: `gh api repos/huggingface/hub-docs/contents/docs/hub?ref=ef42b8f...` (file list); raw fetches of `security-tokens.md`, `organizations-security.md`, `security-gpg.md`, `security-pickle.md`, `storage-buckets-security.md`, `repositories-settings.md`.
- 2026-10-13 17:37:29 TST: `gh api repos/github/docs/contents/...` (file lists); raw fetches of `managing-your-personal-access-tokens.md`, `available-rules-for-rulesets.md`, `about-rulesets.md`.
- 2026-10-13 about 17:40 TST: WebSearch "decentralized LLM training without blockchain coordinator shared object storage deterministic aggregation 2026": no system matching the description; results were FusionLLM (arXiv 2410.12707), a survey (arXiv 2503.11023) and a forum post. Nothing recorded from them.
- 2026-10-13 about 17:40 TST: WebSearch "Psyche Nous verification witness verifier implemented 2026": no relevant results.
- 2026-10-13 17:42:16 TST: `gh api repos/huggingface/huggingface_hub/commits/main` and `repos/huggingface/huggingface_hub`; raw fetch of `src/huggingface_hub/hf_api.py` at that SHA (S15).
- 2026-10-13 17:44:55 TST: `gh api repos/learning-at-home/hivemind` (`license.spdx_id`, `pushed_at`, `archived`) for S12.
- WebFetch was not used. No number or claim in these notes comes from a search snippet.

**Not covered in this strand:** IOTA (not re-read); Hivemind/DeDLOC/Moshpit membership in practice (strands 1 and 4); Gensyn REE; the TOPLOC paper body; Agora §4 to §6 except the parts listed; Psyche's documentation website; any chain's fees or availability; discovery beyond the named organisations and two WebSearch queries.
