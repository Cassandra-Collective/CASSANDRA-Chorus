# Re-audit B: changed lines 227 to 576 (post-fix report)

Date: 2026-10-13. Report copy: `audit/report_postfix.md` (byte-identical to the repository report, checked with `cmp`).
Lines: 227 253 269 274 275 276 278 284 304 312 314 326 346 359 392 422 448 468 491 525 531 535 536 537 538 540 549 554 576.

Status: FINAL (after advisor review). Nothing in the repository was edited.

Method: each claim traced to its notes tag, then to the raw source under `sources/` (paper text, saved docs, clones at the recorded commit, saved API JSON). Derived numbers recomputed with `reauditB_scripts/async.py` and `gossip.py` (Python `-I`); HALoS ratios recomputed inline. Nothing downloaded was run.

Totals: 29 lines; 88 claim entries checked (some entries bundle several numbers from one source, e.g. the Agora timeouts); 6 PROBLEMs (P-B1 to P-B6), listed at the end. Classes: OK-raw or OK (notes) for most entries, 22 OK-inference, 6 PROBLEM.

## Per-line results

### L227 (Q4, Where sources disagree; HALoS)
- Async Local-SGD parity with synchronous DiLoCo, fine-tuning, 4 to 16 workers: w1b S2; raw 2401.09135 v2 Tables 1 to 3 (c.txt 303 to 334; 4/8/16 workers, continued from 24,000 steps). OK-raw.
- HALoS reimplements "the same algorithm": raw 2506.04531 c.txt 196 (Liu et al. 2024 with dynamic local updates and delayed Nesterov). OK-raw.
- "24.8% more tokens than DiLoCo at 160M from scratch (inference: 16.1B / 12.9B)": Table 1 (c.txt 209, 211) DiLoCo 12.9B, Async Local-SGD 16.1B at 160M; 16.1/12.9 = 1.2481. "from scratch" for 160M: c.txt 202. OK-inference.
- "70M and 410M columns' protocol is not confirmed, see section 7": only the 160M protocol is described (c.txt 202, 205); section 7 line 606 carries it. Pointer only. OK.
- Unverified rule: pass.

### L253 (Q5 host table, Cloudflare R2 row)
- 4.995 TiB per object: raw r2-docs/limits.mdx footnote 2 (line 27). OK-raw.
- Free per month 10 GB-month, 1 million Class A, 10 million Class B, egress free: pricing.mdx lines 54 to 57, 18. OK-raw.
- 1 write per second per key: limits.mdx line 23. OK-raw.
- "an R2 subscription" through a checkout: get-started_index.mdx lines 18, 21. OK-raw.
- New text "free tier exists": get-started line 23 "R2 is free to get started with included free monthly usage". OK-raw.
- "whether checkout needs a payment card is not confirmed, section 7": w1d "Could not verify" line 571; report section 7 line 636. Pointer only. OK.
- "may end up paying for": w1d H12 classification wording. OK (flag, not a claim of fact).
- Unverified rule: pass.

### L269 (Q6 behaviours table, partial round)
- Hivemind `partition.py` lines 128 to 136 (`register_failed_reducer`, "use our local part instead") and 248 to 255 (`on_sender_failed`, "Exclude that sender's data ... did not submit yet"): checked in clone `hm` at 4bd43b7 (2026-01-04). OK-raw.
- "Agora, whose all-reduce appears to derive from Hivemind's (inference from its code)": w2b B11 inference; raw `ar_runner.py` imports `hivemind.p2p`, `hivemind.proto.averaging_pb2`, docstrings name `DecentralizedAverager`, `AllReduceRunner` (lines 34 to 38, 90, 111 to 119) at 37d29a9. OK-inference.
- Unverified rule: pass.

### L274 (Q6, Psyche exception)
- "errors out of its loop (code)": `train.rs` lines 616 to 632 return `ApplyError` variants; `client.rs` line 213 `run.apply_state(*new_state).await?;` at 0bdb13d. OK-raw.
- "by inference, must rejoin at the next epoch": w2b B7 inference, labelled. OK-inference.
- Unverified rule: pass.

