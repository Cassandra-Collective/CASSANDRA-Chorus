# Audit 3: report lines 263 to 582 (Q6 to section 6)

Auditor 3, 2026-10-13 (about 22:00 to 23:15 TST). Report frozen copy: audit/report_preaudit.md. Status: final, after advisor review.

Method: each claim traced to its notes tag, then to the raw source in `sources/` (grep of paper text, fetched docs, clones at the recorded commit, saved API JSON, saved CI workflow files). Derived numbers recomputed with `scripts_a3/calc_s5.py` (Python `-I`). Two maintenance facts re-fetched raw into `audit_sources/a3/` (GitHub API, unauthenticated, 2026-10-13 22:53 TST): Templar commit 0fefc2a file list; Hivemind commits since 2025-01-01. Nothing run, built or installed. Read-range check (method step 3): every code line, paper section, table and doc line cited in scope was compared with the notes' read-status lines; all lie inside except the two code locators in P14 (values still confirmed in raw).

## Counts by class

| Class | Count |
|---|---|
| OK-raw | 80 table rows |
| Derived, recomputes, but sits under an unlabelled table | 7 table rows (lines 536 to 544; one PROBLEM, P1) |
| OK-inference | 12 table rows |
| PROBLEM | 15 entries (P11 holds 5 unlabelled inferences, P14 two read-range gaps; 22 report locations in all) |

Section-4 checks: inference labels present on the section and every subsection; no class (c) design recommended by default (ledger flagged for Phase 6; library defaults (c) "must be replaced"; bucket event stream "borderline"; R2 flagged). Section-6 durations are labelled as the report's estimates (line 567).

## PROBLEM list

**P1. Line 531 (section 5 table header), derived but unlabelled.** Text: "**Evidence on each option's quality cost** (all from section 3, Q4; w1b F3 and evidence grid)". The table's percentage gaps (−0.14%, −0.3% to −0.9%, +18.6% / +24.8% / +30.9%, −1.8% to +15.4%, +1.29%, +3.49%, +8.99%, +0.61% to +3.68%, −1.45% to +0.42%, +6.6%, +0.75%, +1.6% / +2.9% / +2.1%) are w1b's arithmetic (loss ratios or log-perplexity ratios). Q4 labels them (line 205); section 5 does not. All recompute (see rows 536 to 544). Also line 538, "15M, far from converged", is w1b S11's inference (the authors say only that it "does not yet capture the scale"). Fix: "**Evidence on each option's quality cost** (all from section 3, Q4; w1b F3 and evidence grid; relative gaps in loss or log-perplexity are w1b's arithmetic, inference)", and "15M, far from converged (inference)".

**P2. Line 535, wrong value (range from one table, three cited).** Text: "Async Local-SGD, Delayed Nesterov + Dynamic Local Updates (2401.09135 v2, Tables 1 to 3) | ... | −0.14% to +0.06% in continued pretraining | −0.3% to −0.9% against a same-step large-batch worker". Both ranges are Table 3 only (4 workers). Tables 1 and 2 (20M) give −0.18% against DiLoCo at 16 workers (40.98 against 41.25) and +0.25% against the 16× large-batch worker (40.98 against 40.60): the sign flips. Fix: "−0.18% to +0.06% in continued pretraining (Tables 1 to 3) | −0.3% to −0.9% against a same-step large-batch worker at 4 workers (Table 3); +0.25% at 16 workers (Table 2, 20M)".

**P3. Line 549, wrong value and derived but unlabelled.** Text: "Pure gossip costs about 1% to 4% against DiLoCo at 8 to 32 workers, growing with worker count." w1b's own cells run from 0.0% (GASLoC 2-Peer, 551M, 8 replicas: 2.64 against 2.64) to +5.24% (GASLoC 1-Peer, 551M, 16 replicas: 2.81 against 2.67); Factored Gossip LocalM1M2 at 16 workers is +3.56% (22.24 against 19.99, auditor arithmetic). Fix: "Pure gossip costs about 0% to 5% against DiLoCo at 8 to 32 workers (w1b's arithmetic, inference), more with more workers within each paper." The same "about 1% to 4%" appears in the Summary (line 26) and w1b F3, outside this scope; they should change together.

