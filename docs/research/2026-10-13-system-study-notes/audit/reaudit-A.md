# Re-audit A: changed lines 6 to 213 of the system study report (post-fix)

Date: 2026-10-13 (about 23:35 TST onward). Auditor: re-audit agent A. Read-only: nothing in the repository was edited.
Report: `docs/research/2026-10-13-system-study-report.md`, byte-identical to `audit/report_postfix.md` (`cmp` silent). Line numbers are the post-fix copy's.
Lines in scope (27): 6 20 24 25 26 30 31 32 34 36 38 52 58 71 92 105 113 121 133 142 152 157 172 177 209 211 213.

Method: each line read in full with its neighbours (matrix rows read whole); the pre-fix text taken from `diff report_preaudit.md report_postfix.md`; each source-attributed claim traced to the notes at its tag, then to the raw source under `sysstudy/sources/` (paper text by grep, fetched docs, clones at the recorded commit with `git log -1`, saved API JSON) or `audit_sources/a2/`. Read-range check as in audit 3: every locator compared with the read-status lines of the notes. Derived numbers recomputed with `audit/scripts_reA/recalc.py`; Hub OpenAPI fields re-parsed with `audit/scripts_reA/oapi.py` (both Python `-I`, reading saved files only). Rule 2 checked against every "Could not verify" list and section 7 (lines 583 to 692).

Classes: **OK-raw** (matches the notes at the tag and the raw source), **OK-inference** (derived, labelled, recomputes), **OK-judgment** (rating, design statement or classification supported by the cited evidence; no number), **PROBLEM**.

## Results by line

**L6 (header, Status).** Claim: audited 2026-10-13, every number in sections 1 to 6 against raw sources, plus unverified items; fixes applied. Audit scopes: audit 1 lines 1 to 82, audit 2 lines 83 to 262, audit 3 lines 263 to 582, audit 4 header and sections 1 to 6; fix-log "Applied: 39. Not applied: 0". OK-judgment. Rule 2: OK.

**L20 (Answer).**
1. One supported shape (deadline-closed rounds, inputs on a public host, every peer merges): OK-judgment (sections 3 to 4).
2. "Every system read with one shared model keeps one function central: an agreed record of which updates count": OK-judgment. w1c Q3d (inference) and w1c Gaps ("every system that fixes a round's inputs uses either a ledger or a single coordinator or leader"); w2c part 1 inference summary. Systems without one shared model (gossip, group all-reduce, Agora, RL Swarm) are excluded by the report's own L187.
3. Psyche on a ledger; Templar in a ledger clock plus one validator's list: OK-raw (w1c S1, S2, Q3d; code lines checked by audit 1).
4. HF²L with the owner: OK-raw (w2c T8).
5. BOINC in its server database: OK-raw (w2c B2 §5.1; `sources/w2c/papers/boinc.txt` 711 to 712 "communicate and synchronize through the database", §5.1 heading at 686).
6. Flower in its SuperLink: OK-raw (w2c F1; part 1 summary "Flower in its SuperLink").
7. flwr-serverless's asynchronous mode has none, so peers can merge different sets: OK-raw (w2c T2, part 2 pattern 4; `w2c/fs/flwr_serverless/federated_node/async_federated_node.py` 141 to 154 at `bbf8a10`: each node merges whatever unseen keys it finds).
8. Signed configuration plus conditional commit log could carry it (inference, untested; w1c S15): OK-inference; `w1c/docs/hfhubpy/hf_api.py` 5033 to 5039 docstring confirmed.
Rule 2: OK. Server-side `parent_commit` enforcement (section 7, L624) is not asserted; "untested" is stated.

