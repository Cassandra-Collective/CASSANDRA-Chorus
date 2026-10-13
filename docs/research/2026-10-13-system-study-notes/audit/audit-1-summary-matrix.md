# Audit 1: header, Section 1 (Summary), Section 2 (Requirements matrix)

Scope: lines 1 to 82 of `audit/report_preaudit.md` (frozen copy of `docs/research/2026-10-13-system-study-report.md`). Auditor 1, 2026-10-13. Report, notes and repository not modified.

Method: each source-attributed claim traced to the notes at the cited tag, then to the raw source under `sysstudy/sources/` (paper text by `grep -F`; docs in the fetched page; code at the recorded commit, clone HEADs checked with `git rev-parse HEAD`; API values in `sources/w2a/api/*/repo.json`, `release_latest.json`, `commits.json` with `_querylog.txt` times). One re-query: `gh api repos/one-covenant/templar/commits/142666f0dd91` (2026-10-13), which confirmed the dormant-notice diff and date. FoMoE raw text was found in the Stage 0 scratchpad (`scratchpad/papers/q4a/2606.19025/paper.txt`, `paper_html.txt`); nothing had to be re-fetched. Derived numbers recomputed with Python 3.12 `-I`.

## Counts by class

| Class | Header and §1 (24 items) | §2.1 (80 cells) | §2.2 (80 cells) | §2.3 (2) | Total |
|---|---|---|---|---|---|
| OK-raw | 12 | 40 | 18 | 2 | 72 |
| OK-inference | 3 | 0 | 0 | 0 | 3 |
| OK-judgment | 4 | 39 | 61 | 0 | 104 |
| PROBLEM | 5 | 1 | 1 | 0 | 7 |
| Total | 24 | 80 | 80 | 2 | 186 |

Counting rule: each attributed sentence-level claim in the header and Section 1 counts once; each of the 160 matrix cells in 2.1 and 2.2 counts once (cells with a source quote, number or code fact are OK-raw when confirmed in the raw source; ratings resting on the cited mechanism, including "Not addressed", are OK-judgment); 2.3 counts two claims. Rows grouped in the tables below ("R2 to R7, central") are counted cell by cell. Items in the PROBLEM list are not counted again as OK.

## PROBLEM list

**P1. L20** "Every system read keeps one function central: **an agreed record of which updates count in a round**. ... BOINC and Flower keep it in a server's database (w1c Q3d; w2c part 1)."
- What is wrong: cell/claim unsupported by the cited evidence. w2c Part 1 summary says "flwr-serverless's asynchronous mode drops agreement altogether", and w2c Part 2 pattern 4 says the counted set is fixed by "nobody (T2's asynchronous mode, where each node merges what it sees)". Gossip methods (w1b F1) and RL Swarm (w1c S9, no shared model) also keep no such record, and the report's own matrix rates flwr-serverless R1 "Met: no server". Secondary: w2c says BOINC keeps it in its database and Flower in its SuperLink (PostgreSQL only in the HA preview, F1), not "a server's database" for both.
- Fix: "Every system read that keeps one shared model keeps one function central: an agreed record of which updates count in a round. Psyche puts it on a ledger, Templar splits it between a ledger clock and one validator's list, HF²L gives it to the owner, BOINC keeps it in its server database and Flower in its SuperLink (w1c Q3d; w2c part 1). flwr-serverless's asynchronous mode has no such record, so peers can merge different sets (w2c T2)."

**P2. L24** "Every method read that applies stale updates keeps the global model on one central holder".
- What is wrong: wrong scope relative to the source. w1b F1 says type-2 (stale-update) methods hold global state on one party "except the overlap methods S13 and S14, which keep an all-reduce and bound the delay", and lists DeDLOC's and SWARM's one-round delayed updates as stale with no server. The summary dropped the word "asynchronous" that w1b F2's conclusion uses. The report's own L70 rates the one-round-delayed merges R1 "Met: all-reduce, no server".
- Fix: "Every asynchronous method read that applies stale updates keeps the global model on one central holder; only the one-round overlap methods avoid one, by keeping a synchronous all-reduce (w1b F1, F2)."