**P4. Line 392 (section 4.0 table), wrong value attributed to a source.** Text: "the most churn evidence (Decoupled DiLoCo, 2B to 9B)". Decoupled DiLoCo's failure and churn runs are 2B to 5B dense plus a 2.8B-active MoE (Tables 2, 3, 10, 11, 15); its 9B result (Table 14) is "no failures"; w1b's gaps say "Decoupled DiLoCo's failure runs are 2B to 5B". Fix: "the most churn evidence (Decoupled DiLoCo: simulated failures at 2B to 5B dense and a 2.8B-active MoE)".

**P5. Line 422, misattributed.** Text: "otherwise peers compare within a tolerance, as Templar's sync score does (w1c S8)". w1c S8 is Gensyn OPEN-1B; the sync score is w1c S4 (Gauntlet, arXiv 2505.21684 §3.2, "2 values per tensor", threshold 3) and w1c Q3b. Confirmed in `sources/w1c/2505.21684` text lines 187 to 196. Fix: "as Templar's sync score does (w1c S4, Q3b; Gauntlet §3.2)".

**P6. Lines 537 and 540, misattributed locators.** (a) Line 537 cites "(2604.21428 v1, Tables 5, 12)" for "downstream parity at 2B (54.4 against 55.1) to 9B"; the 9B pair (67.8 against 68.0) is Table 14. (b) Line 540 cites "(2606.11081 Tables 1b, 3)" for "551M 2-Peer equals DDP at 8 replicas"; DDP 2.64 is in Table 2 (one-step table, 16 replicas), so the claim compares 2-Peer at H = 30 and 8 replicas (Table 3) with DDP from the one-step table at 16 replicas (Table 2): different regimes and replica counts, not a like-for-like result the paper reports. Fix: "(2604.21428 v1, Tables 5, 12, 14)"; for GASLoC: "551M: 2-Peer matches DiLoCo at 8 replicas (2.64, Table 3); DDP's 2.64 (Table 2) comes from a one-step run at 16 replicas, so no direct comparison" with locator "(2606.11081 Tables 1b, 2, 3)".

**P7. Line 554, inference not labelled.** Text: "**What the gate needs**, by the standards the sources use (w1b \"What a Gate N1b would need\"):". w1b titles that list "(inference, not a design)"; the report keeps the label only on one sentence of item 1. Fix: "**What the gate needs** (inference from the standards the sources use; w1b \"What a Gate N1b would need\"):".

**P8. Line 346, outside what was read and wrong as stated.** Text: "packaging and build fixes only since 2025". w2a read only the three newest commits (`commits?per_page=3`, back to 2025-08-03; one of them is "Make imports of hivemind submodules explicit"). The full list since 2025-01-01 (auditor fetch, GitHub API, 2026-10-13 22:53 TST, `audit_sources/a3/hivemind_commits/`) has 16 default-branch commits, including bug fixes such as "Fix RemoteMixtureOfExperts and RemoteSwitchMixtureOfExperts backward() on GPU (#626)" (2025-03-16) and CI and test changes. Fix: "latest release 1.1.12 on 2026-01-03, newest commit 2026-01-04, the three newest commits (2025-08-03 to 2026-01-04) packaging, build and import changes, 70 open issues and 24 open pull requests (search `total_count`)".

**P9. Line 312, generalised beyond what was read.** Text: "Hivemind 1.1.12's PyPI files carry a publish attestation from its `release.yml` workflow (PyPI Integrity API, queried 2026-10-13 17:42); Petals' latest PyPI release has none". Only 2 of Hivemind 1.1.12's 5 files were queried (manylinux x86_64 wheel and sdist; the two macOS wheels and the manylinux aarch64 wheel were not), and only Petals' wheel, not its sdist (`sources/w1d/pypi-api/`). Fix: "Hivemind 1.1.12's manylinux x86_64 wheel and sdist (2 of its 5 files; the rest not queried) carry a publish attestation from its `release.yml` workflow (PyPI Integrity API, queried 2026-10-13 17:42); Petals 2.2.0.post1's wheel has none (sdist not queried)".

**P10. Line 359, wrong as stated.** Text: "(w1d Q10; every setting is a data centre or rented cloud machines)". The table includes Training Transformers Together (line 372), a volunteer run whose hardware and links are not stated in the parts read (w1d P11 itself calls it the nearest precedent "for volunteers on home connections"). Fix: "(w1d Q10; every measured setting is a data centre or rented cloud machines, except Training Transformers Together, a volunteer run whose hardware and links the paper does not state)".