### L275 (Q6, time-boxes)
- Hivemind 15 s / 60 s: `optimizer.py` lines 177 to 178 (defaults 15.0, 60.0), 209 to 210 (fallbacks) at 4bd43b7; read-range addendum now in w2b B1. OK-raw.
- DeDLOC 5 s stragglers, 30 s give up: `albert/arguments.py` lines 23 to 28 at 10a9df8. OK-raw.
- Agora 40 s matchmaking, 30 s / 60 s, 2 of last 3 rounds terminates: paper v1 text lines 750 (Algorithm 3 caption), 669 to 670 (§3.3.1); config `reparam_llama/default.yaml` lines 21, 48 to 49. OK-raw.
- Psyche 360 s training, 5 s witness, `config/consilience/state.toml` (run_id "consilience-40b"): lines 1 to 10 at 0bdb13d; live-run caveat points to section 7 (line 663). OK-raw.
- prime-diloco 10 s heartbeat default: `comms.py` lines 24 to 26 at de5b931. OK-raw.
- "One place can wait indefinitely: prime-diloco's non-leaders ... `comms.py` lines 407 to 414": the non-leader `while ... == self._last_resolved_time: time.sleep(...)` loop has no exit but a changed value, with the TODO quoted verbatim (lines 410 to 414). OK-raw.
- "NoLoCo's blocking pair exchange waits until torch.distributed's default timeout, then raises (value not checked; see section 7) (w2b B10)": raw shows only blocking `dist.send`/`dist.recv` (`sparse_optimizer_c.py` lines 28 to 56) and `init_process_group(backend="gloo")` with no timeout argument (`train.py` lines 81 to 85) at a1b4a42. The wait-then-raise behaviour is w2b B10's "(inference)", and no source read shows it; section 7 (line 667) holds only the timeout value. PROBLEM (P-B1, low severity): an unlabelled inference stated as fact.
- Unverified rule: the NoLoCo clause asserts a runtime behaviour not read at source (see P-B1); the rest passes.

### L276 (Q6, coordinator loss)
- PCCL "Master Crash = End of Run": `docs/md/05-ImplementationNotes/03_MasterOrchestration.md` line 8 at 2af926a. OK-raw.
- prime-diloco leader death blocks the rest: `comms.py` 407 to 414 (see L275); w2b B9 inference. Covered by the bold "(inference)". OK-inference.
- Decoupled DiLoCo syncer restarts from a checkpoint: w1b S1 (App. E.2), also line 201, already audited. OK-raw (notes).
- "in the three systems read (inference)": w2b F3 inference. OK-inference.
- Unverified rule: pass.

### L278 (Q6, deliberate multiple holders)
- Bamboo exactly 2 per stage, different zones: w2b B13; raw 2204.12013 text lines 107 to 108 ("consecutive nodes in each pipeline come from different zones"). OK-raw.
- Oobleck f + 1 for f simultaneous failures: w2b B14; raw 2309.08125 v2 abstract (symbol lost in extraction, as the notes record). OK-raw.
- Agora 4 Pluralis nodes per body stage, 8 and 16 on head and tail, §5.1: raw 2607.13332 v1 lines 1831 ("5.1 SETUP") to 1843. OK-raw.
- "No volunteer system read enforces a minimum holder count without nodes its operator runs (inference over the systems read)": w2b F5 inference, labelled. OK-inference.
- Unverified rule: pass.

### L284 (Q6, Where sources disagree; PCCL)
- PCCL aborts and restores a failed collective (§4.1): raw 2505.14065 v1 lines 755 (heading 4.1), 930 to 931 ("aborted and unwinds and restores the buffer to its pre-operation state"). OK-raw.
- credits fault tolerance to restricting legal state transitions (§2.5.3): raw lines 306 to 320. OK-raw.
- "this report reads that as excluding partial rounds (inference)": labelled. OK-inference.
- Hivemind accepts partially averaged rounds: B1 code (see L269). OK-raw.
- Unverified rule: pass.

### L304 (Q7, per-participant limits)
- Hub `contributor` role confines writes to the user's own repositories: w1c S13; raw `organizations-security.md` line 17. OK-raw.
- GitHub rulesets block force pushes and require signed commits: w1c S14; raw `about-rulesets.md` line 37 (and the rules doc). OK-raw.
- "Team and Enterprise per `about-rulesets.md` line 17": raw line 17 ("for customers on Team and Enterprise plans"). OK-raw.
- "Enterprise only per line 21 of the same page": the only saved copy (`sources/w1c/docs/ghdocs/about-rulesets.md`) has "For organizations on the Enterprise plan, you can set up rulesets at the ... organization level" at **line 23**, not 21 (`grep -n`). Line 23 is inside w1c's recorded read range (17 to 41), so the reading is in scope; only the locator is wrong. PROBLEM (P-B2, low severity): wrong line number.
- Unverified rule: pass (the claim is in raw), subject to P-B2.