**P3. L24** "gossip ... costs about 1% to 4% against DiLoCo at 8 to 32 workers (w1b F3)".
- What is wrong: wrong value and derived but unlabelled. The papers give perplexities (S9) and losses (S10); the percentages are the researcher's ratios (S9 in log-PPL, S10 in loss, two conventions). Recomputed from the raw tables: S9 Table 1 LocalM1M2 against DiLoCo +1.29% (M = 8; 19.37 vs 18.65) and +3.56% (M = 16; 22.24 vs 19.99); S10 Table 1(b) 134M 2-Peer +0.61 / +1.47 / +2.55%, 1-Peer +1.21 / +2.65 / +3.68% at 8 / 16 / 32; S10 Table 3 551M 2-Peer 0.0 / +1.87%, 1-Peer +1.14 / **+5.24%** (2.81 vs 2.67) at 8 / 16. Range 0.0% to 5.24%. Raw: `sources/w1b/2606.11081/c.txt` Tables 1(b), 3; `sources/w1b/2606.22768/c.txt` lines 191 to 192, 204 to 205. The notes' F3 summary sentence carries the same understatement.
- Fix: "costs 0% to about 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in S10, log-perplexity ratios in S9; w1b S9, S10, F3)".

**P4. L25** "Exchange through file hosts ... has four precedents, none measured on home connections (w2c part 2)".
- What is wrong: count does not match the cited source. w2c part 2's table of "Systems and papers found that exchange training updates only through storage" has five rows: Templar, Hivetrain, flwr-serverless, HF²L and LambdaML (T3, S3 in one cloud region). The report's section 3 table silently drops LambdaML.
- Fix: "has five precedents (Templar, Hivetrain, flwr-serverless and HF²L, plus LambdaML inside one cloud region), none measured on home connections (w2c part 2)", or keep "four" and add "outside a single cloud region".

**P5. L38** "they rest on full reads of the named systems, not an exhaustive search."
- What is wrong: read status overstated. The notes record section-level reads (P) for the stale-update papers (w1b S1, S2, S11, S12 each list unread sections) and file-level or line-range code reads (C) for go-libp2p, rust-libp2p, iroh, Hivemind (w1a S4, S5, S7, S9). The matrix itself marks these P and C. Only a few sources are F.
- Fix: "they rest on the sections and code paths of the named systems listed as read in the notes, not on full reads or an exhaustive search."

**P6. L52** Petals, R1: "Not met as documented: always-on bootstrap machines (w1a S8, D)".
- What is wrong: cell unsupported by the cited evidence. The wiki (`petals-wiki/launch-own-swarm.md`, Step 2) calls always-on CPU bootstrap machines "a good practice" for unreliable GPU machines and says "If you have reliable GPU machines, you can skip this step"; Step 3 gives `--new_swarm` without bootstrap peers; joins need only "at least one of their initial peers" alive. That is the same condition the report rates "Partly" for Hivemind (L51).
- Fix: "Partly: the wiki recommends always-on bootstrap machines when servers are unreliable but lets them be skipped; a join needs one listed initial peer alive (w1a S8, D)".

**P7. L71** FoMoE, R1: Not met as published: "central coordinator, synchronous rounds" (w1b S17, via notes 04a, 06; F).
- What is wrong: a paraphrase shown as a quotation. Stage 0 note 04a (line 218) writes the phrase without quotation marks; the paper (v2, `papers/q4a/2606.19025/paper_html.txt` line 219; `paper.txt` line 226) says "We employ a central coordinator to manage initialization, broadcasting, and aggregation, restricting our study to synchronous training". The substance is right.
- Fix: Not met as published: a "central coordinator to manage initialization, broadcasting, and aggregation", synchronous rounds only (FoMoE §3.1; w1b S17, via note 04a; F).