**P11. Q6, inferences not labelled** (each is marked "(inference)" in w2b):
- (a) Line 269: "Agora, whose all-reduce is a Hivemind derivative" (w2b B11: inference from shared code and docstrings in `ar_runner.py`). Fix: "Agora, whose all-reduce appears to derive from Hivemind's (inference from its code)".
- (b) Line 274: "a client lacking an agreed payload errors out and rejoins the next epoch". The error is in code (`train.rs`, `client.rs` line 213); the rejoin is w2b B7's inference. Fix: "errors out of its loop (code) and, by inference, must rejoin at the next epoch".
- (c) Line 276: "**Coordinator loss is handled by restart, never by hand-over:**" (w2b F3 inference over three systems). Fix: "**Coordinator loss is handled by restart, not hand-over, in the three systems read (inference):**".
- (d) Line 278: "**No volunteer system read enforces a minimum holder count without nodes its operator runs**" (w2b F5 inference). Fix: append "(inference over the systems read)".
- (e) Line 284: "PCCL's authors forbid such states as what made fault tolerance tractable (§2.5.3)". §2.5.3 says restricting "the set of legal state transitions" made fault tolerance tractable; it does not mention partially averaged rounds. Abort and restore is §4.1. Fix: "PCCL aborts and restores a failed collective (§4.1) and credits fault tolerance to restricting legal state transitions (§2.5.3); this report reads that as excluding partial rounds (inference)".