### L312 (Q8, what the candidates do)
- Hivemind 1.1.12 has 5 files (macOS x86_64 and arm64, manylinux aarch64 and x86_64 wheels, sdist): `sources/w1d/pypi-api/hivemind.json`. OK-raw.
- The manylinux x86_64 wheel and the sdist carry a publish attestation, publisher GitHub `learning-at-home/hivemind`, workflow `release.yml`: `prov_hivemind-1.1.12-...x86_64.whl.json`, `prov_hivemind-1.1.12.tar.gz.json`. OK-raw.
- "the rest not queried": only three provenance files exist (w1d query log: "Integrity API provenance for three files"). OK-raw.
- Petals 2.2.0.post1's wheel has none: `prov_petals-...whl.json` = "No provenance available". sdist not queried: no file. OK-raw.
- Query date 2026-10-13 17:42: w1d T4; file times 17:42. OK.
- Psyche `sha256` pin, Templar `git clone`: w1d T5 (unchanged, previously audited). OK (notes).
- Unverified rule: pass (image-signature check pointed to section 7).

### L314 (Q8, work units and updates as data)
- safetensors header capped at 100 MB, values not checked: w1d T7; raw `safetensors/README.md` line 172. OK-raw.
- `torch.load` `weights_only=True` default since 2.6, "narrows": raw `pytorch-docs/serialization.md` line 271. OK-raw.
- BOINC input templates list files "optionally with MD5 checksums": w2c B1; raw `Job-templates.md` line 51 (`[ <md5_cksum>...</md5_cksum> ]`, brackets mark optional) and lines 108 to 109. OK-raw.
- Unverified rule: pass.

### L326 (Q9 table, go-libp2p row)
- Go 1.26 (`go.mod` "go 1.26.0"), MIT (`repo.json` spdx_id), last commit 2026-09-21 (`commits.json`, 3c2c902, committer date 2026-09-21T14:17:10Z), v0.50.0 (2026-09-21): w2a block 3 and `sources/w2a/api/libp2p_go-libp2p/`. Query window in the L319 header. OK-raw.
- "pnet over TCP or WebSocket (inference)": w1a S4 inference from the QUIC and WebTransport PSK refusals (`p2p/transport/quic/transport.go` lines 74 to 76; `webtransport/transport.go` lines 98 to 100; clone at 3c2c902). The clone also shows WebRTC refusing a PSK (`webrtc/transport.go` lines 137 to 139), which supports the inference. OK-inference.
- Unverified rule: pass.

### L346 (Q9, corrections: Hivemind)
- Latest release 1.1.12 on 2026-01-03 (`release_latest.json` published_at 2026-01-03T07:41:24Z); newest commit 2026-01-04 (4bd43b7); the three newest commits 2025-08-03, 2025-10-12, 2026-01-04: "Make imports of hivemind submodules explicit", "Fix p2pd cross-compilation, build wheels in GHA", "Make Hivemind compatible with PEP 517" (`commits.json`), i.e. packaging, build and import changes. OK-raw.
- 70 open issues, 24 open PRs (search `total_count`): `search_open_issues.json`, `search_open_prs.json`. OK-raw.
- No Windows wheel: PyPI file list (w2a 1, queried 18:05:53 TST). OK-raw.
- `p2pd` fork newest commit 2023-11-21: w2a 1 (API 17:56:03 to 17:56:27 TST). OK (notes).
- Query date: the line carries none of its own. The GitHub facts (release, commits, issue and PR search at 17:55:34 to 17:55:46; fork at 17:56) fall inside the Q9 header's "all GitHub fields queried 2026-10-13 between 17:55 and 18:21 TST" (L319), which plausibly covers them. "No Windows wheel" rests on the PyPI file list (18:05:53 TST), which is not a GitHub field and carries no date anywhere in the line or header. PROBLEM (P-B3, low severity): one maintenance claim without its query date.
- Unverified rule: pass.

