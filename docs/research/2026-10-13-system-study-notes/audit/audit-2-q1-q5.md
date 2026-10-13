# Audit 2: report lines 83 to 262 (Q1 to Q5)

Status: COMPLETE (2026-10-13, about 23:15 TST). Report audited: `report_preaudit.md` (frozen copy), lines 83 to 262, "## 3. Findings by question" through Q5. Evidence: notes w1a, w1b, w1c, w1d, w2a, w2b, w2c; Stage 0 notes 01, 04a, 04b, 06; raw sources under `sysstudy/sources/`.

Re-fetched for this audit (raw, into new empty directories under `sysstudy/audit_sources/a2/`; nothing run): FoMoE arXiv 2606.19025 v2 (PDF and HTML; the PDF's Table 6 is garbled by pdftotext, the HTML table was parsed with a local `-I` script); Scaling Laws for DiLoCo arXiv 2503.09799 v1 (PDF). Local `-I` scripts: `audit/scripts_a2/q4calc.py` (recomputes every Q4 percentage), `oapi_uploaded.py`, `tab6.py`.

## Counts by class

| Class | Count |
|---|---|
| OK-raw | 104 |
| OK-inference | 24 |
| PROBLEM | 11 (minor to moderate; none changes a conclusion of the report) |

Counting rule: one row of the OK table below is one check (some rows bundle several numbers from the same locator; every number in a bundled row was confirmed).

## PROBLEM list

**P1. Line 92 (Q1, private DHTs).** Text: `In go-libp2p, pnet runs over TCP only: "QUIC doesn't support private networks yet"`.
- Wrong / derived but unlabelled. The raw code at `3c2c902` shows QUIC (`quic/transport.go` 74-76), WebTransport (`webtransport/transport.go` 98-100) and WebRTC (`webrtc/transport.go` 137-139) refusing a PSK; TCP and WebSocket do not. "TCP only" is a conclusion, and w1a S4 itself labels it "(inference)" and says "TCP (and WebSocket)".
- Fix: `In go-libp2p the QUIC and WebTransport transports refuse a pre-shared key ("QUIC doesn't support private networks yet", p2p/transport/quic/transport.go lines 74 to 76), so a pnet pool runs over TCP or WebSocket (inference).`

**P2. Line 113 (Q2 table, Trautwein row, Setting).** Text: `volunteer clients mostly in the US`.
- Overstated. The paper (§4.3, paper.txt 305-306) says "the sample distibution is skewed toward the U.S." and that clients were in 39 countries; no majority share is stated.
- Fix: `volunteer clients in 39 countries, sample "skewed toward the U.S." (§4.3)`.

**P3. Line 113 (same row, Caveats).** Text: `the authors say the rate "from scratch is lower"`.
- Misquotation. The paper (§6 "Limitations", paper.txt 666-667) reads "The unconditional end-to-end connectivity metric for establishing a direct connection from scratch is necessarily lower". The quoted string is not contiguous in the source (w1a S1 carries the same trimmed quote).
- Fix: `the authors say the unconditional rate "from scratch is necessarily lower" (§6)`.

**P4. Line 121 (Q2, iroh relays).** Text: `a Windows relay binary is published (w2a 7, A)`.
- Missing date on a maintenance/availability claim. Confirmed in `sources/w2a/api/n0-computer_iroh/release_latest.json` (`iroh-relay-v1.3.0-x86_64-pc-windows-msvc.zip`); w2a 7 records the query at 2026-10-13 18:21:14 TST.
- Fix: `a Windows relay binary is published with release v1.3.0 (w2a 7, A; GitHub API, queried 2026-10-13 18:21 TST)`.

**P5. Line 133 (Q2, STUNMESH-go).** Text: `it refreshes every minute and needs at least one cone NAT`.
- Overstated. README (stunmesh-go `74a0d38`, lines 17 to 22): symmetric NAT "may be difficult to support"; "For best results, ensure at least one peer is behind a cone NAT type" (advice, not a stated requirement). The 1-minute refresh is `refresh_interval: "1m"` in the README's example configuration (lines 81 to 103); no default is stated in the files read.
- Fix: `its example configuration refreshes every minute, and it advises that at least one peer be behind a cone NAT ("For best results")`.

**P6. Line 157 (Q3).** Text: `a client that lacks an agreed payload stops with an error and must rejoin the next epoch (w1c Q3b; w2b B7, C)`.
- Derived but unlabelled. The code shows the error (`train.rs` 616, 623, 630 return `ApplyError`; `client.rs` 213 propagates it with `?`). "Must rejoin the next epoch" is w2b B7's labelled "(inference)".
- Fix: `... stops with an error (w1c Q3b; w2b B7, C) and would have to rejoin at the next epoch (inference, w2b B7)`.

**P7. Line 172 (Q3, Plexus).** Text: `assumes a fully connected overlay and "all nodes remain online" (arXiv 2503.05509 §3.1, §5; w2c F3, P)`.
- Wrong locator. §5 of the paper is "Related Work"; the sentence "we currently assume all nodes remain online during training" is in §6 "Broader Impact and Open Challenges", Open Challenges paragraph (paper.txt 453, heading at 475). w2c F3 carries the same wrong section number. The quote itself is correct; §3.1 for the overlay is correct (paper.txt 106, 137).
- Fix: `(arXiv 2503.05509 §3.1, §6; w2c F3, P)`.

**P8. Line 177 (Q3, candidate 3).** Text: `On the Hub, only Storage Buckets list a per-file uploadedAt`.
- Outside what was read (minor). w2c T9 parsed the OpenAPI spec only for model-repository and Storage Bucket `tree`/`paths-info` endpoints. A full parse of the same file (`sources/w2c/hubapi/openapi.json`) shows `uploadedAt` also under `/api/containers/{namespace}/{repo}/tree/{path}`, `.../paths-info` and `/containers/.../resolve/{path}`. The spec's `containers` tag describes these as "Container image repositories ... Backed by bucket storage: the file endpoints mirror the bucket ones", i.e. a distinct repo type on bucket storage. No model, dataset or Space endpoint lists `uploadedAt`. So the substance (only bucket-backed storage carries it) holds, but "only Storage Buckets" over the whole Hub was not established by the read.
- Fix: `Of the Hub API endpoints read (model repositories and Storage Buckets), only Storage Buckets list a per-file uploadedAt; whether the server assigns it is not confirmed (see section 7).`

**P9. Lines 209 and 227 (Q4, HALoS).** Text: `+18.6% / +24.8% / +30.9% more tokens than DiLoCo to the same loss` and `HALoS's 19% to 31% token cost`.
- Derived but unlabelled. The table header (line 203) labels only "gaps in loss or log-perplexity" as w1b's arithmetic; these are token ratios (HALoS Table 1: 14.0B/11.8B, 16.1B/12.9B, 16.1B/12.3B, recomputed: +18.6 / +24.8 / +30.9%). Line 227 carries no label.
- Fix: line 209: `+18.6% / +24.8% / +30.9% more tokens than DiLoCo to the same loss (inference: 14.0B/11.8B, 16.1B/12.9B, 16.1B/12.3B; ...)`; line 227: `... against HALoS's 19% to 31% token cost (inference, from its Table 1) ...`; or widen line 203 to "gaps in loss, log-perplexity or tokens are w1b's arithmetic, inference".

**P10 (minor). Line 211 (Q4, HeLoCo row, Setting).** Text: `15M, 5 workers, far from converged`.
- Inference shown as a sourced setting. w1b S11 labels it "(inference)" from losses near 6.5 nats; the paper says only that the setting "does not yet capture the scale of practical low-communication LLM training" (§5).
- Fix: `15M, 5 workers, far from converged (inference: losses near 6.5)`.

**P11. Line 213 (Q4, Streaming DiLoCo overlap row, Setting).** Text: `Streaming DiLoCo overlap (arXiv 2501.18512 §3.3.2) | 35M to 4B | under 0.2% up to an overlap of 10 inner steps`.
- Wrong value / misattributed setting. 35M to 4B is the paper's scaling range; its ablations, including §3.3.2's overlap result, use one model: "we perform all our ablations on a model of size 500 million parameters" (§3.3, paper.txt 502-503). The "< 0.2%" quote is correct (paper.txt 560-561).
- Fix: `Streaming DiLoCo overlap (arXiv 2501.18512 §3.3.2) | 500M (the paper's ablation model, §3.3) | under 0.2% up to an overlap of 10 inner steps`.

## OK checks

| Line | Claim | Source | Class | Where confirmed |
|---|---|---|---|---|
| 89 | Hivemind raises "DHTNode bootstrap failed" when no initial peer answers a ping (default `ensure_bootstrap_success=True`), node.py 219-245 at 4bd43b7 | w1a S7 | OK-raw | node.py 124, 219-245; read range 40-250 |
| 89 | kad-dht dials bootstrap list until 2 succeed; retries every 2 min; dht.go 497-560 | w1a S4 | OK-raw | dht.go 497-560; dht_bootstrap.go 18-21 (`maxNBoostrappers`=2, `periodicBootstrapInterval`=2 min) |
| 89 | rust-libp2p `bootstrap()` returns `NoKnownPeers` | w1a S5 | OK-raw | kad/src/behaviour.rs 984-996 at a035aad |
| 89 | Petals: join "as long as at least one of their initial peers is alive" | w1a S8 | OK-raw | petals-wiki launch-own-swarm.md 40 |
| 90 | Hivemind "any computers with a public IP address that are always online" | w1a S7 | OK-raw | docs/user/dht.md 83-84 |
| 90 | Petals "a few CPU-only machines that are always online" | w1a S8 | OK-raw | launch-own-swarm.md 24 |
| 91 | kad-dht no reuse of previous routing table, TODO cites #387; datastore in memory | w1a S4 | OK-raw | dht.go fixLowPeers TODO; internal/config/config.go 140 |
| 91 | Hivemind DHT "temporary metadata", not persisted | w1a S7 | OK-raw | node.py 47-50 |
| 91 | BEP 5 "should be saved between invocations"; `nodes` key in torrent file | w1a S10 | OK-raw | bep_0005.txt 160, 169, 185-187 |
| 92 | ProtocolPrefix gives separate protocol; pnet refuses nodes without key | w1a S3, S4 | OK-raw | dht_options.go 170-178; pnet spec line 41 |
| 92 | Quote "QUIC doesn't support private networks yet", quic/transport.go 74-76 | w1a S4 | OK-raw | quic/transport.go 74-76 (the "TCP only" conclusion is P1) |
| 92 | Hivemind new DHT without initial peers; iroh no DHT by default, `MemoryLookup` | w1a S7, S9 | OK-raw | node.py 134, 219; iroh address_lookup.rs module docs |
| 93 | NATed laptops client mode; only server-mode nodes added; impls decide, forceable | w1a S3-S5 | OK-raw | kad-dht/README.md 78-82, 95-96; dht_options.go 26-36; rust behaviour.rs 1118-1123, 1168-1180 |
| 94 | mDNS local only; rendezvous point | w1a S11 | OK-raw | discovery/mdns.md 49; rendezvous/README.md 44 |
| 95 | Public networks incl. HyperDHT public bootstrap nodes | w1a S9, S10; w2c N3 | OK-raw | hyperdht lib/constants.js 17-20; README 84 |
| 99 | k = 20 or K = 8 exceed N; DHT degenerates | w1a inference | OK-inference | labelled block; k=20 kad spec 47; K=8 BEP 5 line 123 |
| 100 | P_join formula; four members at 0.5 give 0.9375 | w1a inference | OK-inference | 1 − 0.5^4 = 0.9375 |
| 101 | `BootstrapPeersFunc` and `MemoryLookup` accept an application list | w1a S4, S9 | OK-raw | dht_options.go 324-343; address_lookup.rs |
| 103 | AutoNAT v1 spec "more than 3 peers"; go public after one dial-back | w1a S3, S4 | OK-raw | autonat-v1.md 81-83; autonat.go 318-332 |
| 103 | Code behaviour matters at 3 to 5 peers | inference | OK-inference | labelled |
| 113 | Trautwein: arXiv 2604.12484 v1, IMC '26; data 1 Dec 2022 to 1 Jan 2023 | w1a S1 (F) | OK-raw | paper.txt 23, 57, 277 |
| 113 | 70% ± 7.1% (abstract, §5.2.1); TCP and QUIC near 70% (§5.2.3); 97.6% first attempt (§5.2.3); ~29% excluded (§6) | w1a S1 (F) | OK-raw | paper.txt 31, 442 (§5.2.1), 558, 581 (§5.2.3), 658 (§6) |
| 114 | ProbeLab: 25-29 May 2026, 5 days; cloud prober behind nftables port-restricted cone | w1a S14 (D) | OK-raw | dcutr-final-report.md 130, 132 |
| 114 | 82.9% (3,042 of 3,669); APDF mapping-unresolved 37.0%; symmetric 39.7% (213 of 536), doubted; 36% never reserved | w1a S14 (D) | OK-raw | report 178-180, 189, 198; blog 59, 61, 173 |
| 115 | Ford: 380 reports, 2005; 82% UDP, 64% TCP; hairpin 24% / 13% (§6.2, Table 1) | w1a S2 (P) | OK-raw | cs0603074 paper.txt 31-32, 564-577, 602, 631 |
| 117 | CGN in 17-18% non-cellular eyeball ASes, >90% cellular | w1a S13 (P) | OK-raw | richter2016 paper.txt 100-102 (abstract), 669-672 (§5) |
| 117 | 11% non-cellular CGN ASes symmetric vs <2% CPE; 74% within 1 min; non-cellular CGN median 35 s (§6.5) | w1a S13 (P) | OK-raw | paper.txt 946-950, 973-976 |
| 117 | RFC 7021 §3.1 P2P applications failed behind CGN (lab) | w1a S12 (D) | OK-raw | rfc7021.txt 688-691 |
| 119 | Relay service only on hosts judged public unless forced; static relays; ACL | w1a S3, S4 | OK-raw | options.go 292-300, 322-330, 349; circuit-v2.md 213 |
| 119 | Defaults 2 min and 128 KiB in go and rust; `WithInfiniteLimits` | w1a S4, S5 | OK-raw | resources.go 62-68; rust relay behaviour.rs 160-161; relay/options.go 37-43 |
| 119 | Defaults enough for signalling, not 0.2-0.6 GB | w1a S4 inference | OK-inference | follows from 128 KiB; DCUtR < 500 bytes (Trautwein §3.2) |
| 119 | Relay must be directly reachable; no chaining | w1a S3 | OK-raw | circuit-v2.md 268 |
| 120 | Hivemind fork: 4 GiB per direction, 30 min; bootstrap peers as trusted relays | w1a S7 (C) | OK-raw | hm-p2pd 3762261 p2pd/main.go 94, 99-100 |
| 121 | `RelayMode::Custom`; iroh relays carry all traffic; self-host DNS name, TLS, ports 80 and 443 | w1a S9 (C, D) | OK-raw | endpoint.rs 1997-2011; concepts_relays.md 13; relays_self-hosted.md config block |
| 122 | Psyche defaults: project-named relays, n0 discovery | w1a S15 (C) | OK-raw | psyche 0bdb13d cli.rs defaults "psyche", "n0"; lib.rs 105-106, 135-142 |
| 123 | DCUtR starts from relayed connection; AutoNAT service off when private; Hivemind all-NAT = `use_ipfs` (c); iroh Disabled = direct only | w1a Q2 | OK-raw | DCUtR.md; autonat.go 345-350; dht.md 129-130; endpoint.rs 2000-2002 |
| 123 | IPv6 firewalls "will still commonly block" (Ford §1) | w1a S2 | OK-raw | cs0603074 paper.txt 107 and 53 (§1) |
| 128 | Templar: R2 bucket per participant; LastModified within 70 s (`hparams.json` line 50); chain block time; leader's list | w2c T1 (C) | OK-raw | templar 0fefc2a hparams.json 50; comms.py 520-544; miner.py 717-730 |
| 128 | 70 s communication per round of about 20 minutes (Covenant-72B §4.3) | w1d P4 (P) | OK-raw | 2603.08163 paper.txt 372-374 (§4.3 at 362) |
| 129 | Hivetrain: Hub repo per miner; central averager every 1,200 s | w2c T7 (C) | OK-raw | DistributedTraining 8d5dd20 neurons/averager.py 106; README 9, 14 |
| 130 | flwr-serverless: one key per node in a shared folder; async none / sync wait all; threads (§5) | w2c T2 (F, C) | OK-raw | async_federated_node.py 141-177; 2310.15329.txt §5 items 5-6 |
| 131 | HF²L: participants open PRs; owner writes main; listener waits then merges | w2c T8 (D) | OK-raw | hf_fl fe9569e README 194-206, 476-516 |
| 133 | STUNMESH-go: DNS, OpenDHT or script; "No rendezvous server, no relay"; Google STUN in example; no success rates | w2c N1 (D, C) | OK-raw | README 3-5, 93 (wording issue is P5) |
| 133 | File host cannot tell a peer its own address | w2c inference | OK-inference | labelled "w2c's decomposition (inference)" |
| 135 | ROADMAP risk table names file-host exchange as fallback | ROADMAP | OK-raw | docs/ROADMAP.md 156 |
| 135 | N = 5, S = 0.6 GB: 2.4 GB down per peer, 12 GB served; 240 s at 20 Mbit/s | w1a inference | OK-inference | (N−1)S = 2.4; N(N−1)S = 12; 0.6 × 8000 / 20 = 240 |
| 138 | Trautwein "in 40% of cases as of 2016"; Richter 40% cellular, 11% non-cellular | w1a S13 | OK-raw | 2604.12484 paper.txt 732; richter 945, 975 |
| 139 | Ford: fewer TCP than UDP; 2022 and 2026 studies TCP ≈ QUIC | w1a Q2 | OK-raw | Ford 31-32; Trautwein 581; ProbeLab blog 184 |
| 140 | No unconditional home-to-home rate; 36% never reach precondition | w1a Q2 | OK-raw | as lines 113-114 |
| 150 | Psyche: `join_authority`; `tick` callable by anyone; witness-quorum result per batch from common checkpoint | w1c S1 | OK-raw | w1c psy 0bdb13d authentication.md 11-13; general-workflow.md 208; model-sharing.md 7 |
| 150 | Payload hash checked against signed commitment; recomputation `todo!()` at coordinator.rs 701-702 | w1c S1 (C) | OK-raw | steps.rs 605-619; client.rs 437/466 (64-byte signature by iroh key); coordinator.rs 701-702 |
| 151 | Templar: registration; highest-staked validator's list; window; sync score from 2 values per tensor | w1c S2, S4 | OK-raw | comms.py 2239; Gauntlet 2505.21684 paper.txt 187-189 |
| 152 | prime-diloco: leader at rank 0 hosts the key-value store | w1c S5 (C) | OK-raw | prime-diloco de5b931 comms.py 95-100, 247 |
| 153 | PCCL: accepted peers vote newcomers in; master; bit-identical state; hash outliers | w1c S7 (P) | OK-raw | 2505.14065 paper.txt 191, 263-264, 287 |
| 154 | Agora: singleton Authorizer; DHT matchmaking, deterministic order | w1c S11 (P) | OK-raw | 2607.13332 paper.txt 336, 686, 1369 |
| 155 | OPEN-1B: chained state hash per step; anyone replays and compares bytes | w1c S8 | OK-raw | open-transformers d7b7b67 README 6-9, 54-56 |
| 157 | Psyche: no stored model; same checkpoint; witness-selected results; error on missing payload | w1c Q3b; w2b B7 | OK-raw | train.rs 600-632 (rejoin part is P6) |
| 157 | Templar same structure; PCCL and OPEN-1B checking half; fixed-order kernels | w1c S2, S7, S8 | OK-raw | README 48 ("fixed-order reductions") |
| 157 | Two properties: computes same vs can be checked | w1c inference | OK-inference | labelled |
| 159 | What the ledgers carry (Psyche, Templar, INTELLECT-2, RL Swarm); bytes off the ledger | w1c Q3c, Q7 | OK-raw | instance_state.rs 76-85; chain.py commitments; 2505.07291 paper.txt 489-581; SwarmCoordinator.sol index |
| 165-170 | Ledger-function table (carriers and losses) | w1c Q3d | OK-inference | header "(w1c Q3d; inference)" |
| 165 | Agora: peers check signed credentials locally | w1c S11 | OK-raw | 2607.13332 §3.6.1 (paper.txt 1369 region) |
| 167 | `create_commit(..., parent_commit=...)` "will fail if `revision` does not point to `parent_commit`", hf_api.py 5035-5039 | w1c S15 | OK-raw | w1c/docs/hfhubpy/hf_api.py 5033-5039 (a704b84) |
| 169 | Psyche pointer any member can overwrite | w1c S1 | OK-raw | instance_state.rs 397-414; coordinator.rs 598-600 |
| 172 | BOINC "outside servers" by URL and hash; uploads elsewhere | w2c B1, B2 | OK-raw | boinc.wiki Job-templates.md 26; boinc.txt 155 (§2.2) |
| 172 | Daemons "communicate and synchronize through the database" (Anderson §5.1) | w2c B2 (P) | OK-raw | boinc.txt 711-712 (§5.1 at 686) |
| 172 | Flower keeps state in the SuperLink | w2c F1 | OK-raw | per w2c F1 (explanation-flower-architecture.rst 41-51) |
| 172 | Plexus hash rule, rotating aggregator, "fully connected overlay" (§3.1) | w2c F3 (P) | OK-raw | 2503.05509.txt 106, 137, Algorithm 1 (the §5 locator is P7) |
| 175-179 | Candidates for the record of which updates count | inference | OK-inference | labelled "(inference)" |
| 177 | Templar uses R2 `LastModified` | w2c T1 | OK-raw | comms.py 520-544 (the "only Storage Buckets" scope is P8) |
| 181 | Glossary "Designated, trusted participants"; program checks only membership; last pointer wins; verifying task unimplemented | w1c S1 | OK-raw | glossary.md 31; instance_state.rs 397-414; coordinator.rs 598-600, 701-702; index.md 57 |
| 183 | Negative result over sources read | w1c gaps; w2c gap 5 | OK-raw | w1c Gaps first item; w2c Gaps 5 |
| 187 | Two meanings of asynchronous; stale methods on one global state; exceptions | w1b F1 | OK-inference | labelled |
| 196 | Async Local-SGD "a central server" (§3) | w1b S2 | OK-raw | 2401.09135 c.txt 142 |
| 197 | Decoupled DiLoCo syncer holds global fragments and outer optimizer state (§4) | w1b S1 | OK-raw | 2604.21428 html.txt 645 (§4 at 631) |
| 193-199 | Remaining "who holds what" rows (missing peer forces restart, FG §5.2; HeLoCo synchronizer; HALoS LPS/GPS; FoMoE central coordinator) | w1b F2 | OK-raw | 2606.22768 c.txt 226; 2606.00271 c.txt 97, 183; 2506.04531 c.txt 63, 80; FoMoE v2 paper_v2.txt 226 |
| 201 | "on CPU-only resources, partitioned into M shards"; "naturally leads to a parameter server architecture"; "highly stable, CPU-only resources with a minimal failure surface" (§4) | w1b S1 (P) | OK-raw | html.txt 635, 645, 655 |
| 201 | Syncer restart from Chandy-Lamport checkpoint (E.2); learners copy from peer learner (E.3); event tape bitwise replay (E.1) | w1b S1 (P) | OK-raw | html.txt 3519-3523, 3529-3535, 3547 |
| 201 | Hand-over of about two copies: 0.8 to 2.4 GB fp32 for 100M to 300M | inference | OK-inference | 2 × 100M × 4 B = 0.8 GB; 2 × 300M × 4 B = 2.4 GB |
| 201 | Rotating syncer would hold canonical model, against principle 6 | inference | OK-inference | labelled; ROADMAP.md 54 |
| 207 | Async Local-SGD naive vs sync +1.83 / +1.36 / +1.69% (Table 3, v2); 4 workers, H = 50, from 24,000-step checkpoint | w1b S2 | OK-inference | c.txt 218, 327-333; recomputed ln-PPL gaps |
| 208 | DN + DyLU −0.14 / −0.03 / +0.06%; −0.86 / −0.34 / −0.42% vs 4× batch | w1b S2 | OK-inference | c.txt 330-333; recomputed |
| 209 | HALoS Table 1 token values; Pythia 70M / 160M / 410M from scratch, 16 workers; reimplementation of Liu et al. | w1b S12 | OK-raw | 2506.04531 c.txt 196, 202, 209-212 (labelling of the % is P9) |
| 210 | Decoupled Table 5: 55.3 vs 54.4 text; 37.0 vs 37.6 vision; 51.4 / 25.7 without grace; 2B, M = 8, heterogeneous TPUs | w1b S1 | OK-raw | html.txt 1020-1069, caption 1107 |
| 210 | Table 12: 2B DP 55.1 vs Decoupled 54.4 at 26B tokens | w1b S1 | OK-raw | html.txt 3110 |
| 211 | HeLoCo Table 1: −1.8% (6.50 vs 6.62), +15.4% (7.64 vs 6.62); 15M, 5 workers | w1b S11 | OK-inference | 2606.00271 c.txt 214-225; recomputed −1.81, +15.41 |
| 212 | Eager Table 2: eager +0.75%, naive +12.7%, lowered lr +2.2%; 500M, 2 replicas, H = 30; Table 1 1B vs DP +0.75 / +0.40 / +0.41% | w1b S13 | OK-inference | 2502.12996 c.txt 212, 224-238, 243, 253-259; recomputed |
| 213 | "< 0.2%" up to an overlap of 10 inner steps (§3.3.2) | w1b S14 | OK-raw | 2501.18512 paper.txt 560-561 (setting is P11) |
| 214 | Factored Gossip LocalM1M2: +1.29% vs DiLoCo; +3.49% vs Sync DP (+2.37% at 30B); +8.99% at 16 workers; 1.5B, M = 8, 10B tokens | w1b S9 | OK-inference | 2606.22768 c.txt 186-206; recomputed |
| 215 | GASLoC 2-Peer +0.61 / +1.47 / +2.55%; 1-Peer +1.21 / +2.65 / +3.68%; DiLoCo vs DDP +3.77 / +6.92 / +11.01% (134M; 8/16/32) | w1b S10 | OK-inference | 2606.11081 c.txt 199, 207-212; recomputed |
| 216 | NoLoCo −1.45% to +0.42% vs DiLoCo; +0.83% to +7.68% vs FSDP; 125M to 6.8B with pipeline routing | w1b S8 | OK-inference | 2506.10911 c.txt 127-135; recomputed over all 16 cells (14 negative) |
| 217 | Moshpit "the same within the margin of error"; DeDLOC "virtually identical" | w1b S3, S4 | OK-raw | 2103.03239 c.txt 320; 2106.10207 c.txt 237 |
| 218 | FoMoE Table 6 v2: O_e = 2 +1.6 / +2.9 / +2.1%; O_e = 1 +3.4 / +4.8 / +5.3% vs full replica (K = 32 / 64 / 128); 54M, synchronous | w1b S17; notes 04a, 06 | OK-inference | re-fetched v2 HTML Table 6 (LocalAdamW, Fixed, M = 4: 121.42/112.00/103.91; 130.79/119.53/104.47; 143.72/123.50/111.89); recomputed 1.61/2.90/2.09 and 3.35/4.83/5.31 |
| 220 | Tuned DiLoCo-family gaps vs DP +0.3% to +3.9% at 4 to 8 workers | note 01 A2 | OK-raw | re-fetched 2503.09799 v1 Table 4 (paper_v1.txt 392-398: 35M M=8 +3.9%, 2.4B M=4 +0.3%) |
| 220 | Stage 0 +6.1% with plain averaging | Stage 0 report §3.1 | OK-raw | 2026-10-11-stage0-literature-report.md 297, 303 |
| 222 | All-reduce 2(N−1)/N × S; N = 4: 0.3 to 0.9 GB, 120 to 360 s at 20 Mbit/s | w1b F4 inference | OK-inference | 1.5 × 0.2/0.6; 0.3 × 8000/20 = 120, 0.9 × 8000/20 = 360 |
| 222 | Syncer moves about N × S; D-PSGD Table 1 hotspot | w1b S6 | OK-raw | 1705.09056 paper.txt 92-100, 394-395 |
| 222 | NoLoCo "essentially the same" bytes (App. C) | w1b S8 | OK-raw | 2506.10911 c.txt 564, 579 |
| 222 | Decoupled int4 +0.09%, 2 bits +32%, 1 bit +83% (Table 10) | w1b S1 | OK-raw | html.txt 2703-2705, caption 2803 |
| 224 | FoMoE "within expert replica groups", dense over all; central coordinator; 54M | w1b S17; 04a | OK-raw | FoMoE v2 paper_v2.txt 226, 1771; 04a 218, 231, 237 |
| 224 | DiPaCo per-module averaging with sqrt rescaling (04b block 4); SWARM synchronous stage all-reduce; Learning@home one holder, no averaging (04b block 7) | w1b S5, S16, S18; 04b | OK-raw | 04b lines 101, 112, 181; 2301.11913 c.txt 174, 1294 |
| 227 | Async Local-SGD parity, fine-tuning, 4 to 16 workers | w1b S2 | OK-raw | c.txt 218, 316-322 (HALoS % labelling is P9) |
| 228 | NoLoCo reimplementation "diverged after approximately 5k steps"; 22.65 vs 18.65 (App. B.1) | w1b S9 | OK-raw | 2606.22768 c.txt 678-686 |
| 229 | Streaming overlap "negligible" up to 10 steps vs 5-step divergence (App. B.2) | w1b S14, S9 | OK-raw | 2501.18512 paper.txt 560; 2606.22768 c.txt 696-698 |
| 230 | nanochat SFT ChatCORE 0.1190 vs 0.0157 (Table 1); Decoupled App. B names it contrary | w1b S15, S1 | OK-raw | 2511.13761 paper.txt 216-217; 2604.21428 html.txt 2224 |
| 231 | AD-PSGD parity vs "lower accuracy even after training for 150 epochs" in Moshpit | w1b S7, S3 | OK-raw | 2103.03239 c.txt 303 |
| 239 | Every system read keeps a full copy; INTELLECT-1 "30-60 minutes" for 10B | w1d Q5b; P8 | OK-raw | 2412.01152 paper.txt 342, 364 (§2.4.2) |
| 239 | Psyche clients full model; Templar validator checkpoints; Petals copy on Hub | w1d S2, S1, S5 | OK-raw | psyche model-sharing.md 3-5; templar dcp_checkpoint.py; petals from_pretrained.py |
| 240 | Petals downloads only shard files via `model.safetensors.index.json`; Psyche joiners fetch layer by layer | w1d S5, S2 | OK-raw | from_pretrained.py 103, 131; model-sharing.md 21 |
| 241 | Psyche `manifest.json` "an atomic marker", listings can mix versions; Templar `_LATEST.json`; flwr-serverless `.success` | w1d S2; w2c T1, T2 | OK-raw | gcs-checkpoints.md 159-161; dcp_checkpoint.py 168, 548-552; s3_folder.py (w2c T2) |
| 242 | Xet ~64 KB chunks, 64 MB blocks keyed by hash; Git LFS SHA-256; BitTorrent v2 SHA-256 Merkle root; SHARDCAST SHA-256 | w1d H3, H9, P12 | OK-raw | xet_deduplication.md 3, 64; xet_legacy-git-lfs.md 5, 11; bep_0052.rst 218; 2505.07291 paper.txt 344-346 |
| 243 | Web-seeded torrent still needs tracker or DHT; IPFS persists only while pinned; paid pinning | w1d H9, H11 | OK-raw | bep_0019.rst 27; persistence.md 18, 57; work-with-pinning-services.md 19 |
| 243 | No always-on seed needed (inference) | w1d H9 | OK-inference | labelled |
| 249 | Hub sizes: 500 GB hard, <200 GB; no per-repo limit; <100k files, <10k per folder; <100 files per commit; 60 s HTTP timeout | w1d H1 | OK-raw | storage-limits.md 73-76, 93-105, 114 |
| 249 | "Best-effort"; 5,000 per 5 min free, 3,000 per IP anonymous ("September '25", "subject to change"); commit limits undocumented | w1d H1, H2 | OK-raw | storage-limits.md 18; rate-limits.md 18, 60-73, 105-110 |
| 249 | "a few thousand commits"; "not meant to work as a database"; CommitScheduler 5 minutes | w1d H1, H4 | OK-raw | storage-limits.md 107-108; hf-hub-lib guides_upload.md 322 |
| 249 | "excessive bulk activity", "excessive or irrelevant data"; "with or without cause" | w1d H5 | OK-raw | content-policy.txt 87, 91; terms-of-service.txt |
| 250 | Buckets "non-versioned and mutable", "training checkpoints, logs, intermediate artifacts"; free allowance unquantified; events stream; repo recommendations do not apply | w1d H1 | OK-raw | storage-buckets.md 3, 342, 437 (grep-read per notes); storage-limits.md 60 |
| 251 | GitHub releases: 1,000 assets; under 2 GiB; "nor bandwidth usage"; 5,000/h; 80/min and 500/h | w1d H6, H7 | OK-raw | about-releases.md 49; releases.yml 1; large_files.yml 13; reusables (authenticated 3; secondary 9) |
| 251 | "significantly excessive" bandwidth; "excessive automated bulk activity"; one free machine account | w1d H8 | OK-raw | AUP 68, 105; ToS 85 |
| 252 | Git LFS 2 GB per file Free/Pro; 10 GiB storage and bandwidth; blocked without payment | w1d H6 | OK-raw | about-git-large-file-storage.md 27-28; large_files.yml; git-lfs.md 58, 104 |
| 253 | R2: 4.995 TiB; 10 GB-month, 1 M Class A, 10 M Class B; egress free; 1 write/s per key; "an R2 subscription" via checkout | w1d H12 | OK-raw | limits.mdx 21-27; pricing.mdx 18, 54-57; get-started_index.mdx 18-21 |
| 254-255 | BitTorrent and IPFS rows | w1d H9, H11 | OK-raw | as line 243 |
| 245 | Host limits read 2026-10-13 | w1d Q5a | OK-raw | header carries read date; notes H1-H12 fetch times 17:29-17:35 |
| 257 | 10 GiB / 0.6 GB ≈ 17 downloads; 10 GB-month / 0.6 GB ≈ 16 copies | w1d inference | OK-inference | 10.74/0.6 = 17.9; 10/0.6 = 16.7 (both floored) |
| 257 | 6 commits × 48 rounds = 288 per day; "a few thousand" in 1 to 2 weeks | inference | OK-inference | 288/day; 2,000/288 ≈ 7 d, 4,000/288 ≈ 14 d |
| 259 | Releases page "under 2 GiB" vs large-files page "plan's Git LFS limit"; agree free, differ paid | w1d H6 | OK-raw | about-releases.md 49; about-large-files-on-github.md 113-119; about-git-large-file-storage.md 27-30 |
| 261 | Unknowns list | w1d gaps | OK-raw | w1d Could not verify / Gaps |