## OK checks

Abbreviation: `src/` = `scratchpad/sysstudy/sources/`. "Notes" names the notes block where the claim was found.

### Header and Section 1

| Line | Claim | Source (notes) | Class | Where confirmed |
|---|---|---|---|---|
| 8 | Wave 1 17:18 to 17:50; wave 2 17:53 to about 18:45; w2c resumed 22:00 to 22:12 | notes headers and query logs | OK-raw | w1a/w1d first log entries 17:18; w1d "finished 17:50"; w2b log 17:53, status ≈18:45; w2c log 17:53:47, resumed 22:00, T9 fetched 22:11 to 22:12 (header says completed 22:10) |
| 8 | Method: pdftotext or arXiv HTML; raw docs; shallow clones never run | method lines of all seven notes | OK-raw | each notes header; clone HEADs match recorded commits |
| 20 | Psyche puts the counted set on a ledger (witness records on chain) | w1c S1, Q3d | OK-raw | `src/w1c/code/psy/repo` `explain/index.md` lines 5, 11; `coordinator.rs` 596 to 601 |
| 20 | Templar: chain clock plus one validator's list | w1c S2, Q3d; w2c T1 | OK-raw | `src/w1c/code/tpl/repo/src/tplr/comms.py` 2235, 2240 (`metagraph.S.argmax()`), 2340; notes say 2239 (one-line offset, notes only) |
| 20 | HF²L gives it to the owner | w2c T8 | OK-raw | `src/w2c/hffl/README.md` lines 23, 204, 483 (owner aggregates, participants open PRs) |
| 20 | Owner-signed config plus conditional commit log could carry it; no source tests it | w1c S15, Q3d | OK-inference (labelled) | `src/w1c/docs/hfhubpy/hf_api.py` 5033 to 5039: "the commit will fail if `revision` does not point to `parent_commit`" |
| 24 | No source tests a rotating synchronizer | w1b F2, gaps | OK-raw (negative finding as recorded) | w1b F2 last paragraph; gaps item 1 |
| 24 | Server-free methods are group all-reduce (Moshpit, DeDLOC, SWARM) and gossip | w1b F2 | OK-judgment | w1b F2 table |
| 24 | Asynchronous branch closed under R1, group branch open | w1b F1, F2 | OK-judgment | follows from F2 |
| 25 | Direct connections need one of our machines reachable | w1a Q2 | OK-judgment | w1a Q2 "If none of our machines is reachable"; port mapping counts as reachable |
| 25 | File-host exchange needs only outbound connections | w1a Q2 | OK-inference (labelled) | w1a Q2 inference bullets |
| 25 | None measured on home connections | w2c part 2, gap 1 | OK-raw | w2c Part 2 last paragraph; Gaps 1 |
| 26 | Hivemind, Petals, Psyche, prime-diloco, Templar dormant or barely maintained | w2a 1, 2, 8, 9, 11 | OK-raw | `src/w2a/api/*/commits.json`, `release_latest.json`: Hivemind last commit 2026-01-04; Petals 2024-08-25; Psyche 2026-03-20; prime-diloco 2025-04-10; Templar README "Templar is dormant" (`src/w2a/raw/one-covenant_templar/README.md` 22 to 24); queries 17:55 to 18:00 TST |
| 26 | None documents native Windows support | w2a 1, 2, 8, 9, 11 | OK-raw | Hivemind README 82 to 90 (WSL, experimental); Petals README 56 (WSL); Psyche `join-run.md` 11 (Linux only); prime-diloco and Templar README no Windows mention; Templar `ci.yml` ubuntu only |
| 26 | go-libp2p and iroh released within the last month | w2a 3, 7 | OK-raw (date comparison) | v0.50.0 2026-09-21T14:17:28Z, v1.3.0 2026-09-28T19:26:13Z (`release_latest.json`); 22 and 15 days before 2026-10-13 (recomputed) |
| 26 | go-libp2p and iroh test on Windows | w2a 3, 7 | OK-raw | `go-test-template.yml` 21 to 28 (`os: ["ubuntu","macos","windows"]`); iroh `tests.yaml` 220 to 246 (`build_and_test_windows`, target `x86_64-pc-windows-msvc`) and 330 to 360 (`cargo nextest run`) |
| 34 | Churn can leave 1 or 0 holders; no volunteer system read prevents it without operator machines | w2b F5 | OK-judgment | w2b F5 inference bullet; Agora floor `src/w2b/p/2607.13332v1.txt` / `src/w1c/2607.13332/paper.txt` 1841 to 1843 |
| 34 | Publishing the merged model each round caps loss at one round | none | OK-inference (labelled) | own reasoning, labelled |
| 38 | No source measures home links, groups of 3 to 5, holders 2 to 1, file-host exchange of 0.2 to 0.6 GB | w1b gaps; w2b F6; w2c gap 1 | OK-raw (negative findings as recorded) | w1b Gaps items 4 and 6; w2b F6 last bullet; w2c Gaps 1 |