**P12. Line 304, source internally inconsistent (low severity; the report matches the line it read).** Text: "organisation-wide rulesets are Team and Enterprise features (w1c S13, S14)". `about-rulesets.md` line 17 supports this ("multiple repositories in an organization for customers on Team and Enterprise plans"), but line 21 of the same page (inside w1c's read range, lines 17 to 41) says organisation-level rulesets are for "organizations on the Enterprise plan". The report should note the inconsistency. Fix: "organisation-wide rulesets need a paid plan (Team and Enterprise per `about-rulesets.md` line 17; Enterprise only per line 21 of the same page)".

**P13. Line 314, wrong detail.** Text: "BOINC's work units are XML templates listing input files with hashes (w2c B1)". In `Job-templates.md` the `<md5_cksum>` element is optional, as w2c B1 records. Fix: "BOINC's work units are XML templates listing input files, optionally with MD5 checksums (w2c B1)".

**P14. Lines 275 and 302, locators outside what the notes record as read (values true in raw).** (a) Line 275, "Hivemind matchmaking 15 s and averaging timeout 60 s": w2b B1 cites `optimizer.py` lines 177 to 179 and 209 to 210, but its read status for `optimizer.py` is lines 30 to 70, 136 to 150, 345 to 410, 510 to 730. (b) Line 302, "Templar ... reads them with `weights_only=True`": w2c T1 cites `comms.py` lines 602 to 605 and 1470, but its read status is lines 280 to 292, 341 to 560, 1287 to 1380, 1412 to 1450, 1631 to 1720. The auditor confirmed both in the clones (hm @4bd43b7 lines 177 to 178 default 15.0 and 60.0, lines 209 to 210; tp @0fefc2a lines 602 to 605 and 1470). Fix: report wording can stay; record the auditor's confirmation, or extend the notes' read status (w2b B1: `optimizer.py` lines 170 to 215; w2c T1: `comms.py` lines 600 to 606, 1465 to 1472), since the report cites the notes as its evidence.

**P15. Line 275, qualifier dropped.** Text: "Two places can wait indefinitely: prime-diloco's non-leaders waiting for a dead leader (...) and NoLoCo's blocking pair exchange (w2b B9, B10)". w2b F2 adds "up to the library default" for NoLoCo, and B10 says the exchange blocks "until torch.distributed's default timeout, which then raises". Only prime-diloco's wait is indefinite. Fix: "One place can wait indefinitely: prime-diloco's non-leaders waiting for a dead leader (...); NoLoCo's blocking pair exchange waits until torch.distributed's default timeout and then raises (w2b B9, B10)".

Observation, not a PROBLEM: P1 in section 6 measures "the address seen from outside" and the NAT class; doing so needs an outside echo or STUN service, which the row does not name. It is a measurement, not live coordination, so it is not a class (c) design; the owner may still want the service named.

## OK checks
| Line | Claim | Source | Class | Where confirmed |
|---|---|---|---|---|
| 269 | Hivemind failed reducer/sender: `partition.py` 128-136, 248-255 | w2b B1; clone hm @4bd43b7 | OK-raw | partition.py lines 128-136 `register_failed_reducer`, 248-255 `on_sender_failed` (inside read range 95-285) |
| 270 | PCCL abort and restore (§4.1 v1) | w2b B8; 2505.14065v1.txt | OK-raw | line 930 "aborted and unwinds and restores the buffer" |
| 270 | prime-diloco retries up to 3 (`diloco.py` 92-121) | w2b B9; clone pd @de5b931 | OK-raw | diloco.py 92-121 retry loop; config.py `retry_all_reduce: int = 3` |
| 271 | Moshpit absent peers keep own values; Psyche batch skip | w2b B3, B7 | OK-raw | moshpit averager.py (read 110-142); Psyche via w1c S1 |
| 273 | Fallback quotes: "Proceeding with local gradients", "using local updates only", "Resorting to calculating pseudo-gradient without reduce", "Skipped averaging" | w2b F1 | OK-raw | hm optimizer.py 634; ms collaboration.py 147; pd diloco.py 124; sw collaborative.py 261 |
| 275 | Hivemind matchmaking 15 s, averaging timeout 60 s | w2b B1 | OK-raw | optimizer.py 177-178 defaults 15.0, 60.0 (value confirmed; lines outside the recorded read range, see P14a) |
| 275 | DeDLOC 5 s stragglers, 30 s give up | w2b B4 | OK-raw | albert/arguments.py 23-28 |
| 275 | Agora 40 s, 30 s / 60 s, 2 of last 3 | w2b B11 | OK-raw | 2607.13332v1.txt l.750, l.669 |
| 275 | Psyche consilience-40b 360 s train, 5 s witness | w2b B7 | OK-raw | config/consilience/state.toml lines 1-9 |
| 275 | prime-diloco 10 s heartbeat eviction | w2b B9 | OK-raw | comms.py 24-26 |
| 275 | prime-diloco TODO comment, `comms.py` 407-414 | w2b B9 | OK-raw | comms.py line 412 inside 405-416 |
| 276 | "Master Crash = End of Run" | w2b B8 | OK-raw | 03_MasterOrchestration.md line 8 |
| 277 | PCCL "effectively lost"; SWARM "on all active nodes" | w2b B8, B6 | OK-raw | MasterOrchestration.md l.41; 2301.11913v2.raw.txt l.963 (App. A) |
| 278 | Agora 4 Pluralis nodes per body stage, 8 and 16 head/tail, §5.1 | w2b B11 | OK-raw | 2607.13332v1.txt l.1841-1843 |
| 279 | Agora 1B, 16 workers/stage, "from roughly 3.04 to 2.97" §6.4 | w2b B11 | OK-raw | l.3655, l.3725 |
| 279 | 669 joins, 607 departures §5.3.2 | w2b B11 | OK-raw | l.2054-2055 |
| 279 | Bamboo 77%, 64 spot, 3.7× (§3, abstract) | w2b B13 | OK-raw | 2204.12013v1.raw.txt l.17, l.31, l.213 |
| 279 | Oobleck up to 29.6× | w2b B14 | OK-raw | 2309.08125v2.raw.txt l.21 |
| 280 | f = 1 analogy, zones | w2b F9 | OK-inference | labelled |
| 283 | Learning@home §3.3 "regularly saves latest expert weights into the same DHT" | w2b B2; w1b S16 | OK-raw | 2002.04013v3.txt l.432 |
| 283 | Hivemind saves to local disk, DHT holds UID records | w2b B1 | OK-raw | checkpoints.py l.62-63; dht_handler.py |
| 285 | SWARM README "not yet added" | w2b B6 | OK-raw | README.md l.8-9 |
| 286 | NoLoCo code seeds pairing with step counter; paper shared seed | w2b B10; w1b S8 | OK-raw | sparse_optimizer_c.py 6-8, 102-109 @a1b4a42; 2506.10911 h.txt l.1043 `seed` |
| 296 | Hub `write` role "create, delete, or rename any repo"; `super_squash_history` "non-revertible" | w1c S13, S15 | OK-raw | organizations-security.md l.19; hf_api.py l.4299 |
| 296 | GitHub tokens scoped to repositories, not paths (parts read) | w1c S14 | OK-raw | pat.md l.51 |
| 297 | Hub `contributor` role writes only repos user created; Templar per-participant buckets; Hivemind signed records | w1c S13, S2, S12 | OK-raw | organizations-security.md l.17; w1c S2 code; crypto.py |
| 299 | Psyche any epoch member can repoint checkpoint | w1c S1 | OK-raw | coordinator.rs 598-600 TODO overwrite; instance_state.rs l.410 SignerNotAClient @0bdb13d |
| 302 | Gensyn "Checkpoint directories are code, not data." | w1c S8 | OK-raw | open-transformers README.md l.114 @d7b7b67 |
| 302 | Hivetrain `torch.load` without `weights_only`; flwr-serverless pickles; Templar `.pt` written, read `weights_only=True` | w2c T7, T2, T1 | OK-raw | averaging_logic.py l.70 @8d5dd20; s3_folder.py l.186, 201 @bbf8a10; comms.py l.1352, 602-605, 1470 @0fefc2a (602-605 and 1470 outside the recorded read range, see P14b) |
| 303 | INTELLECT-2 signed URLs; needs live issuer | w1c S6 | OK-raw | 2505.07291 txt l.600, 636 |
| 304 | GitHub rulesets block force pushes, require signed commits | w1c S14 | OK-raw | rules.md "Require signed commits", "Block force pushes" |
| 310 | BOINC "a separate computer", "disconnected from the network"; key rotation; separate account | w1d T1 | OK-raw | boinc wiki @7e16379 Code-signing.md l.33, 38, 63-79; Security-in-volunteer-computing.md l.65 |
| 311 | "will not know if key material has been revoked"; "not a guarantee that an artifact is secure" | w1d T3 | OK-raw | verify-attestations-offline.md l.54; artifact-attestations.md l.50 |
| 312 | Psyche pins image by sha256 digest; Templar `git clone` | w1d T5 | OK-raw | rm_coordinator_client.rs l.196-201; templar miner.md l.98 |
| 313 | Reproducible builds: bit-for-bit identical from same source, environment, instructions | w1d T6 | OK-raw | definition.txt l.16, 31 |
| 314 | safetensors header 100 MB; NaN/Inf not checked; torch.load `weights_only=True` since 2.6, "narrows"; `.py` configs | w1d T7, S2 | OK-raw | safetensors README l.92, 172; serialization.md l.258, 271; gcs-checkpoints.md l.204-209 |
| 315 | R2 code-signing key matches BOINC; principle 2 support | w1d Q8 inference | OK-inference | labelled "Inference (w1d)" |
| 363 | SparseLoCo Table 1: 17.21 MB vs 512.40 MB; loss 2.70 / 2.76 / 2.69; 1 bit 4.79 (Table 7) | w1d P3 | OK-raw | 2508.15706 v3_html.txt (17.21 l.219; 512.40, 4.79 present) |
| 364 | Decoupled DiLoCo Table 10: int4 +0.09%, 2 bits +32%, 1 bit +83% | w1b S1 | OK-raw | 2604.21428 html.txt "Relative val loss: +0.09% +32% +83%" |
| 365 | Streaming DiLoCo Table 1: 1.10 TB vs 441 TB over 25B tokens; FP4 E3M0; "no sign of performance regression" (§2.4) | w1d P5 | OK-raw | 2501.18512 paper.txt l.469-473, 314-318 |
| 366 | MuLoCo §6.3: 416M, K = 8, H = 30; 8/4/2 bits; 4-bit lossless; 2-bit statistical fine | w1d P6 | OK-raw | 2505.23725 paper.txt l.648, 878-899 |
| 367 | OpenDiLoCo: FP16, 300 s, 127 to 935 Mbit/s, "no noticeable impact" | w1d P7 | OK-raw | 2407.07852 paper.txt l.280-283, 352, 385 |
| 368 | INTELLECT-1: int8 4×; median 103 s to 469 s | w1d P8 | OK-raw | 2412.01152 paper.txt l.239, 520-534 |
| 369 | DiLoCo Table 6: 25/50/75% pruned, −0.06% / +0.39% / +1.66% | w1d P9 | OK-raw | 2311.08105 paper.txt l.800-806 (percentages printed in the table) |
| 370 | DeMo Table 1: 300M 7.49 MB at k = 8 vs 636.9 MB | w1d P1 | OK-raw | 2411.19870 v2_html.txt l.253, 289, 297 |
| 371 | DisTrO: 86.8 MB vs 74.4 GB (857×); "the 1.2B model seems to be the smallest size"; 300M "do not converge as well" | w1d P2 | OK-raw | distro/report.txt l.144-145, 177-178, fn 7 l.215 |
| 372 | TTT §3.3: 8-bit large tensors, 16-bit others | w1d P11 | OK-raw | 2207.03481 paper.txt l.200-201 |
| 373 | Covenant-72B: "more than 146×"; 70 s per round | w1d P4 | OK-raw | 2603.08163 paper.txt l.228, 374 |
| 375 | Home speeds: TTT 10 to 100 Mbit/s (§2); DisTrO assumed 100 down, 10 up (§3.1) | w1d Q10 | OK-raw | 2207.03481 l.112; distro report l.168-169 |
| 376 | Update sizes and upload times at 20 Mbit/s; SparseLoCo scaled ≈10 MB ≈4 s | w1d Q10 | OK-inference | labelled; recomputed: 0.2-0.6 / 0.1-0.3 / 0.05-0.15 GB; 240/120/60 s; 17.21×300/512 = 10.08 MB, 4.0 s |
| 378 | DisTrO README "seed research/idea"; INTELLECT-1 averages 2 and 10 min vs medians 103 s, 469 s | w1d P2, P8 | OK-raw | distro README l.6; 2412.01152 l.479, 533-534 |
| 319-341 | Q9 table: licence, last commit, latest release for all 19 rows | w2a blocks 1-15, summary table | OK-raw | saved API JSON `sources/w2a/api/*/{repo,commits,release_latest}.json` (script `scripts_a3/api_summary.py`); every licence, `commit.committer.date` and `releases/latest` value matches; js-libp2p npm 3.3.12 per w2a 6 (npm 18:08:56) |
| 323-340 | Q9 runtime, Windows, docs cells (Hivemind `>=3.9`, WSL "experimental", `setup.py` platform list; Psyche "only runs on modern Linux distributions", linux-x64 run-manager only; Rust 77.7%; RL Swarm "not very well tested", "no official swarms running right now"; prime-diloco `torch==2.5.1`; iroh-ffi Alpha, `win_amd64`; go-libp2p Go 1.26, OS matrix incl. windows; rust-libp2p `cargo check` on windows-latest, tests ubuntu only; py-libp2p windows job without `interop`, Beta; js-libp2p windows-latest; iroh `build_and_test_windows`, Windows relay zip; PCCL Windows wheels only as release assets, no CUDA, PyPI linux and macOS only; Flower ubuntu-only CI, macOS and Linux classifiers; BOINC windows.yml x64 and arm64; Templar CI ubuntu only; Petals "Windows + WSL"; Node0 and Agora Python 3.11 only, WSL2) | w2a 1 to 15 | OK-raw | raw README, pyproject, setup.py, join-run.md and every `.github__workflows__*` file under `sources/w2a/raw/`; `api/*/release_latest.json` assets (iroh, PCCL); `pkg/pypi_*.json` classifiers and filenames; languages.json |
| 335, 348 | Templar newest commit changes a test file only; dormant notice added 2026-03-31 by `142666f0dd91` | w2a 11 | OK-raw | w2a commit-diff record (18:09:55 TST); auditor re-fetch of commit 0fefc2a at 2026-10-13 22:53 TST (`audit_sources/a3/templar_commit/`): only `tests/conftest.py` modified |
| 343 | moshpit-sgd, DeDLOC, swarm, noloco, HALoS licence and `pushed_at` (17:36 TST) | w1b S3, S4, S5, S8, S12 | OK-raw | notes' recorded API values, query time 14:36 UTC |
| 343 | flwr-serverless, Hivetrain, HF²L, STUNMESH-go values with query times | w2c T2, T7, T8, N1 | OK-raw | notes' recorded API values, 18:29 to 18:35 TST |
| 346 | Hivemind 1.1.12 on 2026-01-03, newest commit 2026-01-04, 70 issues and 24 PRs (search `total_count`) | w2a 1 | OK-raw | search_open_issues.json, search_open_prs.json |
| 347 | prime-diloco no default-branch commit in 18 months; OpenDiLoCo "is no longer maintained" | w2a 9 | OK-raw | commits.json 2025-04-10; OpenDiloco README line 5 |
| 349 | Psyche redirects to nousnet | w1c S1, w2a 8 | OK-raw | notes' API record 17:19 and 17:55:22 TST |
| 351 | prime-diloco master store on rank 0; INTELLECT-2 "The orchestrator and discovery service are currently centralized" (§2.4.3) | w1c S5, S6 | OK-raw | 2505.07291 paper.txt lines 642 to 644 (§2.4.3) |
| 353 | Inference for D35 | w2a | OK-inference | labelled |
| 355 | Agora 40 days (abstract) against "500B tokens over 7 weeks" (README) | w1c S11, w2a 13 | OK-raw | 2607.13332 paper.txt line 24; agora README line 25 |
| 386-511 | Section 4 header and every subsection carry "(inference)"; 4.7 "(inference; the owner accepts or rejects it)" | none | OK-inference | lines 386, 388, 401, 458, 470, 474, 488, 496, 511 |
| 393 | Rotating holder hand-over 0.8 to 2.4 GB | w1b S1, F2 | OK-inference | 100M to 300M x 4 bytes x 2 copies = 0.8 to 2.4 GB |
| 394 | Decoupled DiLoCo K = 1 with grace matched K = 8 (Table 5); Psyche and Templar close rounds on timers; DeDLOC and Moshpit through real churn | w1b S1, S3, S4; w2b B7; w2c T1 | OK-raw | 2604.21428 html.txt Table 5 (55.3 against 54.4); state.toml `max_round_train_time`; Templar `time_window_delta_seconds` per w2c T1 |
| 395-397 | Gossip +1.29% (1.5B, 8 workers); GASLoC +0.6% to +3.7% (134M); eager +0.75%; naive +12.7% (+2.2%) | w1b S9, S10, S13 | OK-inference | section-4 inference; recomputed 1.29; 0.61 to 3.68; 0.75; 12.73 and 2.25 |
| 409-411 | Conditional commit `parent_commit`; manifest last; offline signer | w1c S15; w1d S2, T1 | OK-raw | hf_api.py lines 5033 to 5039; gcs-checkpoints.md lines 204 to 209; Code-signing.md |
| 420 | Sharded safetensors with an index, as Petals reads | w1d S5 | OK-raw | notes S5 (`from_pretrained.py`) |
| 422 | Stage 0's D11 rule; coordinator already implements merging and outer optimizer (ROADMAP §1) | SRS D11; ROADMAP §1 | OK-raw | SRS.md lines 63, 192; ROADMAP.md lines 27 to 29 |
| 425-427 | flwr-serverless synchronous wait; Decoupled DiLoCo learners overwrite their fragment; Hivemind donors; NoLoCo fixed world | w2c T2; w1b S1; w2b B1, B10 | OK-raw | sync_federated_node.py lines 166 to 184; w2b B1, B10 code |
| 431-433 | Rolling gives exactly 2 holders (D37); Bamboo zones; quorum of 1 per fragment; no source measures which is better | ROADMAP principle 7; w2b B13, F9; w1b S1 | OK-raw | ROADMAP.md line 55; 2204.12013 raw lines 40, 368 |
| 441 | ROADMAP risk table asks for more than one host | ROADMAP §7 | OK-raw | ROADMAP.md risk row "More than one host" |
| 445 | `huggingface_hub` Apache-2.0, `pushed_at` 2026-10-13T13:54:35Z queried 17:42 TST; safetensors Apache-2.0; ed25519 (Psyche); RSA (BOINC) | w1c S15, S1; w1d T7, T1 | OK-raw | notes' dated API record; Code-signing.md "RSA key pair" |
| 448 | Class (c) or borderline elements flagged, none recommended: bucket event stream (borderline), R2 (owner-paid) | none | OK-inference | flagged, not recommended |
| 451-453 | "a few thousand commits"; N − 1 downloads, 2.4 GB; 240 s per 0.6 GB at 20 Mbit/s; eager +0.75% | w1d H1; w1a Q2; w1b S13 | OK-raw and OK-inference | storage-limits.md line 107; 4 x 0.6 = 2.4 GB; 4,800 Mbit / 20 = 240 s |
| 460-468 | Static relay with our peer IDs and raised limits; BEP 5 `nodes`; Hivemind minimum 2 members; iroh Windows CI, relay binary, Alpha wheels; Hivemind 2023 fork; pnet TCP only; py-libp2p NAT traversal unconfirmed | w1a S4, S9, S10, Q2; w2a 1, 3, 5, 7; w2b B1 | OK-raw | notes as cited; w2a raw CI files |
| 467 | Library defaults (n0 relays and discovery, IPFS bootstrap) are (c) and "must be replaced" | w1a S4, S9 | OK-inference | class (c) flagged, not recommended |
| 490-494 | Hub `contributor` role; `write` role "create, delete, or rename any repo"; ledger is (c), flagged for Phase 6, not recommended; every exemplar had a coordinator | w1c S13, Q7 | OK-raw | organizations-security.md lines 17, 19 |
| 498-507 | Section 4.6 table (Hivemind fork go-libp2p v0.32.1 against v0.50.0; Psyche last commit 2026-03-20; prime-diloco 2025-04-10; Templar dormant; PCCL one release, no Windows CUDA build), dated 17:55 to 18:21 TST | w2a 1, 8 to 11; w2b B8 | OK-raw | API JSON as in the Q9 rows |
| 525 | GitHub "500 content-creating requests per hour" | w1d H7 | OK-raw | reusable_secondary-rate-limit-rest-graphql.md line 9 ("500 content-generating requests per hour") |
| 536 | HALoS +18.6% / +24.8% / +30.9% more tokens | w1b S12 | OK-raw (derived; label: P1) | 2506.04531 h.txt lines 428 to 448: 14.0/11.8, 16.1/12.9, 16.1/12.3 |
| 537 | Decoupled DiLoCo 55.3 against 54.4; 2B 54.4 against 55.1 | w1b S1 | OK-raw | html.txt Table 5; Table 12 text average 55.1 / 54.4 |
| 538 | HeLoCo −1.8% to +15.4% | w1b S11 | OK-raw (derived; label: P1) | h.txt Table 1: 6.50 and 7.64 against 6.62 gives −1.81% and +15.41% |
| 539 | Factored Gossip +1.29%; +3.49%; +8.99% at 16 workers | w1b S9 | OK-raw (derived; label: P1) | h.txt 17.53, 18.65, 19.37, 17.22, 22.24 |
| 540 | GASLoC +0.61% to +2.55% / +1.21% to +3.68% at 134M | w1b S10 | OK-raw (derived; label: P1) | h.txt Table 1b |
| 541 | NoLoCo −1.45% to +0.42%; +0.83% to +7.68% against FSDP; +6.6% without routing | w1b S8, S9 | OK-raw (derived; label: P1) | paper.txt Table 1, all 16 cells recomputed (14 better); FG h.txt line 1743 (22.65) |
| 542 | Eager +0.75% (2 replicas); +0.40% to +0.75% at 1B | w1b S13 | OK-raw (derived; label: P1) | h.txt Tables 1, 2 |
| 543 | Moshpit "same within the margin of error" | w1b S3 | OK-raw | 2103.03239 h.txt line 641 |
| 544 | FoMoE O_e = 2: +1.6% / +2.9% / +2.1% | w1b S17; Stage 0 notes 04a, 04b, 06 | OK-raw (derived; label: P1) | 04a lines 261 to 263, 275; 06 lines 152 to 154; recomputed 1.61 / 2.90 / 2.09 |
| 547 | Naive asynchronous DiLoCo worse at every size; HeLoCo "diverges across all configurations"; naive delay +12.7% | w1b S2, S11, S13 | OK-raw | 2401.09135 h.txt Table 3; 2606.00271 h.txt line 414 |
| 550 | Every asynchronous result near 100M to 300M is continued pretraining, a server-hierarchy reimplementation or gossip at 8 workers or more | w1b gate item 8 | OK-raw | w1b line 478 |
| 552 | Candidate for Gate N1b | w1b | OK-inference | labelled |
| 555-557 | Seeds 7, 11, 19; HeLoCo row (1,6,6,6,6): 5.43% worse at equal tokens, 5.80% better at equal wall-clock; event tapes App. E.1 | w1b gate items 1 to 3 | OK-raw | 2606.00271 h.txt Table 1 row (1,6,6,6,6): ΔSN −5.43, TΔSN 5.80 |
| 555 | "equal compute" must say steps run or steps merged | none | OK-inference | labelled |
| 567 | Prototype durations are the report's estimates | none | OK-inference | stated at line 567 above the table |
| 571 | ProbeLab classifies NAT mapping and filtering | w1a S14 | OK-raw | notes S14 (RFC 4787 classes) |
| 574 | Storage Buckets `uploadedAt` field | w2c T9 | OK-raw | notes T9 (OpenAPI spec) |
| 575 | "excessive bulk activity" | w1d H5 | OK-raw | hf-pages/content-policy.txt line 91 |
| 577 | Phase 1 has no GPU budget | ROADMAP Phase 1 | OK-raw | ROADMAP.md line 68 "no GPU" |