### L359 (Q10 table lead-in)
- Training Transformers Together is a volunteer run whose hardware and links the paper does not state: raw 2207.03481 §2 gives instructions to join "using free cloud providers or their own GPU" and a general 10 to 100 Mbit/s assertion; nothing on the hardware or links actually used in the run. OK-raw.
- "every measured setting is a data centre or rented cloud machines" for the other rows, checked row by row: DeMo (one 64-H100 cluster, w1d P1), DisTrO (32 H100 in DDP, P2), SparseLoCo (8 × H100 per replica, P3), Decoupled DiLoCo (TPU in Google data centres, w1b S1), Streaming DiLoCo (TPU data-centre runs, P5), MuLoCo (simulation on a cluster, P6), OpenDiLoCo ("hosted by different cloud providers", raw 2407.07852 line 380), INTELLECT-1 ("non-colocated data centers", raw 2412.01152 line 467), DiLoCo (CPU server and local machines, P9): all hold. Covenant-72B (L373) does not. Raw 2603.08163 v2 describes "permissionless participation" over "commodity internet links", peers "expected to have at least 8× NVIDIA B200 GPUs", trained "without relying on ... centralized datacenter training environments" (paper.txt lines 160 to 163, 338 to 342); it never says where the peers' machines are. w1d line 13 makes the blanket claim; the raw does not support it for Covenant-72B. PROBLEM (P-B4, low severity).
- Unverified rule: the Covenant-72B setting is asserted beyond the source (see P-B4).

### L392 (section 4.0 table, stale-updates row)
- New evidence cell "simulated failures at 2B to 5B dense and a 2.8B-active MoE": raw 2604.21428 v1 Table 2 (5B, c.txt 308), Table 3 (2.8B-active MoE, c.txt 329), Tables 10 and 11 (2B, c.txt 1114, 1141); 9B and the 3.8B-active MoE appear only without failures (Table 14, Fig. 7). OK-raw.
- First cell, unchanged: "Stale updates applied to one holder's state (Async Local-SGD, Decoupled DiLoCo, HeLoCo)". w1b F1 puts Decoupled DiLoCo in type 1 (quorum merges, no global barrier), not type 2 (stale updates), and the paper says its approach "never requires updating the model using a stale gradient computed on a previous version of the parameters" (App. A; c.txt line 1000). The paper's "stale" wording elsewhere (c.txt 338, 1367) is about a recovering or slow learner's own local state, not about updates applied at the syncer. PROBLEM (P-B5): Decoupled DiLoCo classed against its source and the notes. The earlier full audit passed this cell.
- Section 4 inference label present (L386, L388). No class (c) design recommended. Rule 2 pass.

### L422 (section 4.1, merge rule)
- Templar's sync score compares within a tolerance: w1c S4 ("2 values per tensor", threshold 3, §3.2) and Q3b (lines 373 to 374); raw 2505.21684 paper.txt line 175 ("3.2 Fast Evaluation") to about 203 ("setting the threshold to 3"). OK-raw.
- Merge formula, Stage 0 D11 rule, ROADMAP §1: design text in an inference section, unchanged and previously audited. OK-inference.
- Rule 2: pass.

### L448 (section 4.1, central)
- "Cloudflare R2 (an owner-subscribed account, possibly paid; section 7)": matches w1d H12's classification and the section 7 item (line 636). Flagged, not adopted. OK.
- Rule 2: R2 is (b), flagged against R1; the bucket event stream is "borderline", a flag only. No class (c) design recommended. Pass.

### L468 (section 4.2, risks)
- "go-libp2p's pnet runs over TCP or WebSocket only, not QUIC": QUIC refusal raw (see L326); "TCP or WebSocket only" is w1a's inference, under the subsection's "(inference)" heading (L458). OK-inference.
- 240 s per 0.6 GB at 20 Mbit/s: 0.6 × 8 / 0.02 = 240 s. OK-inference.
- Rule 2: Option B is not the default recommendation (L513). Pass.

### L491 (section 4.5, round log)
- Hub `write` role can "create, delete, or rename any repo": raw `organizations-security.md` line 19. OK-raw.
- `parent_commit` makes the commit fail if the branch moved: w1c S15 (client docstring, `hf_api.py` lines 5035 to 5039). OK (notes).
- "provided the Hub enforces `parent_commit` on the server, which is not confirmed (section 7; prototype P4)": section 7 line 624 and P4 (L574) exist. Pointer only. OK.
- Rule 2: the log is on the Hub, class (b). Pass.