### 2.1 Systems and building blocks (8 cells per row)

| Line | Row: cells | Source | Class | Where confirmed |
|---|---|---|---|---|
| 51 | Hivemind R1 (initial peer must be up) | w1a S7 | OK-raw | `src/w1a/hivemind/repo/hivemind/dht/node.py` 241 "DHTNode bootstrap failed" |
| 51 | Hivemind R2 (DHT not persisted by design) | w1a S7 | OK-raw | `node.py` 50 to 52 "persistence on shutdown" |
| 51 | Hivemind R3 (4 GiB, 30 min; all-NAT uses IPFS) | w1a S7 | OK-raw | `src/w1a/hm-p2pd/repo/p2pd/main.go` 94 to 100 (`1<<32`, `30*time.Minute`); `docs/user/dht.md` 129 to 130 |
| 51 | Hivemind R4 (group all-reduce, timeouts, local fallback) | w2b B1 | OK-raw | `src/w2b/c/hm/hivemind/optim/optimizer.py` 634 "Proceeding with local gradients"; `matchmaking.py` 296 |
| 51 | Hivemind R5 (`min_group_size` 2; MoE 1 holder) | w2b B1 | OK-raw | `averager.py` 119; `moe/server/dht_handler.py` 69 to 70 |
| 51 | Hivemind R6 (DeDLOC, OpenDiLoCo full copies) | w2a 1 | OK-raw | `src/w2a/raw/PrimeIntellect-ai_OpenDiloco/README.md` 76 |
| 51 | Hivemind R7 (owner-signed expiring records) | w1c S12 | OK-raw | `src/w1c/docs/hivemind/crypto.py` 13 to 18, 46 to 47; `validation.py` 7 to 11 |
| 51 | Hivemind central (initial peers, `use_ipfs`, PyPI/GitHub) | w2a 1 | OK-raw | `p2p_daemon.py` 101, 131; `src/w2a/pkg/pypi_hivemind.json` |
| 52 | Petals R2, R3 | w1a S8 | OK-judgment | wiki Step 2; `server.py` relays |
| 52 | Petals R4 (servers do not update weights) | w2b B5 | OK-raw | `src/w2b/p/2312.08361v1.txt` 430 to 431 |
| 52 | Petals R5 (sole holder never leaves) | w2b B5 | OK-raw | `src/w2b/c/pt/src/petals/server/block_selection.py` 59 to 60 |
| 52 | Petals R6, R7 | B5 | OK-judgment | not a training system |
| 52 | Petals central (bootstrap, health API, Hub) | w1a S8; w2a 2 | OK-raw | `constants.py` 3 to 7, 14 (`health.petals.dev`) |
| 53 | Agora R1, R7 (Authorizer singleton; short-lived credentials; operator checkpoints) | w1c S11 | OK-raw | `src/w1c/2607.13332/paper.txt` 336, 1369, 464 |
| 53 | Agora R2, R6 | w1c S11 | OK-judgment | |
| 53 | Agora R3 (public inbound port) | w2a 13 | OK-raw | `src/w1c/code/n0/repo/README.md` 72 |
| 53 | Agora R4 (async partial averaging) | w2b B11 | OK-raw | `src/w2b/p/2607.13332v1.txt` 294 "5% of weights · async · every 20 steps" |
| 53 | Agora R5 (operator floor 4 to 16) | w2b B11 §5.1 | OK-raw | paper lines 1841 to 1843 (8 per stage, then head 8, tail 16, body 4) |
| 53 | Agora central | w1c S11 | OK-judgment | |
| 54 | libp2p R1 (every role a peer role) | w1a S3, S4 | OK-judgment | notes Fit lines |
| 54 | libp2p R2 (go DHT does not persist table) | w1a S4 | OK-raw | `src/w1a/go-libp2p-kad-dht/repo/dht.go` 529 to 532 (TODO, snapshots) |
| 54 | libp2p R3 (2 min, 128 KiB defaults) | w1a S4, S5 | OK-raw | `resources.go` 62 to 68; rust `behaviour.rs` 162 to 163 |
| 54 | libp2p R4 to R7 | | OK-judgment | transport only |
| 54 | libp2p central (default IPFS list) | w1a S4 | OK-raw | `dht_bootstrap.go` 12 to 13 |
| 55 | iroh R1, R2 (`Builder::empty()`, `MemoryLookup`) | w1a S9 | OK-raw | `endpoint.rs` 192 to 193, 2000 to 2011; `address_lookup.rs` 35 |
| 55 | iroh R3 (relays carry all traffic) | w1a S9 | OK-raw | `src/w1a/iroh-docs/concepts_relays.md` 13 |
| 55 | iroh R4 to R7 | | OK-judgment | |
| 55 | iroh central (n0 relays, DNS) | w1a S9 | OK-raw | `defaults.rs` 27 to 33 |
| 56 | Psyche R1 (Solana; TCP dev tool) | w1c S1 | OK-raw | `explain/index.md` 5, 11 |
| 56 | Psyche R2, R4 | w1c S1 | OK-judgment | |
| 56 | Psyche R3 (relays can be disabled; defaults psyche relays, n0 discovery) | w1a S15 | OK-raw | `git show HEAD:shared/client/src/cli.rs` 66 to 72; `network/src/lib.rs` 135 to 142 |
| 56 | Psyche R5 (one trainer per batch) | w2b B7 | OK-judgment | B7 `data_selection.rs` citation |
| 56 | Psyche R6 | w2a 8 | OK-judgment | |
| 56 | Psyche R7 (any epoch member can repoint checkpoint) | w1c S1 | OK-raw | `instance_state.rs` 397 to 414; `coordinator.rs` 598 to 600 |
| 56 | Psyche central (incl. RPC providers) | w2a 8 | OK-raw | `src/w2a/raw/PsycheFoundation_nousnet/psyche-book__src__enduser__join-run.md` 101 |
| 57 | Templar R1 (one leader validator) | w1c S2 | OK-raw | `comms.py` 2240 |
| 57 | Templar R2, R4, R5, R6 | w1c S2; w2c T1 | OK-judgment | |
| 57 | Templar R3 (no peer connections) | w1c S2; w1d P4 | OK-raw | `src/w1c/2603.08163/paper.txt` 191 "avoids requiring direct peer-to-peer connectivity" |
| 57 | Templar R7 (bucket per participant, read keys on chain) | w1c S2 | OK-raw | `chain.py` 140 to 146 |
| 57 | Templar central, dormant notice added 2026-03-31 (commit `142666f0dd91`) | w2a 11 | OK-raw | `src/w2a/api/one-covenant_templar/commits.json` (date 2026-03-31T02:52:32Z, "Update readme"); re-query of the commit diff 2026-10-13 shows the notice lines added |
| 58 | prime-diloco R1 (rank-0 store) | w1c S5 | OK-raw | `src/w1c/code/pdl/repo/src/zeroband/comms.py` 95 to 100, 247 |
| 58 | prime-diloco R2 (fsspec remote checkpoints) | w1d S3 | OK-raw | `src/w1d/prime-diloco/checkpoint.py` 10 to 11 |
| 58 | prime-diloco R3 (Tailscale) | w1c S5 | OK-raw | `src/w1c/2412.01152/paper.txt` 408 |
| 58 | prime-diloco R4 to R7, central | w2a 9; w1c S5 | OK-judgment | |
| 59 | PCCL R1 ("Master Crash = End of Run") | w2b B8 | OK-raw | `src/w2b/c/pc/docs/md/05-ImplementationNotes/03_MasterOrchestration.md` 8 |
| 59 | PCCL R3 (open ports, no relays) | w2b B8 | OK-raw | same file 65 to 71 |
| 59 | PCCL R7 (bit-identical, hash) | w1c S7 | OK-raw | `src/w1c/2505.14065/paper.txt` 209, 264 |
| 59 | PCCL R2, R4, R5, R6, central | w2a 10 | OK-judgment | |
| 60 | RL Swarm R1, R7 (stage manager; registry) | w1c S9 | OK-raw | `src/w1c/code/rlc/repo/src/SwarmCoordinator.sol` 273 (`onlyStageManager`) |
| 60 | RL Swarm R4 (each node its own model) | w1c S9 | OK-raw | `src/w1c/2509.08721/paper.txt` 18 |
| 60 | RL Swarm R2, R3, R5, R6, central | w1c S9 | OK-judgment | |