**L24 (finding 1).**
1. Every asynchronous stale-update method read keeps the global model on one central holder (w1b F1, F2): OK-raw (F2 table: Async Local-SGD server §3, Decoupled DiLoCo syncer §4, HeLoCo synchronizer §3, HALoS LPS/GPS §4.1).
2. Only the one-round overlap methods avoid one, by keeping a synchronous all-reduce: OK-judgment (F1 exception for S13, S14; DeDLOC's and SWARM's one-round delayed updates also keep a group all-reduce).
3. Server-free methods are group all-reduce (Moshpit, DeDLOC, SWARM) and gossip; gossip leaves no single shared model: OK-raw (F1, F2).
4. "costs about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9)": the numbers recompute (S9 LocalM1M2 +1.29% at M = 8 and +3.56% at M = 16, `w1b/2606.22768/c.txt` 191 to 192, 204 to 205; S10 0.00% to +5.24%, `w1b/2606.11081/c.txt` 206 to 212, 233 to 240). OK-inference for S9 and S10. **PROBLEM P1 (scope):** the sentence says "gossip", but NoLoCo, which the report itself files under gossip (L69, L216), measures −1.45% to +0.42% against DiLoCo at 4 to 16 data-parallel replicas (w1b S8; `w1b/2506.10911/c.txt` 129 to 136; e.g. large, C4: 16.6 against 17.3), and S9's NoLoCo reimplementation without routing is +6.6%. w1b F3 scoped the range to "pure gossip ... in the two 2026 papers that measure it" and noted NoLoCo's opposite sign; the summary drops both. The framing predates the fix (pre-audit "1% to 4%").
5. Asynchronous branch closed unless a rotating holder, "which no source tests"; group branch open: OK-judgment (F2: "No paper read describes or tests a synchronizer role that rotates").
Rule 2: OK.

**L25 (finding 2).**
1. Direct connections need one of our machines reachable (w1a Q2): OK-judgment (audit 1).
2. File-host exchange needs only outbound connections (inference): OK-inference.
3. "four precedents outside a single cloud region": count OK (w2c part 2 table: Templar, Hivetrain, flwr-serverless, HF²L, plus LambdaML in "one cloud region", T3). **PROBLEM P2 (minor, wording):** of the four, only Templar/Covenant-72B reports runs across sites. flwr-serverless "simulated concurrent training jobs with python multi-threading" on one machine (`w2c/papers/2310.15329.txt` 532 to 534; w2c T2: "not measured across real machines"), and HF²L reports no runs (w2c T8, "Numbers: none"). "Outside a single cloud region" is true of their designs, not of anything reported.
4. None measured on home connections (w2c part 2; gap 1): OK-raw.
Rule 2: OK.

**L26 (finding 3).**
1. Hivemind, Petals, prime-diloco, Templar dormant or barely maintained: OK-raw (w2a 1, 2, 9, 11; audit 1 and audit 3 P8 checks of `commits.json` and the Templar README notice).
2. Psyche: no default-branch commit since 2026-03-20: OK-raw (w2a 8; `w2a/api/PsycheFoundation_nousnet/commits.json`, saved 17:59 TST: newest `0bdb13d94a05`, 2026-03-20T19:58:10Z; `repo.json` `default_branch` main).
3. "(status not confirmed; see section 7)": pointer to L651. OK.
4. None documents native Windows support: OK-raw (audit 1).
5. go-libp2p and iroh released within the last month: OK-raw (v0.50.0 2026-09-21, v1.3.0 2026-09-28; 22 and 15 days before 2026-10-13).
6. Both test on Windows: OK-raw (audit 1). Query date carried ("GitHub API, queried 2026-10-13").
Rule 2: OK.

**L30, L31, L32 (designs A, B, C).** Design summaries under "(inference; section 4)". A: conditional-commit log, every peer merges, central signing key, configuration, host (b): consistent with 4.1 and L448. B: meets R1 and R3 only while one of ours is reachable (unmeasured): consistent with 4.2 and 4.4. C: A as record and fallback, B's transfer where measured: consistent with 4.3. 3 claims, OK-judgment. Rule 2: A's log relies on server-side `parent_commit` enforcement (section 7, L624); L30 states the design only, and L36 names the prototype. OK.