### L525 (section 4.7, what would change it)
- GitHub release assets, 500 content-creating requests per hour: w1d H7; raw `reusable_secondary-rate-limit-rest-graphql.md` line 9. OK-raw.
- "an owner-subscribed R2 bucket (possibly paid; section 7; flagged)": as L448. OK.
- Rule 2: alternatives only, not the default; none class (c). Pass.

### L531 (section 5 table header)
- "relative gaps in loss or log-perplexity are w1b's arithmetic, inference": label present. OK-inference.

### L535 (section 5, Async Local-SGD row)
- "−0.18% to +0.06% in continued pretraining (Tables 1 to 3)": recomputed as log-perplexity (loss) ratios from raw 2401.09135 v2 (c.txt 306 to 334): Table 1 −0.05 / −0.05 / −0.17 / −0.14; Table 2 −0.14 / −0.14 / −0.18; Table 3 −0.14 / −0.03 / +0.06. Range −0.18 to +0.06. OK-inference. (−0.18 is computed from w1b's Table 2 values rather than stated in w1b; the header's "w1b's arithmetic" is slightly loose, but the inference label holds.)
- "−0.3% to −0.9% against a same-step large-batch worker at 4 workers (Table 3)": −0.86 / −0.34 / −0.42. OK-inference.
- "+0.25% at 16 workers (Table 2, 20M)": 40.98 against 40.60; w1b S2 states it. OK-inference.
- "150M, 4 workers, simulated speeds, not from scratch"; "server (a)": w1b S2 (§3 quote, App. 10.1). OK-raw.
- Rule 2: pass.

### L536 (section 5, HALoS row)
- As L227: 16.1B / 12.9B = 1.2481. OK-inference. "160M from scratch, 16 workers": c.txt 202. OK-raw. The 70M and 410M pointer goes to section 7 (line 606). OK.
- "server (a)": HALoS's Async-Local-SGD workers "fetch updated global models and upload gradients" (c.txt 205). OK-raw.

### L537 (section 5, Decoupled DiLoCo row)
- K = 1 with grace window 55.3 against K = 8 54.4 text (Table 5, c.txt 362). OK-raw.
- 2B 54.4 (Decoupled) against 55.1 (DP) (Table 12, 26B tokens); 9B 68.0 against 67.8 (Table 14, c.txt 1438 to 1455). Locators "Tables 5, 12, 14" now cover all three. OK-raw.
- Rule 2: pass.

### L538 (section 5, HeLoCo row)
- −1.8% (6.50 / 6.62) to +15.4% (7.64 / 6.62; the table's own −15.39): raw 2606.00271 c.txt 215 to 216. OK-raw and OK-inference.
- "15M, far from converged (inference)": w1b S11 inference, labelled. OK-inference.

### L540 (section 5, GASLoC row)
- 2-Peer +0.61 / +1.47 / +2.55%, 1-Peer +1.21 / +2.65 / +3.68% at 134M: recomputed from raw Table 1(b) (c.txt 207, 211, 212). OK-inference.
- "551M: 2-Peer matches DiLoCo at 8 replicas (2.64, Table 3)": c.txt 235, 240. OK-raw.
- "DDP's 2.64 (Table 2) comes from a one-step run at 16 replicas": c.txt 213, 215. OK-raw.
- "so no direct comparison": true of the parts w1b read, but the paper's Appendix D Table 6 (c.txt 978 to 982; outside w1b's read range, which excludes appendices) reports AdamW DDP 2.64 at both 8 and 16 replicas, so a same-replica comparison exists in the source. DDP is one-step by nature and, at a fixed global batch, its value does not change with replica count (Table 5 prints 3.18 three times, Table 6 prints 2.64 twice), so replica count was the only real gap, and Table 6 closes it. The report also compares H = 30 DiLoCo with the one-step-table DDP at 134M elsewhere (L215, "DiLoCo itself +3.77 / +6.92 / +11.01% against DDP", DDP 3.18 from Table 1(a)), so L540's caution is inconsistent with L215. PROBLEM (P-B6, low severity): a negative claim about the paper that its unread appendix contradicts.
- Rule 2: see P-B6; otherwise pass.