### 2.2 Algorithms and storage-only approaches (8 cells per row)

| Line | Row: cells | Source | Class | Where confirmed |
|---|---|---|---|---|
| 66 | Moshpit/DeDLOC R1 ("available at all times") | w1b S4 | OK-raw | `src/w1b/2106.10207/paper.txt` 367 |
| 66 | R2 (first peer pushed to Hub) | w2b B4 | OK-raw | `src/w2b/c/dd/sahajbert/run_first_peer.py` 52 to 55, 124, 148 |
| 66 | R3 (public participants as STUN/relays) | w1b S4 | OK-raw | paper.txt 1446 "no dedicated STUN and TURN servers" |
| 66 | R4 (groupmates skip a round) | w1b S3 | OK-raw | `src/w1b/2103.03239/paper.txt` 290 |
| 66 | R5 (full replicas) | w2b B3 | OK-judgment | |
| 66 | R6 | w1b S3 | OK-judgment | |
| 66 | R7 (allowlist authorization server) | w1d P10 | OK-raw | `src/w1d/2106.10207/paper.txt` 1789 to 1793 |
| 66 | central | w1b S4; w1d P10 | OK-judgment | |
| 67 | SWARM R1, R4 | w1b S5 | OK-judgment | |
| 67 | SWARM R5 (survives with one per stage) | w2b B6 | OK-raw | `src/w2b/p/2301.11913v2.raw.txt` 963 to 964 |
| 67 | SWARM R2, R3, R6, R7, central | | OK-judgment | |
| 68 | Stale-update R1 (server or syncer) | w1b F2, S1, S2 | OK-judgment | notes record §3, §4 quotes |
| 68 | R6 (Decoupled DiLoCo MoE holds every expert) | w1b S1 | OK-judgment | notes Fit |
| 68 | R2 to R5, R7, central | | OK-judgment | |
| 69 | Gossip R1, R4 | w1b F1, F2 | OK-judgment | |
| 69 | Gossip central (NoLoCo fixed world) | w2b B10 | OK-raw | `src/w2b/c/nl/src/noloco/train.py` 81 to 85 |
| 69 | R2, R3, R5, R6, R7 | | OK-judgment | |
| 70 | One-round-delayed R1 (all-reduce, no server) | w1b S13, S14 | OK-judgment | notes quote §3 "without any central parameter server" |
| 70 | R2 to R7, central | | OK-judgment | |
| 71 | FoMoE R4 (synchronous) | w1b S17 | OK-raw | `scratchpad/papers/q4a/2606.19025/paper_html.txt` 219, 462 |
| 71 | FoMoE R5, R6 (O_e holders; within replica groups) | w1b S17; 04a | OK-judgment | 04a block 2 |
| 71 | FoMoE R2, R3, R7, central | | OK-judgment | |
| 72 | flwr-serverless R1, R3 | w2c T2 | OK-judgment | |
| 72 | R4 (sync waits forever) | w2c T2 | OK-raw | `src/w2c/fs/flwr_serverless/federated_node/sync_federated_node.py` 166 to 184 |
| 72 | R7 (one folder, one credential set) | w2c T2 | OK-raw | `shared_folder/s3_folder.py` 28 (`boto3.client("s3")`, default credentials; inside the recorded read range 1 to 135) |
| 72 | R2, R5, R6, central | | OK-judgment | |
| 73 | HF²L R1, R7 (owner listener; PRs) | w2c T8 | OK-raw | `src/w2c/hffl/README.md` 204, 483 |
| 73 | HF²L R4 (synchronous FedAvg only) | w2c T8 | OK-raw | README 23 |
| 73 | R2, R3, R5, R6, central | | OK-judgment | |
| 74 | Hivetrain R1 (central averager) | w2c T7 | OK-raw | `src/w2c/dt/README.md` 14 |
| 74 | R7 (history squashed after push) | w2c T7 | OK-raw | `hivetrain/hf_manager.py` 107, 128 |
| 74 | R2 to R6, central | | OK-judgment | |
| 75 | Plain storage R1 (tracker or DHT; IPFS always-on node or paid pinning) | w1d H9, H11 | OK-raw | `src/w1d/ipfs-docs/persistence.md` 37 ("for a fee"; free allowance "for new users"); `work-with-pinning-services.md` 19; `src/w1d/beps/` |
| 75 | R2 (Hub, GitHub, BitTorrent named in R2) | brief | OK-raw | brief line 48 |
| 75 | R7 (host roles and tokens) | w1c S13, S14 | OK-raw | `src/w1c/docs/hfhub/organizations-security.md` 17, 19 |
| 75 | R3 to R6, central | | OK-judgment | |

### 2.3 Contrast cases

| Line | Claim | Source | Class | Where confirmed |
|---|---|---|---|---|
| 79 | BOINC server must have "a static IP address" | w2c B1 | OK-raw | `src/w2c/bw/ServerIntro.md` 15 at `7e16379` |
| 79 | Flower SuperLink "a long-running process", clients over HTTP | w2c F1 | OK-raw | `src/w2c/fl/framework/docs/source/explanation-flower-architecture.rst` 43 at `47c6a82` |

## Notes for the other auditors (outside scope, seen in passing)

- w1c S2 cites `comms.py` line 2239 for `metagraph.S.argmax()`; it is line 2240 at `0fefc2a`. Notes-level only.
- L58 R1 "master key-value store on rank 0": the "rank 0" fact rests on prime-diloco `comms.py` line 247 (`_global_leader = global_rank == 0`), which is outside w1c S5's explicit ranges (86 to 107, 336 to 360) and covered only by "plus a function index". Value confirmed; counted OK-raw here, but the notes should list line 247 as read.
- Read-range containment was checked for every OK-raw locator in this file against the notes' read-status lines; all others sit inside the recorded ranges.
- The w1b F3 summary sentence "about 1% to 4%" is also the likely source of any repetition of that range later in the report.