**L34.**
1. Rolling assignment gives each expert 2 holders: OK-judgment (Chorus's own design, per the brief).
2. Churn can leave 1 or 0, which no volunteer system read prevents without operator-run machines (w2b F5, inference): OK-inference (F5 inference bullet).
3. Publishing every round caps the loss at one round (inference): OK-inference.
4. Ledgers, public STUN, the bucket event stream are class (c) or borderline, flagged: OK-judgment (L135, L250, L448, 4.5).
Rule 2: OK.

**L36 (Recommendation).** Labelled inference. Own repositories plus signed log entries (4.5); Gate N1b candidate; four prototypes P5 (commit limits), P4 (concurrent conditional commits), P3 (upload times), P6 (merge determinism), matching 4.7's dependency list. 3 claims, OK-judgment. Rule 2: OK (no assertion of server enforcement or token granularity; 4.5 points to section 7).

**L38 (Confidence).**
1. Negative findings 1 and 2 rest on the sections and code paths the notes list as read: OK-judgment (matrix read-status letters; audit 1 P5).
2. No source measures home links, groups of 3 to 5, holders 2 to 1, file-host exchange of 0.2 to 0.6 GB (w1b gaps; w2b F6; w2c gap 1): OK-raw (notes).
Rule 2: OK.

**L52 (Petals row, all 8 cells).** R1: OK-raw (w1a S8, wiki read whole; `sources/w1a/petals-wiki/launch-own-swarm.md` line 24 "a good practice to have a few CPU-only machines that are always online", line 26 "you can skip this step", line 40 "as long as at least one of their initial peers is alive"); the "Partly" rating matches Hivemind's (L51) on the same kind of evidence. R2, R3: OK-judgment (S8). R4, R5: OK-raw (w2b B5; `block_selection.py` 59 to 60). R6, R7: OK-judgment. Central: OK-raw (w1a S8 `constants.py`; w2a 2). Rule 2: Petals' rebalancing threshold (section 7) not used. OK.

**L58 (prime-diloco row, label and 8 cells).** Label "(INTELLECT-1's framework by its own description; section 7)": OK-judgment (w1d S3: description "prime is a framework for ...", the framework name the INTELLECT-1 report uses; section 7 L644 states the caveat). R1 rank-0 store: OK-raw (`w1c/code/pdl/repo/src/zeroband/comms.py` 95 to 100, 247 at `de5b931`: global `TCPStore` with `is_master=self._global_leader`, `global_rank == 0`; membership keys written to that store, lines 111 to 125). R2 fsspec: OK-raw (w1d S3). R3 Tailscale "as run": OK-raw (w1c S5, INTELLECT-1 §2.5), qualified by the label. R4 to R7: OK-judgment (w2a 9; w1c S5). Central: Tailscale "(c) by inference only (section 7)": pointer to L619. Rule 2: the untraced `god_store` host (section 7, L618) is not used; R1 rests on the global store. OK.

**L71 (FoMoE row, all 8 cells).** R1 quote: OK-raw (`audit_sources/a2/fomoe/paper_v2.txt` 226 to 227, under "3.1 Architecture and design" at 201: "We employ a central coordinator to manage initialization, broadcasting, and aggregation, restricting our study to synchronous training"); read status F (Stage 0 note 04a: "full text (v2 PDF)"). R4 synchronous: OK-raw (same sentence). R5, R6: OK-judgment (w1b S17). R2, R3, R7: OK-judgment. Central (a): OK-inference (S17). Rule 2: OK.

**L92.**
1. `ProtocolPrefix` gives a separate Kademlia protocol: OK-raw (w1a S4; audit 2).
2. pnet refuses nodes without the key: OK-raw (w1a S3; audit 2).
3. QUIC and WebTransport refuse a pre-shared key, with the quoted error: OK-raw (`w1a/go-libp2p/repo` at `3c2c902`: `p2p/transport/quic/transport.go` 74 to 76; `webtransport/transport.go` 98 to 100).
4. "so a pnet pool runs over TCP or WebSocket (inference)": OK-inference. It holds in raw: the only other transport, WebRTC, also refuses (`webrtc/transport.go` 137 to 139), and the upgrader applies the PSK to stream transports (`p2p/net/upgrader/upgrader.go` 156 to 157). See observation 1.
5. Hivemind starts a new DHT with no initial peers: OK-raw (w1a S7, `node.py`).
6. iroh has no DHT by default and uses `MemoryLookup`: OK-raw (w1a S9).
Rule 2: rust-libp2p pnet over QUIC (section 7) is not asserted. OK.

**L105.** Public-address question (w1a gaps 1, 2): OK-raw. rust-libp2p routing-table persistence "(not checked; see section 7)": w1a gap 8; section 7 L599. Rule 2: OK.

**L113 (Trautwein row).** Read status F (w1a S1). 39 countries and "skewed toward the U.S." (§4.3): OK-raw (`w1a/2604.12484/paper.txt` 303 to 306; §4.3 heading at 299). Data 1 Dec 2022 to 1 Jan 2023: OK-raw (277). 70% ± 7.1% (abstract, §5.2.1): OK-raw (31, 442). TCP and QUIC near 70%: OK-raw (w1a S1; audit 2). 97.6% on the first attempt: OK-raw (40, 558). About 29% excluded (§6): OK-raw (658). "from scratch is necessarily lower" (§6): OK-raw, a contiguous substring of lines 666 to 667 in the Limitations paragraph of §6 (heading at 576). Rule 2: second-hand numbers (section 7) not used. OK.

**L121.** `RelayMode::Custom`: OK-raw (w1a S9, `endpoint.rs` 2010). Relays carry all traffic: OK-raw (`iroh-docs/concepts_relays.md` 13). Self-hosted setup with DNS name, TLS, ports 80 and 443: OK-raw (`iroh-services_relays_self-hosted.md` 34 to 39). Windows relay binary in release v1.3.0 (GitHub API, queried 2026-10-13 18:21 TST): OK-raw (w2a 7; query log 18:21:14, `releases/latest` assets; saved `w2a/api/n0-computer_iroh/release_latest.json`: tag v1.3.0, asset `iroh-relay-v1.3.0-x86_64-pc-windows-msvc.zip`). Rule 2: the "9 out of 10" claim is not used. OK.

**L133.** STUNMESH-go at `74a0d38` (w2c N1, README read whole): endpoint encrypted, shared through DNS, OpenDHT or a script, "No rendezvous server, no relay": OK-raw (README 5). Example configuration `refresh_interval: "1m"`: OK-raw (README 81 to 85). Cone-NAT advice "For best results": OK-raw (README 22). Google STUN in the example, (c): OK-raw (README `stun.l.google.com:19302`). No success rates: OK-raw (N1). Decomposition (inference): OK-inference (w2c part 2). Untested anywhere read: OK-raw (w2c part 2, gap 2). Rule 2: STUNMESH-go's success in practice (section 7) not asserted. OK.

**L142.** Unknowns: per-pair success, Turkish CGN, IPv6, iroh `--dev` relay (w1a gaps 1, 3, 6, 7), the last pointed to section 7 (L600); file-host timing (w2c gap 1). Rule 2: OK.

**L152 (Q3 table, prime-diloco row).** "not described (INTELLECT-1 paper)": OK-judgment (w1c S5 grep; Q3a). Rank-0 leader hosts the key-value store: OK-raw (code as for L58). All-reduce over the live group: OK-raw (w1c S5, §2.4.1, §2.4.5). "none described": OK-judgment. Rule 2: `god_store` not used. OK.

**L157.** No stored model; same checkpoint; witness-selected results: OK-raw (w1c Q3b; audit 2). Stops with an error: OK-raw (`w1c/code/psy/repo` at `0bdb13d`: `shared/client/src/state/train.rs` 614 to 632 return `ApplyError` variants; `shared/client/src/client.rs` 213 `run.apply_state(*new_state).await?`). "would have to rejoin at the next epoch (inference, w2b B7)": OK-inference. Templar same structure (w1c S2); PCCL and OPEN-1B as the checking half (w1c S7, S8); two properties (inference): OK-raw and OK-inference (unchanged; w1c Q3b). Rule 2: Psyche joiner hash check (section 7) not asserted. OK.

**L172.** Most server functions split into a rule, a static host or a peer role: OK-judgment (w2c part 1, labelled inference there; see observation 3). BOINC remote files by URL and hash: OK-raw (`w2c/bw/Job-templates.md` 26 to 28: URL, size and MD5). Uploads elsewhere: OK-raw (`boinc.txt` 155, §2.2 at 139). Daemons "communicate and synchronize through the database" (§5.1): OK-raw (711 to 712). Flower SuperLink: OK-raw (w2c F1). Plexus hash rule and rotating aggregator: OK-raw (`w2c/papers/2503.05509.txt` 133 to 142, Algorithm 1). Fully connected overlay (§3.1): OK-raw (106, 134 to 137). "all nodes remain online" (§6): OK-raw (453; the right-column continuation after the "6 Broader Impact and Open Challenges" heading at 475, before "7 Conclusions"). Read range: w2c F3 records reading the "limitations passage", so the part was read (see observation 2). Rule 2: OK.

**L177.** Templar R2 `LastModified` (w2c T1): OK-raw. "Of the Hub API endpoints read (model repositories and Storage Buckets), only Storage Buckets list a per-file `uploadedAt`": OK-raw (w2c T9; re-parse of `w2c/hubapi/openapi.json`: bucket `tree` and `paths-info` list `uploadedAt` and `mtime`; model `tree` and `paths-info` list `lastCommit` only). Server assignment "not confirmed (see section 7)": L680. Rule 2: OK.

**L209 (HALoS row).** Pythia 160M from scratch, 16 workers: OK-raw (w1b S12; `w1b/2506.04531/c.txt` 202). "24.8% more tokens than DiLoCo to the same loss at 160M from scratch (inference: 16.1B / 12.9B)": OK-inference (Table 1, c.txt 209 and 211; recomputed 24.8%). 70M and 410M protocol "not confirmed (section 7)" and "not used here (section 7)": pointers to L606. Rule 2: HALoS's venue (section 7) not stated. OK.

**L211 (HeLoCo row).** 15M, 5 workers: OK-raw (`w1b/2606.00271/c.txt` 227). "far from converged (inference: losses near 6.5)": OK-inference (6.50 to 6.62, c.txt 215). −1.8% with no staleness: OK-inference (6.50 / 6.62 = −1.81%; the paper calls the homogeneous case "the absence of staleness", c.txt 223). +15.4% with severe staleness: OK-inference (7.64 / 6.62 = +15.41%; the paper's ΔSN −15.39, c.txt 216). Rule 2: HeLoCo's abstract figures (section 7) not used. OK.

**L213 (Streaming DiLoCo overlap row).** "under 0.2% up to an overlap of 10 inner steps" (§3.3.2): OK-raw (w1b S14; `w1b/2501.18512/paper.txt` 556 to 563). "500M (the paper's ablation model, §3.3)": true in raw (`paper.txt` 499 to 505, §3.3 opening: "we perform all our ablations on a model of size 500 million parameters"). **PROBLEM P3 (read range, value true in raw; same class as audit 3 P14):** no notes file records §3.3's opening paragraph as read (w1b S14: §2.3, §3.3.2; w1d P5: §2.4, §3.1, §3.2 Table 1, §3.3.3, Supplement Table 4; Stage 0 01 A3: §3.1, §3.2, Supplementary). The Figure 8 caption does not give the size, and w1b F3 still records this row's setting as "35M to 4B (01)". Only audit 2 read it (audit-2 P11). Rule 2: OK.

## Counts

27 lines checked; 118 claims, counted as numbered or listed above (each matrix cell or label once: L52 8, L58 9, L71 8; L30 to L32 one each). OK-raw 64, OK-inference 13, OK-judgment 38, PROBLEM 3 (L24 item 4 is counted as the PROBLEM, although its numbers recompute).

## PROBLEM list

Summary: rule 2 holds on all 27 lines, and no number is wrong. The three PROBLEMs are one of scope, one of wording and one of read range.

**P1. L24 (minor; scope): the gossip cost is stated for gossip as a class.** Text: "and gossip, which leaves no single shared model and costs about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9)".
Why: the range is right for S9's pure pairwise gossip and S10's GASLoC, but the sentence states it for gossip as a class. NoLoCo, which the report files under gossip (L69, L216), measures −1.45% to +0.42% against DiLoCo at 4 to 16 replicas with pipeline routing (w1b S8; `2506.10911/c.txt` 129 to 136). It measures +6.6% when reimplemented without routing (w1b S9 App. B.1). w1b F3 limits the range to "pure gossip ... in the two 2026 papers that measure it" and notes NoLoCo's opposite sign. The wording was already there before the fix.
Fix: "and gossip, which leaves no single shared model; pure pairwise gossip costs about 0% to 5% against DiLoCo at 8 to 32 workers in the two papers that measure it (inference: loss ratios in w1b S10, log-perplexity ratios in S9), while NoLoCo with pipeline routing reports −1.45% to +0.42% (w1b S8)."
Short variant for the summary's 620-word budget (about 6 words added): "... and gossip, which leaves no single shared model; pure pairwise gossip costs about 0% to 5% against DiLoCo at 8 to 32 workers (inference: ...; NoLoCo differs, w1b S8)."
Related line outside this range: L549 (section 5) gives the same range but already says "Pure gossip", so it is scoped. It still omits NoLoCo, and that line belongs to the re-audit of lines after 213.

**P2. L25: "outside a single cloud region" (minor wording).** Text: "has four precedents outside a single cloud region, none measured on home connections (w2c part 2)".
Why: this is true of the four designs, which unlike LambdaML (T3) are not tied to one cloud region. But only Templar/Covenant-72B reports runs across sites. flwr-serverless ran as threads on one machine (`2310.15329.txt` 532 to 534; w2c T2), and HF²L reports no runs (w2c T8). A reader will take "outside a single cloud region" to describe where they ran.
Fix: "has four precedents whose design is not tied to one cloud region (unlike LambdaML), none measured on home connections (w2c part 2)".

**P3. L213: the setting comes from a part no notes file records as read (value true in raw).** Text: "| 500M (the paper's ablation model, §3.3) |".
Why: the 500M comes from §3.3's opening paragraph (`2501.18512/paper.txt` 499 to 505), outside every recorded read range (w1b S14, w1d P5, Stage 0 01 A3). Only audit 2 read it. w1b F3 still gives this row's setting as "35M to 4B (01)", so the report and the notes it cites disagree. Same class as audit 3 P14.
Fix: the report wording can stay. In w1b S14, add one bullet after its read-status line, as was done for audit 3 P14: "audit 2 (2026-10-13) read §3.3's opening paragraph (`paper.txt` lines 499 to 505): 'we perform all our ablations on a model of size 500 million parameters'; the §3.3.2 overlap result is at 500M." Optionally, change w1b F3's setting cell for the τ-step overlap row from "35M to 4B (01)" to "500M (§3.3)". Fallback in the report, if notes edits stay restricted: "500M (the paper's ablation model, §3.3 opening, `paper.txt` lines 499 to 505, read in audit 2)".

## Observations (not PROBLEMs)

1. L92: the inference's stated premise names QUIC and WebTransport only. WebRTC also refuses a PSK (`webrtc/transport.go` 137 to 139). Audit 2 read that file; w1a S4's read status does not include it. The conclusion holds. Optional wording: "the QUIC, WebTransport and WebRTC transports".
2. L172: w2c F3 and the w2c part 1 findings still say §5 for "all nodes remain online"; the report's §6 is right per the raw text. A notes correction would remove the mismatch.
3. L172: "most server functions split into a rule, a static host or an occasional peer role" is w2c's labelled inference. Here it appears without the label. It is a classification, not a number.
4. L6: if this re-audit leads to further edits, the status line should record them.

Status: COMPLETE (advisor review done; P1 severity, the short P1 variant, the L549 note and the P3 report-side fallback were added after it).