### L549 (section 5, gossip range)
- "about 0% to 5% against DiLoCo at 8 to 32 workers (inference: loss ratios in w1b S10, log-perplexity ratios in S9)": recomputed. GASLoC loss ratios (raw Tables 1b, 3): 134M 2-Peer +0.61 / +1.47 / +2.55, 1-Peer +1.21 / +2.65 / +3.68 (8 / 16 / 32 replicas); 551M 2-Peer 0.00 / +1.87, 1-Peer +1.14 / +5.24 (8 / 16). Factored Gossip LocalM1M2 log-PPL ratios (raw Table 1, c.txt 190 to 205): +1.29 (M = 8, 10B tokens), +0.72 (M = 8, 30B), +3.56 (M = 16). Minimum 0.00, maximum 5.24: "about 0% to 5%". OK-inference.
- "more with more workers within each paper": holds in every series (GASLoC 134M and 551M; Factored Gossip 8 to 16). OK-inference.

### L554 (section 5, gate needs)
- "(inference from the standards the sources use; w1b ...)": w1b heading line 469 "(inference, not a design)". OK-inference.

### L576 (section 6, P6)
- "hash check (w1c S8)": w1c S8, Gensyn OPEN-1B chained state hashes and replay. OK (notes; previously audited).
- "tolerance check (w1c S4)": Gauntlet sync score, threshold 3, §3.2 (raw lines 175 to 203). OK-raw.
- Durations labelled as estimates (L567). Rule 2: pass.

## Observations, not PROBLEMs

- L535 and L549: the extremes −0.18% (L535) and 0.00% and +5.24% (L549) are ratios computed from w1b's raw values (by audit 3 and this re-audit), not ratios w1b itself states. Both carry "(inference)" and recompute, so they pass; "w1b's arithmetic" in the L531 header and the L549 tag is slightly loose.
- L275: prime-diloco's "can wait indefinitely" is a direct reading of a polling loop with no exit but a changed value (`comms.py` lines 410 to 414). If the dead leader also hosted the store, `get` might raise instead; who hosts the store is an open item already in section 7 (line 618). "Can" keeps the sentence true.
- L326 and L468: go-libp2p's WebRTC transport also refuses a pre-shared key (`p2p/transport/webrtc/transport.go` lines 137 to 139, clone at 3c2c902), which strengthens the "TCP or WebSocket" inference. w1a did not read that file; no change needed.

## PROBLEM list

**P-B1. L275, unlabelled inference (low severity).**
Text: "NoLoCo's blocking pair exchange waits until torch.distributed's default timeout, then raises (value not checked; see section 7) (w2b B10)."
Why: the code read shows only blocking `dist.send`/`dist.recv` (`sparse_optimizer_c.py` lines 28 to 56) and `init_process_group(backend="gloo")` with no timeout argument (`train.py` lines 81 to 85). That the exchange waits for the default timeout and then raises is w2b B10's "(inference)"; no source read shows it, and section 7 (line 667) lists only the timeout value. Audit 3 P11 labelled every other code-derived behaviour in Q6.
Fix: "NoLoCo's blocking pair exchange sets no timeout of its own (gloo, no timeout argument); by inference it waits until torch.distributed's default timeout and then raises (value and behaviour not checked; see section 7) (w2b B10)." Optionally widen the section 7 item at line 667 to "NoLoCo's default torch.distributed timeout in the version it pins, and whether gloo's blocking send and recv then raise."

**P-B2. L304, wrong locator (low severity).**
Text: "(Team and Enterprise per `about-rulesets.md` line 17; Enterprise only per line 21 of the same page)".
Why: in the saved copy (`sources/w1c/docs/ghdocs/about-rulesets.md`) the Enterprise-plan sentence ("For organizations on the Enterprise plan, you can set up rulesets at the ... organization level") is on line 23; line 21 is a blank-adjacent `{% ifversion not ghes %}` block. Line 23 is inside w1c's recorded read range (17 to 41). The sentence also names the Enterprise plan without the word "only".
Fix: "(Team and Enterprise per `about-rulesets.md` line 17; line 23 of the same page names only the Enterprise plan for organisation-level rulesets)".

**P-B3. L346, a maintenance claim without its query date (low severity).**
Text: "Added: no Windows wheel, and its `p2pd` fork has had no commit since 2023-11-21."
Why: "no Windows wheel" rests on the PyPI file list (w2a 1, queried 2026-10-13 18:05:53 TST). The L319 header dates GitHub fields only; no date covers the PyPI query. The GitHub facts on the line fall inside L319's window.
Fix: "Added: no Windows wheel (PyPI, queried 2026-10-13 18:05 TST), and its `p2pd` fork has had no commit since 2023-11-21."

