# Audit 4: unverified items stay in section 7

Report audited: `docs/research/2026-10-13-system-study-report.md`, frozen copy `report_preaudit.md` (715 lines; identical to the live file at audit start, `diff -q` silent). Scope: header block and sections 1 to 6 (lines 1 to 582). Section 7 = lines 583 to 686. Line numbers below refer to the frozen copy.

Method: every "Could not verify" bullet in the seven notes files, plus inline markers ("not read", "not checked", "not confirmed", "unverified", "figure only", "abstract only", "garbled", "vendor claim", "not stated", "not established"), compiled with an ID. Each item got 2 to 8 search tokens (name, key number, key phrase); `scripts/search_items.py` searched lines 1 to 582 for all of them (raw dump: `hits_raw.txt`, 117 searched items, 632 lines). Every hit was then read and classed by hand against the notes. Hits where a token matched something unrelated (e.g. "R2" the requirement, Ford's own 64%) are recorded as "incidental" and not counted.

Classes: **OK-pointer**; **OK-verified-elsewhere** (another note, or the earlier Stage 0 notes, verified it at source); **OK-abstract-only**; **OK-search-finding**; **PROBLEM**. Four extra labels were needed and are counted separately: **OK-verified-part** (the report uses only the part of a source that was read; the unverified part is not used), **OK-figure-only** (a text statement about a figure-only result, no value read off the figure; applied uniformly to the labelled and unlabelled cases), **UNKNOWN-missing-from-7** (stated only as unknown, but the item is absent from section 7), and **NOTE** (design text in section 4 resting on an unverified premise; not stated as a finding).

---

## 1. Compiled unverified items

CNV = under the file's "Could not verify" heading; inline = marked elsewhere in the file.

### w1a (13 items: 5 CNV, 8 inline)
- w1a-01 (CNV) Second-hand NAT numbers cited by Trautwein et al.: Halkes and Pouwelse 2011 (~64% punchable, >80% success), Guha and Francis 2005 (88% TCP over 93 home NATs), ~11% EDM NATs; Seemann et al. 2022.
- w1a-02 (CNV) iroh's "roughly 9 out of 10 network configurations allow a direct connection" (vendor claim, no method).
- w1a-03 (CNV) Who operates Psyche's relay hosts under `iroh.link`.
- w1a-04 (CNV) py-libp2p README "Done" status for relay v2, AutoNAT, hole punching.
- w1a-05 (CNV) rust-libp2p pnet over QUIC.
- w1a-06 (inline) Trautwein 2510.27500 v1 body not read; figures not readable (values from text only).
- w1a-07 (inline) ProbeLab sub-reports (`nat-classification.md`, `dcutr-testbed.md`, `dcutr-audit.md`) not read.
- w1a-08 (inline) go-libp2p-kad-dht issue #387 not read.
- w1a-09 (inline) iroh docs `add-a-relay.md`, `dedicated-infrastructure.md` downloaded, not read.
- w1a-10 (inline, gap 8) rust-libp2p routing-table persistence not checked.
- w1a-11 (inline, gap 7) iroh relay without DNS name or certificate (`--dev`): hole punching still works? (also w2a CNV "still open").
- w1a-12 (inline) Hyperswarm / HyperDHT not read in w1a (HyperDHT later read in w2c N3).
- w1a-13 (inline) Tailscale, Headscale, DERP, ZeroTier, Yggdrasil, WebRTC ICE not read.

### w1b (23 items: 11 CNV, 12 inline)
- w1b-01 (CNV) Decoupled DiLoCo Table 14, 2B column: printed 52.3 / 51.6 do not match per-task averages.
- w1b-02 (CNV) Decoupled DiLoCo Table 15: reference run of the deltas not stated (scavenging deltas unused).
- w1b-03 (CNV) Decoupled DiLoCo Table 5: caption and §5.4 name different TPU generations.
- w1b-04 (CNV) HALoS Table 1: which method produced the reference loss; whether 70M and 410M columns follow the 160M protocol ("from scratch on 12.9B tokens").
- w1b-05 (CNV) HeLoCo abstract figures ("up to 7.5%", "22.1%", "3.3%").
- w1b-06 (CNV) Venues not confirmed: D-PSGD NeurIPS 2017, AD-PSGD ICML 2018, HALoS ICML 2025, Factored Gossip ICML 2026.
- w1b-07 (CNV) NoLoCo pairing mechanism (closed by w2b B10).
- w1b-08 (CNV) Factored Gossip: who draws the pairwise matching.
- w1b-09 (CNV) Momentum Look-Ahead (MLA): not read.
- w1b-10 (CNV) Hivemind's averager is Moshpit All-Reduce? (closed by w2b B1).
- w1b-11 (CNV) SWARM Appendix A, AD-PSGD Appendix A, D-PSGD NLP supplement not read (SWARM App. A read in part by w2b B6).
- w1b-12 (inline) Async Local-SGD wall-clock result (Fig. 2, figure only); `asyncdiloco` code not read.
- w1b-13 (inline) Moshpit §4.1 Fig. 3 and §4.2 Fig. 4 results (figure only).
- w1b-14 (inline) DeDLOC: sahajBERT curves "virtually identical" and WikiText-103 slowdowns (figures only); App. I.5 (allowlist) not read (read by w1d P10).
- w1b-15 (inline) SWARM "training dynamics ... similar" (Fig. 4, figure only).
- w1b-16 (inline) NoLoCo Fig. 7 and Fig. 5 (figure only); App. D to F not read.
- w1b-17 (inline) Factored Gossip's attribution of NoLoCo's gap to the missing Nesterov look-ahead "not confirmed experimentally"; its code not checked.
- w1b-18 (inline) GASLoC Fig. 3, Fig. 4 (figure only).
- w1b-19 (inline) Streaming DiLoCo per-worker slack (Fig. 10, figure only).
- w1b-20 (inline) Learning@home MNIST robustness (Fig. 5, figure only).
- w1b-21 (inline) EDiT tables garbled (no number); PALSGD abstract and grep only; "Not Every Sync Is Safe" abstract only.
- w1b-22 (inline) FoMoE and DiPaCo "not re-read" (read in full in Stage 0 notes 04a, 04b, 06).
- w1b-23 (inline) Not opened: SeedFlood, Epidemic Learning, SPARTA, GWTF, 1907.11612, FedBuff, Papaya, HGA-FL, FedAH, DiLoCoX.

### w1c (24 items: 14 CNV, 10 inline)
- w1c-01 (CNV) Psyche `update` while a run is active.
- w1c-02 (CNV) Psyche verification implemented after 2026-03-20 elsewhere.
- w1c-03 (CNV) Psyche joiner checks the assembled model against a hash.
- w1c-04 (CNV) Psyche relay hostnames and their operator.
- w1c-05 (CNV) Which process hosts prime-diloco's `god_store`.
- w1c-06 (CNV) Tailscale's architecture, hence its (c) classification.
- w1c-07 (CNV) Bittensor validator consensus (Yuma); do miners ever follow a validator other than the highest-staked.
- w1c-08 (CNV) Bitwise identity of Templar miners' models.
- w1c-09 (CNV) RepOp licence.
- w1c-10 (CNV) Hub fine-grained token restricting writes to one repository.
- w1c-11 (CNV) GitHub per-path write limits (absence in parts read only).
- w1c-12 (CNV) TOPLOC paper not read.
- w1c-13 (CNV) Agora §5.7.2, §5.7.1, §6.4 not read (all-reduce failure results read by w2b B11 as v1 §3.5.3 and §6.4).
- w1c-14 (CNV) `docs/prior-work.md` Psyche entry (Consilience 40B blog) not re-read.
- w1c-15 (inline) SAPO paper: abstract only.
- w1c-16 (inline, S15 Fit line) Whether the Hub server, rather than the client, enforces `parent_commit`: "not read".
- w1c-17 (inline) IOTA not re-read.
- w1c-18 (inline) Gensyn REE and Verde's protocol / RepOps evaluation not read.
- w1c-19 (inline) Costs of the ledger route (fees, RPC, availability) not read.
- w1c-20 (inline) Psyche documentation website not fetched.
- w1c-21 (inline) Gauntlet Algorithm 1 garbled, not relied on.
- w1c-22 (inline) INTELLECT-2 Figure 3 garbled.
- w1c-23 (inline) RL Swarm README grep only.
- w1c-24 (inline) Hivemind / DeDLOC membership in practice not read.

### w1d (20 items: 12 CNV, 8 inline)
- w1d-01 (CNV) Hub commit rate limits (exist, undocumented).
- w1d-02 (CNV) "Best-effort" free storage; bucket free allowance not quantified.
- w1d-03 (CNV) BEP 19 web seeds on Hub or GitHub URLs.
- w1d-04 (CNV) Whether R2's "checkout flow" requires a payment card.
- w1d-05 (CNV) Whether GitHub release downloads count against REST limits.
- w1d-06 (CNV) Whether `cosign sign-blob --key` uploads to Rekor by default.
- w1d-07 (CNV) Whether pip verifies PEP 740 attestations.
- w1d-08 (CNV) DisTrO's algorithm (not described; `distro.rs` not read).
- w1d-09 (CNV) Psyche run-manager image-signature check (grep of two files).
- w1d-10 (CNV) How a joining peer gets the model in Covenant-72B.
- w1d-11 (CNV) SparseLoCo 178M (App. J) and Table 5 (garbled).
- w1d-12 (CNV) prime-diloco = INTELLECT-1's framework (rests on description and checkpoint code).
- w1d-13 (inline, S2 question) Whether a multi-file Hub commit becomes visible all at once ("not stated in H1").
- w1d-14 (inline, gaps) Xet deduplication savings on successive training updates (not measured).
- w1d-15 (inline) Figure-only quality results: DeMo §3.5 (Figs. 5, 6), Streaming DiLoCo Fig. 11, MuLoCo Fig. 7, OpenDiLoCo Fig. 6.
- w1d-16 (inline) DisTrO report Tables 1 and 2 garbled (not used); Table 3 row layout garbled, mapping recovered from the "857x" in §3.
- w1d-17 (inline) Hivemind `state_averager.py` fetched, not read (in w1d).
- w1d-18 (inline) Covenant-72B validator operator not stated.
- w1d-19 (inline) Hub `storage-buckets-s3.md` grep only.
- w1d-20 (inline) Not read: PyTorch DCP docs, GitHub Additional Product Terms, Cloudflare terms, IPFS pinning terms, INTELLECT-3, DiLoCoX.

### w2a (18 items: 13 CNV, 5 inline)
- w2a-01 (CNV) Per-expert Hivemind averager under its own key prefix matches only holders (docstring inference).
- w2a-02 (CNV) PCCL `peer_group` for overlapping holder groups.
- w2a-03 (CNV) PCCL NAT traversal and master failover (answered from docs by w2b B8).
- w2a-04 (CNV) py-libp2p NAT traversal on Windows; interop with go and rust.
- w2a-05 (CNV) iroh-ffi Python custom-relay support (`support-matrix.yaml` claim); `--dev` hole punching still open.
- w2a-06 (CNV) Psyche's current status (docs.psyche.network not fetched); "Development appears paused or moved ... not established".
- w2a-07 (CNV) prime-diloco's 2026 pushes went to other branches (inference, not checked).
- w2a-08 (CNV) Issue-count discrepancies (rust-libp2p 303 v 299; Node0 6 v 2).
- w2a-09 (CNV) RL Swarm community swarms; README notice and body conflict.
- w2a-10 (CNV) Flower native Windows support.
- w2a-11 (CNV) BOINC Windows client (inferred from CI).
- w2a-12 (CNV) Python bindings for go-libp2p and rust-libp2p.
- w2a-13 (CNV) `agora` on PyPI.
- w2a-14 (inline) Hivemind synchronous mode as one group of all peers: "not tested anywhere read".
- w2a-15 (inline) iroh blobs crate not checked.
- w2a-16 (inline) Psyche `python/` directory not read.
- w2a-17 (inline) PCCL `docs/` and Agora `docs/` not read (two PCCL docs pages read by w2b B8).
- w2a-18 (inline) `prime-rl` recorded as a lead, not read.

### w2b (17 items: 12 CNV, 5 inline)
- w2b-01 (CNV) Petals rebalancing threshold: paper p = 20% v code ~33%.
- w2b-02 (CNV) SWARM Table 5 row assignment.
- w2b-03 (CNV) Whether SWARM §4.3/§4.4 used rebalancing code absent from the repo.
- w2b-04 (CNV) Psyche's live Consilience settings v repository `state.toml`.
- w2b-05 (CNV) Hivemind `k_min` counting over the batch.
- w2b-06 (CNV) Hivemind `_load_state_from_peers` timeout replacement.
- w2b-07 (CNV) Learning@home DHT persistence in older `mryab/learning-at-home` code.
- w2b-08 (CNV) NoLoCo's default torch.distributed (gloo) timeout in its pinned version.
- w2b-09 (CNV) Agora backward pinning under failure (grep only).
- w2b-10 (CNV) PCCL `test_peer_groups.cpp` not read.
- w2b-11 (CNV) Bamboo cost 2.4x (abstract) v 3.6x (§1).
- w2b-12 (CNV) Agora "operating threshold near 85%": one ablation run.
- w2b-13 (inline) Learning@home Figs. 5 and 6 (figure only).
- w2b-14 (inline) Petals Appendix E (figure only).
- w2b-15 (inline) SWARM Figure 6 and Agora Figure 15d (figure only).
- w2b-16 (inline) Bamboo §7 garbled, §2 and §4 not read; Petals 2022 paper abstract page only; Node0 code cloned, not read; Agora code grep only.
- w2b-17 (inline) SWARM's vendored averager: semantics inferred from B1's later version, not re-read.

### w2c (21 items: 11 CNV, 10 inline)
- w2c-01 (CNV) Venues of LambdaML (SIGMOD 2021) and FedLess (IEEE BigData 2021): search results only.
- w2c-02 (CNV) LambdaML Table 6 garbled.
- w2c-03 (CNV) FedLess Fig. 12 cost values.
- w2c-04 (CNV) STUNMESH-go success in practice; docs site and FOSDEM talk not read.
- w2c-05 (CNV) HF²L webhook workflow and Exchange service (`docs/`, code not read).
- w2c-06 (CNV) Hivetrain operating history.
- w2c-07 (CNV) Whether the Hub assigns `uploadedAt` server-side.
- w2c-08 (CNV) IPLS, GFL, BRFL, GitFL, FLHub: search results only.
- w2c-09 (CNV) Tailscale "few seconds of latency" side-channel claim (author's statement).
- w2c-10 (CNV) Hyperswarm cloned, not read.
- w2c-11 (CNV) Flower "Fault Tolerant FedAvg" implementation.
- w2c-12 (inline) Flower §5.3 cutoff variant: dataset not confirmed.
- w2c-13 (inline) Plexus §4 experiments not read beyond the abstract.
- w2c-14 (inline) Hivetrain `send_interval=800`: unit not confirmed (`DeltaLoop` not read).
- w2c-15 (inline, line 364) Whether a repository commit date can be set by the client: "not stated (Could not verify)".
- w2c-16 (inline) BOINC "hundreds of jobs per second" cites [17], not read.
- w2c-17 (inline) STUNMESH-go exec plugin backed by a file host: (b) by inference, not tested.
- w2c-18 (inline) HyperDHT: no success rates in files read; `lib/connect.js` skimmed.
- w2c-19 (inline) Tailscale blog: sections beyond side channel, firewall timeout, IPv6, TL;DR not read.
- w2c-20 (inline) Asyn2F and T5 (gRPC+S3): grep only.
- w2c-21 (inline) BOINC paper journal version not checked.

**Total compiled: 136** (w1a 13, w1b 23, w1c 24, w1d 20, w2a 18, w2b 17, w2c 21). Of these, 117 were searched with tokens; the remaining 19 are leads or reading-coverage notes whose names were checked with a single combined grep (SeedFlood, Epidemic, SPARTA, GWTF, FedBuff, Papaya, DiLoCoX, INTELLECT-3, torchft, ZeroTier, Yggdrasil, WebRTC, Headscale, prime-rl, Apodotiko, FLStore, LIFL, SMLT, FLSys, harmonia, IOTA, 1907.11612, Gemini, Asyn2F, gRPC, DERP): no use in scope except "Varuna" inside Oobleck's own claim (L279, Oobleck read in w2b B14).

---

## 2. Notes in conflict: w1b items closed by w2b

| w1b item | Closed by | Report's handling | Verdict |
|---|---|---|---|
| Hivemind's averager is Moshpit All-Reduce (w1b CNV) | w2b B1: `key_manager.py` lines 94 to 105; Moshpit when initial group bits are set, plain group all-reduce otherwise (code read, inference) | Section 7 (L588) says it is not used in 1 to 6. Confirmed: no line asserts the identity. L66 "Moshpit SGD, DeDLOC (group averaging, run on Hivemind)" rests on w2b B3 (Moshpit's ALBERT loop uses Hivemind 0.9.5 `DecentralizedAverager`) and w2b B4 (DeDLOC uses `hivemind.CollaborativeOptimizer`), not on the identity. L462 "Moshpit-style group averaging, w1b S3" names the paper's algorithm. | Consistent |
| NoLoCo's pairing (w1b CNV) | w2b B10: `create_random_permutation(world_size, self._step)`, seeded by the step counter; fixed world (code read) | Used at L69 "(w2b B10, C)", L286 "(w2b B10)", L427 and L430 "(w2b B10)". Each cites w2b B10; L69 carries the C letter; section 4 is under its "all inference" preamble; section 7 L587 labels the whole as "an inference from code that was not run". | Consistent, with two exceptions below |

Exceptions:
- **L275 overstates w2b's reading** (PROBLEM P2): "NoLoCo's blocking pair exchange" listed as able to "wait indefinitely". w2b B10 says it blocks "until torch.distributed's default timeout, which then raises"; w2b F2 qualifies "up to the library default"; that default is itself unverified (w2b CNV; section 7 L661).
- **Section 7 L587 is incomplete**: "only the NoLoCo item is used there (Q6, section 4.1)". It is also used in section 2.2 (L69). Fix: "(section 2.2, Q6, section 4.1)".

Two further closures that section 7 does not record as such (it still lists them as unverified while sections 1 to 6 use the later strand's reading; harmless for the rule, but section 7's preamble "Nothing in this section is used as evidence in sections 1 to 6" is then untrue for them):
- PCCL NAT traversal and master failover (w2a CNV; section 7 L642): answered from PCCL's docs by w2b B8 ("Master Crash = End of Run"; "Peers need open ports or port forwarding ... no relays", `03_MasterOrchestration.md`). Used at L59, L276, L506 citing w2b B8. Fix: move to section 7's "listed as open and a later strand closed" paragraph.
- Agora's all-reduce failure results (w1c CNV; section 7 L622): w2b B11 read v1 §3.5.3 and §6.4 in full and maps w1c's §5.7.1 and §6.4 onto them. Used at L279 citing w2b F6. Fix: same move, keeping only "inter-replica divergence (§5.7.2)" as open.

---

## 3. Hits in scope, classified

One row per (item, line). Incidental token matches are listed at the end of the table, not counted.

| Item | Line | Class | Basis |
|---|---|---|---|
| w1a-03 | 56 | OK-verified-part | "defaults are project relays" from code (w1a S15, C); operator not claimed |
| w1a-03 | 122 | OK-verified-part | "project-named relays"; operator not claimed |
| w1a-04 | 328 | OK-pointer | "as go-libp2p, by its own claims (section 7)" |
| w1a-04 | 468 | OK-pointer | "py-libp2p's NAT traversal is unconfirmed" (no explicit "section 7", but no claim) |
| w1a-05 | 327 | OK-verified-part | rust-libp2p "as go-libp2p"; go row says "pnet over TCP"; no QUIC-pnet claim |
| w1a-06 | 113 | OK-verified-part | 2604.12484 v1 read in full; values from text; 2510.27500 not cited |
| w1a-06 | 138 | OK-verified-elsewhere | Trautwein's cited "40%" checked at its source, Richter et al. (w1a S13 correction) |
| w1a-07 | 114 | OK-verified-part | ProbeLab blog and report sections read; sub-reports not used |
| w1a-07 | 140 | OK-verified-part | 36% from the report sections read |
| w1a-08 | 91 | OK-verified-part | cites the code TODO naming #387, not the issue's content |
| w1a-09 | 121 | OK-verified-part | DNS name, TLS, ports 80 and 443 from `iroh-relay/README.md` (read whole; w1a S9, line 325) |
| w1a-10 | 105 | UNKNOWN-missing-from-7 | "routing-table persistence in rust-libp2p (not checked)"; no section 7 entry |
| w1a-11 | 142 | UNKNOWN-missing-from-7 | "whether iroh punches holes when its relay runs without a DNS name and certificate (w1a gaps 1 to 7)"; section 7 carries only the iroh-ffi half of w2a's bullet |
| w1b-01 | 210 | OK-verified-part | uses Table 12's 54.4 v 55.1, not Table 14's printed 52.3 / 51.6 |
| w1b-01 | 537 | OK-verified-part | same |
| w1b-03 | 210 | OK-verified-part | "heterogeneous TPUs"; no generation named |
| w1b-04 | 209 | OK-pointer | "(protocol of the 70M and 410M columns unconfirmed; section 7)"; but the Setting cell says "Pythia 70M / 160M / 410M from scratch" (wording fix suggested in section 7 below) |
| w1b-04 | 227 | PROBLEM | P1 |
| w1b-04 | 536 | OK-verified-part | ratios are read Table 1 values; "160M from scratch" is accurate; the L209 caveat is dropped (fix suggested) |
| w1b-04 | 548 | OK-verified-part | regime point holds on the 160M column alone |
| w1b-05 | 211 | OK-verified-part | HeLoCo Table 1 values, not abstract figures |
| w1b-05 | 538 | OK-verified-part | same |
| w1b-05 | 556 | OK-verified-part | Table 1 row (1,6,6,6,6), w1b gate item 2 |
| w1b-07 | 69 | OK-verified-elsewhere | w2b B10 (C) |
| w1b-07 | 286 | OK-verified-elsewhere | w2b B10 |
| w1b-07 | 427 | OK-verified-elsewhere | w2b B10 |
| w1b-07 | 430 | OK-verified-elsewhere | w2b B10 |
| w1b-07 | 275 | PROBLEM | P2 (NoLoCo part of the sentence; also item w2b-08) |
| w1b-10 | 66 | OK-verified-elsewhere | "run on Hivemind": w2b B3, B4 |
| w1b-10 | 462 | OK-verified-part | "Moshpit-style" names the paper's algorithm (w1b S3); no identity claim |
| w1b-11 | 277 | OK-verified-elsewhere | SWARM state "on all active nodes": w2b B6 read App. A in part |
| w1b-13 | 231 | OK-figure-only | Moshpit's text "achieves lower accuracy" (Fig. 4); no value |
| w1b-14 | 217 | OK-figure-only | labelled "(figures only)" |
| w1b-14 | 543 | OK-figure-only | labelled "(figure only)" |
| w1b-14 | 66 | OK-verified-elsewhere | allowlist authorization server: w1d P10 read the security appendix |
| w1b-18 | 540 | OK-verified-part | "551M 2-Peer equals DDP at 8 replicas" from Tables 2 and 3; figures unused |
| w1b-22 | 71 | OK-verified-elsewhere | FoMoE: Stage 0 notes 04a, 06 (full read) |
| w1b-22 | 199 | OK-verified-elsewhere | Stage 0 note 04a |
| w1b-22 | 218 | OK-verified-elsewhere | Stage 0 notes 06, 04a |
| w1b-22 | 224 | OK-verified-elsewhere | Stage 0 notes 04a, 04b, 06 |
| w1b-22 | 544 | OK-verified-elsewhere | Stage 0 notes via w1b S17 |
| w1c-01 | 159 | OK-verified-part | "changeable only by `main_authority`"; no "at any time" claim |
| w1c-02 | 150 | OK-verified-part | "`todo!()` at the commit read" |
| w1c-02 | 181 | OK-verified-part | code at the commit read (could add "at the commit read") |
| w1c-03 | 240 | OK-verified-part | layer-by-layer fetch (docs); no hash-check claim |
| w1c-05 | 58 | OK-verified-part | "master key-value store on rank 0": global `TCPStore` hosted by rank 0 (w1c S5, `comms.py` 95 to 100, 247); `god_store` not mentioned |
| w1c-05 | 152 | OK-verified-part | same |
| w1c-05 | 351 | OK-verified-part | same |
| w1c-06 | 58 | OK-pointer | "Tailscale, (c) by inference only (section 7)" |
| w1c-07 | 20 | OK-verified-part | one validator's list: code reads the highest-staked validator's bucket (w1c S2, `comms.py` 2239) |
| w1c-07 | 57 | OK-verified-part | same |
| w1c-07 | 128 | OK-verified-part | same |
| w1c-07 | 151 | OK-verified-part | same |
| w1c-08 | 151 | OK-verified-part | sync score "2 values per tensor" (Gauntlet §3.2, w1c S4); no bitwise claim |
| w1c-08 | 157 | OK-verified-part | tolerance check; no bitwise claim |
| w1c-08 | 422 | OK-verified-part | same (cites "w1c S8"; the sync score is in w1c S4 / S2: citation slip, aside) |
| w1c-10 | 306 | OK-pointer | "(section 7)" |
| w1c-10 | 491 | OK-pointer | last sentence: "unconfirmed (section 7)" |
| w1c-11 | 296 | OK-search-finding | "not paths, in the parts read" (w1c S14) |
| w1c-11 | 306 | OK-pointer | "(section 7)" |
| w1c-13 | 279 | OK-verified-elsewhere | Agora §6.4: w2b B11 read it in full |
| w1c-15 | 60 | OK-abstract-only | "(w1c S9, SAPO abstract only)"; claim is the abstract's |
| w1c-16 | 20 | OK-search-finding | "(inference; w1c S15); no source tests that" |
| w1c-16 | 36 | OK-pointer | dependency on prototypes (section 6) |
| w1c-16 | 167 | OK-verified-part | docstring quote; "a writer can skip the check" |
| w1c-16 | 409 | NOTE | Closer "other attempts fail (w1c S15)": design under section 4's inference preamble, rests on server-side enforcement |
| w1c-16 | 440 | NOTE | "the next peer's conditional commit succeeds (w1c S15)": same |
| w1c-16 | 486 | OK-pointer | "CAS behaviour" as a main unknown (item absent from section 7) |
| w1c-16 | 491 | PROBLEM | P5 |
| w1c-16 | 520 | OK-pointer | P4 dependency |
| w1c-16 | 574 | OK-pointer | P4 prototype |
| w1d-01 | 36 | OK-pointer | prototype dependency |
| w1d-01 | 176 | OK-pointer | "undocumented limits (Q5)" |
| w1d-01 | 249 | OK-verified-part | docs state limits exist and are undocumented (H2) |
| w1d-01 | 261 | OK-pointer | "See section 7" (listed at L626) |
| w1d-01 | 451 | OK-verified-part | same as L249 |
| w1d-01 | 575 | OK-pointer | P5 prototype |
| w1d-02 | 250 | OK-search-finding | "free allowance not quantified" |
| w1d-02 | 257 | OK-search-finding | same |
| w1d-02 | 261 | OK-pointer | listed at L627 |
| w1d-03 | 243 | OK-pointer | "not confirmed (section 7)" |
| w1d-03 | 254 | OK-verified-part | BEP 19 web seeds in general (H9); no Hub/GitHub claim |
| w1d-03 | 261 | OK-pointer | listed at L628 |
| w1d-04 | 253 | PROBLEM | P4 |
| w1d-04 | 448 | PROBLEM | P4 |
| w1d-04 | 525 | PROBLEM | P4 |
| w1d-05 | 251 | OK-verified-part | API limits (H7); no claim about download counting |
| w1d-06 | 311 | OK-verified-part | keyless Sigstore only; no `sign-blob --key` claim |
| w1d-07 | 311 | OK-verified-part | no pip claim |
| w1d-07 | 312 | OK-verified-part | PyPI Integrity API record only |
| w1d-08 | 371 | OK-verified-part | "not described" |
| w1d-08 | 378 | OK-verified-part | hedged "may not be the same algorithm" |
| w1d-09 | 312 | OK-pointer | "not confirmed (section 7)" |
| w1d-11 | 363 | OK-verified-part | Tables 1 and 7 (read); 178M and Table 5 unused |
| w1d-11 | 376 | OK-verified-part | scaled from 512M Table 1 (inference) |
| w1d-12 | 58 | PROBLEM | P6 |
| w1d-12 | 152 | PROBLEM | P6 (same pattern) |
| w1d-12 | 347 | OK-pointer | "(section 7 for the identity caveat)" |
| w1d-13 | 261 | UNKNOWN-missing-from-7 | "whether a multi-file Hub commit becomes visible at once ... See section 7": not in section 7 |
| w1d-13 | 574 | OK-pointer | P4 tests it |
| w1d-14 | 261 | UNKNOWN-missing-from-7 | "Xet deduplication savings ... See section 7": not in section 7 |
| w1d-15 | 365 | OK-figure-only | Streaming DiLoCo "no sign of performance regression" (§2.4, text) |
| w1d-15 | 366 | OK-figure-only | MuLoCo, labelled "(figures only)" |
| w1d-15 | 367 | OK-figure-only | OpenDiLoCo, labelled "(figure only)" |
| w1d-15 | 378 | OK-figure-only | "Dropping values is worse than lowering precision" (text statements of figure results) |
| w1d-16 | 371 | OK-verified-part | 86.8 MB / 74.4 GB: row mapping recovered from §3's stated 857x; losses (2.373 / 2.449) not used |
| w1d-17 | 239 | OK-verified-elsewhere | full-state download: w2b B1 (`optimizer.py`, `state_averager.py` read), B4 |
| w2a-01 | 51 | OK-pointer | "per-expert groups untested (w2a 1, D; section 7)" |
| w2a-01 | 66 | OK-verified-part | algorithm-level rating from the Moshpit paper; no Hivemind implementation claim |
| w2a-02 | 59 | OK-pointer | "peer groups per expert unconfirmed (section 7)" |
| w2a-03 | 59 | OK-verified-elsewhere | w2b B8 docs: "Master Crash = End of Run"; open ports, no relays |
| w2a-03 | 276 | OK-verified-elsewhere | w2b B8 |
| w2a-03 | 506 | OK-verified-elsewhere | w2b B8 |
| w2a-05 | 331 | OK-verified-part | wheel and classifier facts; no custom-relay claim |
| w2a-05 | 466 | OK-verified-part | "Python wheels (Alpha)"; no custom-relay claim |
| w2a-06 | 26 | PROBLEM | P3 |
| w2a-06 | 503 | OK-verified-part | "no commit since 2026-03-20" (API) |
| w2a-07 | 26 | OK-verified-part | prime-diloco part: w2a 9 "not actively maintained" (default branch) |
| w2a-07 | 333 | OK-verified-part | default-branch date only |
| w2a-07 | 347 | OK-verified-part | "no default-branch commit in 18 months" |
| w2a-07 | 504 | OK-verified-part | same |
| w2a-09 | 336 | OK-verified-part | README quote; no community-swarm claim |
| w2a-10 | 340 | OK-verified-part | wheel and classifiers only |
| w2a-11 | 341 | OK-verified-part | CI builds only |
| w2b-01 | 52 | OK-verified-part | "a sole holder never leaves" (code, w2b B5); no threshold value |
| w2b-03 | 285 | OK-verified-part | paper v README, both read; no claim on which code the experiments used |
| w2b-04 | 275 | OK-pointer | "whether the live run used them is unconfirmed, section 7" |
| w2b-07 | 283 | OK-verified-part | follows current code; no claim about the older repository |
| w2c-04 | 133 | OK-search-finding | "reports no success rates" |
| w2c-05 | 73 | OK-verified-part | HF²L README lines 194 to 206, 476 to 516 |
| w2c-05 | 131 | OK-verified-part | same |
| w2c-05 | 178 | OK-verified-part | same |
| w2c-06 | 129 | OK-search-finding | "Timings reported: none" |
| w2c-07 | 177 | OK-pointer | "not confirmed (see section 7)" |
| w2c-07 | 574 | OK-pointer | P4 |
| w2c-10 | 95 | OK-verified-part | HyperDHT read (w2c N3); Hyperswarm not used |
| w2c-13 | 172 | OK-verified-part | Plexus §3.1 and §5 read; §4 experiments unused |
| w2c-14 | 129 | OK-verified-part | 1,200 s period confirmed by `averaging_logic.py` line 544; `send_interval` unused |
| w2c-17 | 133 | OK-search-finding | "File-host-coordinated punching ... untested anywhere read" |

Items with no use in scope (search returned no hit, or only incidental hits): w1a-01, -02, -12, -13; w1b-02, -06 (only the verified venues IMC '26 and IMC 2016 appear), -08, -09, -12, -15, -16, -17, -19, -20, -21, -23; w1c-04, -09, -12, -14 (the "40B" at L275 is the `state.toml` run ID), -17, -18, -19, -20, -21, -22, -23, -24; w1d-10, -18, -19, -20; w2a-08, -12, -13, -14, -15, -16, -17, -18; w2b-02, -05, -06, -09, -10, -11 (L279's 3.7x is Bamboo's throughput, not its cost figure), -12, -13, -14, -15, -16, -17; w2c-01, -02, -03, -08, -09, -11, -12, -15, -16, -18, -19, -20, -21.

Incidental matches (not counted): "R2" the requirement (about 15 lines); Ford's 64% TCP (L115); Richter's ">90% cellular" (L117); "persist" in go/Hivemind/IPFS statements (L51, L54, L75, L91, L243, L255); NoLoCo, Factored Gossip, GASLoC, Moshpit, SWARM, Agora, PCCL, Bamboo, Oobleck, BOINC, Flower, PyPI paper or API results unrelated to the unverified part; "pinning" (IPFS) for Agora's pinning; "REST" in "the rest"; "blocking" in other senses.

---

## 4. Converse check

Every notes block cited in scope was listed (`grep -o` of "w1a S..", "w2b B..", etc.; 100 distinct blocks plus Stage 0 notes 01, 04a, 04b, 06). Each exists in its notes file with a read status. Locators spot-checked against the recorded reading, all passing: Trautwein abstract, §5.2.1, §5.2.3, §6, IMC '26 (w1a S1); Ford §1, §6.2 (w1a S2); Richter IMC 2016 (w1a S13); RFC 7021 §3.1 (w1a S12); iroh relay README (w1a S9); Async Local-SGD Tables 1 to 3 (w1b S2); GASLoC Tables 1b, 2, 3 (w1b S10); HALoS Table 1 (w1b S12); HeLoCo Table 1 and §4.2 (w1b S11); NoLoCo App. C, Table 1 (w1b S8); Factored Gossip App. B.1, +6.6% arithmetic (w1b S9, F3); Decoupled DiLoCo Tables 5, 10, 12, App. B, E (w1b S1); nanochat-DiLoCo Table 1 (w1b S15); INTELLECT-2 §2.4.3 (w1c S6); Gensyn "code, not data" (w1c S8); Templar leader validator and joiners (w1c S2); `parent_commit` docstring (w1c S15); Training Transformers Together §2, §3.3 (w1d P11); DeDLOC access passes (w1d P10); R2 pricing (w1d H12); DisTrO README "seed research/idea" (w1d P2); PCCL §2.5.3, master doc (w2b B8); Agora §5.1, §5.3.2, §6.4 (w2b B11); Oobleck 29.6x (w2b B14); Petals sole holder (w2b B5); Hivetrain 1,200 s (w2c T7); HF²L README (w2c T8); flwr-serverless §5 threads (w2c T2); Plexus §3.1, §5 (w2c F3).

**Result: no source cited with a claim in sections 1 to 6 lacks a recorded reading.**

Asides for the citation audit (not this rule): L422 and L576 cite Templar's sync score as "(w1c S8)"; it is recorded in w1c S4 (Gauntlet §3.2) and S2; S8 is OPEN-1B (correct only for the hash-check half of L576). L541's "+6.6%" is w1b's arithmetic and is not marked "(inference)".

---

## 5. Items used in scope but missing from section 7

Each is mentioned in scope only as unknown or as a prototype question (none stated as fact except via P5), but section 7 lacks it; two of them sit behind an explicit "See section 7".

| Item | Lines | Fix |
|---|---|---|
| w1c-16 Whether the Hub server, not only the client, enforces `parent_commit` (w1c S15 "not read") | 409, 440, 486, 491, 520, 574 | Add to section 7 under w1c: "Whether the Hub server, rather than the client library, enforces `parent_commit` (S15 read the docstring only)." |
| w1d-13 Whether a multi-file Hub commit becomes visible at once (w1d S2 question; "not stated in H1") | 261 ("See section 7"), 574 | Add under w1d. |
| w1d-14 Xet deduplication savings on successive training updates (w1d gaps, not measured) | 261 ("See section 7") | Add under w1d, or change L261's pointer to "(w1d gaps)". |
| w1a-10 rust-libp2p routing-table persistence (w1a gap 8, "not checked") | 105 | Add under w1a. |
| w1a-11 Whether iroh punches holes with a relay lacking a DNS name and certificate (`--dev`) (w1a gap 7; w2a CNV "still open") | 142 | Add under w1a or w2a (section 7 L644 carries only the iroh-ffi half of w2a's bullet). |

Section 7 also over-lists two items that sections 1 to 6 use through a later strand (PCCL NAT and master failover via w2b B8; Agora all-reduce failure results via w2b B11): see section 2 above.

---

## 6. Class (c) check (section 4)

Grep of lines 384 to 527 for STUN, DHT, relay, Solana, Bittensor, ledger, chain, IPFS, pkarr, n0, mainline, Amino, event stream, Tailscale, Sigstore, Rekor, "(c)", public, tracker, torrent, DNS, mirror.

- **Option A** (L401 to 456): host (b) only; L448 "Nothing of class (a) or (c)"; flags the bucket event stream (borderline) and R2. No public network for live coordination. Clean.
- **Option B** (L458 to 468): relays and bootstrap are our own reachable machines (L460); L467 "Library defaults (n0 relays and discovery, IPFS bootstrap) are class (c) and must be replaced." Address refresh through a host file (b). Clean.
- **Option C** (L470 to 472): A plus "our intermittent machines as relays"; direct links only where P2 (our relays) measures them. Does not silently rely on public STUN; STUN is flagged as the owner's decision at L135 and L34. Clean.
- **Ledger** (L494): "Not recommended for the pilot ... class (c) ... flagged for Phase 6." Psyche, Templar, Hivemind's all-NAT mode marked (c) in 4.6 (L502 to 505). Clean.
- **Recommendation** (L511 to 525): R2 bucket "(flagged)"; no (c) element.

**No design in section 4 relies silently on a class (c) network.** Three observations for the owner, none a PROBLEM:
1. L420 "mirrored to a second host" does not name the host. It is (b) only if the mirror is a static host such as a GitHub release; an IPFS or BitTorrent mirror would bring (a) or (c) (L254, L255). Suggest "(b), e.g. a GitHub release".
2. The round log uses the Hub's conditional-commit API as the live coordination point. The report classes it (b) as a host R2 names, which is consistent with R2; it is the one place a (b) host does coordination work, and the bucket event stream is already flagged borderline on similar grounds. The owner may want to confirm this reading.
3. P1 (L571) needs an outside view of each home's address and NAT class; if a public STUN or address-echo service is used, that is (c) for measurement only, not coordination. Worth a word in P1.

---

## 7. PROBLEM list

Ordered by weight. All are local wording fixes; none changes a conclusion.

**P1. L227 (Q4, "Where sources disagree").**
Text: "Async Local-SGD's parity with synchronous DiLoCo (fine-tuning, 4 to 16 workers) against HALoS's 19% to 31% token cost for the same algorithm from scratch."
Why: 19% and 31% are the 70M and 410M columns. w1b could not confirm that those columns follow the 160M "from scratch on 12.9B tokens" protocol (w1b CNV; section 7 L602). The sentence asserts "from scratch" for them without a pointer, though L209 carries the caveat.
Fix: "... against HALoS's 24.8% token cost for the same algorithm from scratch at 160M (18.6% and 30.9% at 70M and 410M, whose protocol is not confirmed; see section 7)." Related wording: L209's Setting cell "Pythia 70M / 160M / 410M from scratch" should read "Pythia 160M from scratch (70M and 410M: protocol unconfirmed)"; L536 should carry the same caveat as L209.

**P2. L275 (Q6).**
Text: "Two places can wait indefinitely: prime-diloco's non-leaders waiting for a dead leader (...) and NoLoCo's blocking pair exchange (w2b B9, B10)."
Why: w2b B10 says NoLoCo's exchange blocks "until torch.distributed's default timeout, which then raises", and w2b F2 qualifies "up to the library default". That default is unverified (w2b CNV; section 7 L661). "Indefinitely" states more than the code reading supports and leans on the unchecked value.
Fix: "One place can wait indefinitely: prime-diloco's non-leaders ... (`comms.py` lines 407 to 414). NoLoCo's blocking pair exchange waits until torch.distributed's default timeout, then raises (default not checked; see section 7) (w2b B9, B10)."

**P3. L26 (Summary, finding 3).**
Text: "Hivemind, Petals, Psyche, prime-diloco and Templar are dormant or barely maintained, ..."
Why: Psyche's status is a section 7 item (L645, "Psyche's current status"). w2a 8: "Development appears paused or moved out of this repository; not established." The summary states it as fact.
Fix: "Hivemind, Petals, prime-diloco and Templar are dormant or barely maintained, and Psyche's repository has had no default-branch commit since 2026-03-20 (its current status is not confirmed; see section 7); none documents native Windows support; ..."

**P4. L253, L448, L525 (Q5 host table; Option A; "What would change it").**
Text: L253 "(b), but an account the owner pays for: flag against R1"; L448 "Cloudflare R2 (an owner-paid account)"; L525 "an owner-paid R2 bucket (flagged)".
Why: w1d H12 says R2 "is free to get started with included free monthly usage" and that a bucket is a service the owner "may end up paying for". Whether the checkout needs a payment card is a section 7 item (L629). "Owner pays" is stated as fact.
Fix: L253 "(b), but an R2 subscription the owner may end up paying for (free tier exists; whether checkout needs a payment card is not confirmed, section 7): flag against R1"; L448 and L525 "an owner-subscribed R2 account (possibly paid; section 7)".

**P5. L491 (section 4.5, R7).**
Text: "... appended with conditional commits, so forged entries are ignored and races cannot overwrite each other."
Why: w1c S15 read only the client docstring; "Whether the server, rather than the client, enforces anything beyond the optional check was not read." The report knows this elsewhere (L486 "CAS behaviour" is a main unknown; L520 makes P4 a dependency), but L491 states the guarantee flatly, and the item is missing from section 7.
Fix: "... and races cannot overwrite each other, provided the Hub enforces `parent_commit` on the server, which is not confirmed (section 7; prototype P4)." Add the item to section 7 (see section 5 above).

**P6. L58 (section 2.1, prime-diloco row); same pattern at L152 (Q3 table).**
Text: "| **prime-diloco** (INTELLECT-1) | ... | Not met as run: Tailscale VPN (w1c S5, P) | ..."
Why: The row label states the identity "prime-diloco is INTELLECT-1's framework", which w1d lists as unverified (rests on description and checkpoint code; section 7 L637), and the R3 cell uses the INTELLECT-1 run's VPN as evidence about prime-diloco. The caveat appears only at L347. L152 likewise fills the prime-diloco row with the paper's "not described". Low weight: the identity is well supported.
Fix: label "prime-diloco (INTELLECT-1's framework by its own description; section 7)"; at L152 add "(INTELLECT-1 paper)" to the "not described" cell.

---

## 8. Counts

Compiled items: 136 (w1a 13, w1b 23, w1c 24, w1d 20, w2a 18, w2b 17, w2c 21). Items with any use in scope: 71 (69 with their own rows, plus w2a-04 and w2b-08, which share the rows of w1a-04 at L328 and w1b-07 at L275); with none: 65 (counted by script).

Classified (item, line) hits in scope: 139, counted from the table in section 3 by script.

| Class | Hits |
|---|---|
| OK-pointer | 26 |
| OK-verified-elsewhere | 18 |
| OK-abstract-only | 1 |
| OK-search-finding | 7 |
| OK-verified-part (extra) | 65 |
| OK-figure-only (extra) | 7 |
| UNKNOWN-missing-from-7 (extra) | 4 |
| NOTE (extra) | 2 |
| **PROBLEM** | **9 hits on 9 lines (26, 58, 152, 227, 253, 275, 448, 491, 525), grouped as P1 to P6** |

Items used in scope but missing from section 7: 5 (section 5). Section 7 over-lists 2 items that sections 1 to 6 use through a later strand (section 2). Converse check: 0 sources without a recorded reading (100 distinct notes blocks cited). Class (c): 0 silent reliances; 3 observations.

Status: COMPLETE.