**P-B4. L359, setting asserted beyond the source for Covenant-72B (low severity).**
Text: "(w1d Q10; every measured setting is a data centre or rented cloud machines, except Training Transformers Together, a volunteer run whose hardware and links the paper does not state)".
Why: all eleven rows were checked. Ten are supported (clusters, TPU data centres, "different cloud providers", "non-colocated data centers", TTT as stated). Covenant-72B (L373) is not: the paper describes "permissionless participation" over "commodity internet links", peers "expected to have at least 8× NVIDIA B200 GPUs", trained "without relying on ... centralized datacenter training environments" (2603.08163 v2, paper.txt lines 160 to 163, 338 to 342), and never says where the peers' machines are. The blanket sentence at w1d line 13 is the notes' own generalisation.
Fix: "(w1d Q10; no measured setting is a home connection with consumer GPUs: the settings are data centres or rented cloud machines, except Covenant-72B, whose permissionless peers had at least 8 B200 GPUs each over "commodity internet links" (§3), and Training Transformers Together, a volunteer run whose hardware and links the paper does not state)".

**P-B5. L392, Decoupled DiLoCo classed as a stale-update method (moderate; unchanged cell on a changed line, passed by the earlier audit).**
Text: "| Stale updates applied to one holder's state (Async Local-SGD, Decoupled DiLoCo, HeLoCo) | no: (a) | yes, on the holder | the most churn evidence (Decoupled DiLoCo: ...) | R1 |".
Why: w1b F1 puts Decoupled DiLoCo in type 1 (quorum merges, no global barrier), not type 2 (stale updates applied to a newer model). The paper says its approach "never requires updating the model using a stale gradient computed on a previous version of the parameters" (2604.21428 v1, App. A; c.txt line 1000). Its other "stale" wording (c.txt 338, 1367) concerns a slow or recovering learner's own local state, not updates applied at the syncer. The row sits in the table that sets up the owner's R4 decision. The row's conclusion (one central holder, so R1 fails) still holds.
Fix (keeps the evidence cell and the other rows): first cell "One central holder merges updates as they arrive (Async Local-SGD and HeLoCo apply stale updates; Decoupled DiLoCo merges a quorum at its syncer and, by its own statement, applies no stale gradient, App. A)". The summary's L24 wording ("Every asynchronous method read that applies stale updates keeps the global model on one central holder") is consistent with w1b F1 and needs no change.

**P-B6. L540, "no direct comparison" contradicted by the paper's appendix (low severity).**
Text: "551M: 2-Peer matches DiLoCo at 8 replicas (2.64, Table 3); DDP's 2.64 (Table 2) comes from a one-step run at 16 replicas, so no direct comparison".
Why: GASLoC Appendix D Table 6 (2606.11081 v1, c.txt 978 to 982) reports AdamW DDP 2.64 at both 8 and 16 replicas. DDP is one-step by nature and replica-invariant at a fixed global batch, so the replica count was the only gap, and Table 6 closes it. w1b's read range excludes the appendices, so the sentence is true only of the parts read. It is also inconsistent with L215, which compares H = 30 DiLoCo with the one-step-table DDP (3.18) at 134M.
Fix, minimal and within what w1b read: "...; DDP's 2.64 is reported in Table 2 at 16 replicas; the parts read give no DDP value at 8 replicas". Fix, fuller: "551M: 2-Peer matches DiLoCo and AdamW DDP at 8 replicas (all 2.64; Tables 3, 6)" with locator "(2606.11081 Tables 1b, 3, 6)". This needs a read-status addendum in w1b S10 for Appendix D Table 6, following the audit-3 P14 pattern.

## Rule 2 summary

Section 4 lines (392, 422, 448, 468, 491, 525) sit under section 4's "Everything in this section is inference" (L386) and subsection "(inference)" headings. No line recommends by default a design that relies on a class (c) element. R2 is flagged as (b) against R1. The bucket event stream is "borderline", a flag only. Option B (library defaults are (c), "must be replaced") is not the default. The recommendation (L513 to L516) is Option A on class (b) hosts. Section 7 pointers on lines 227, 253, 275, 312, 448, 491, 525 and 536 point only and do not assert the unverified content. The exceptions are P-B1 (an unverified runtime behaviour stated as fact) and P-B4 (a setting asserted beyond the source).
