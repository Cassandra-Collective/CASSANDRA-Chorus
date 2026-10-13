# Re-audit C: unverified items stay in section 7

| | |
|---|---|
| Auditor | independent second check, 2026-10-13 (did not read `audit-4-unverified.md` or `fix-log.md`) |
| Report | `docs/research/2026-10-13-system-study-report.md`, 721 lines; section 7 starts at line 583 |
| Scope | lines 1 to 582 (header, sections 1 to 6); section 7 checked for completeness and accuracy |
| Method | all seven notes files read in full; every "Could not verify" list plus body markers (not read, abstract only, figure only, vendor claim, not confirmed, garbled, not checked) compiled; scope searched by name, number and phrase with a script (`audit/rc_grep.py`); every arXiv ID and file locator in scope checked against the notes (`audit/rc_conv.py`); raw sources in the scratchpad consulted where a note was ambiguous |
| Status | COMPLETE |

## 1. Compiled unverified items

Counts: "Could not verify" (CNV) entries, plus other entries marked unverified in the note body or gaps.

| Notes file | CNV | Body / gaps | Closed later by another note |
|---|---|---|---|
| w1a | 5 | 8 | none of the CNV items; iroh bindings (S9 "not checked") answered by w2a 7 (API) |
| w1b | 11 | 8 | NoLoCo pairing (w2b B10); Hivemind averager = Moshpit (w2b B1); SWARM App. A partly (w2b B6); DeDLOC I.5 auth (w1d P10 security appendix) |
| w1c | 14 | 10 | PCCL master failure (w2b B8); Agora §6.4 (w2b B11); Agora §5.7.1 NOT closed (see S7-1); Psyche relay hostnames read in w1a S15 (operator still open) |
| w1d | 12 | 12 | none |
| w2a | 13 | 7 | PCCL NAT and master failover (w2b B8) |
| w2b | 12 | 6 | none |
| w2c | 11 | 12 | none |
| **Total** | **78** | **63** | |

### w1a (CNV 5; body 8)
- A1 Halkes/Pouwelse, Guha/Francis, Seemann et al. numbers cited by Trautwein (CNV)
- A2 iroh "roughly 9 out of 10" vendor claim (CNV)
- A3 operator of Psyche's relay hosts (CNV)
- A4 py-libp2p "Done" claims for relay v2, AutoNAT, hole punching (CNV)
- A5 rust-libp2p pnet over QUIC (CNV)
- A6 iroh relay in `--dev` mode: hole punching (gap 7)
- A7 rust-libp2p routing-table persistence (gap 8, not checked)
- A8 go-libp2p-kad-dht issue #387 not read (gap 8)
- A9 arXiv 2510.27500 abstract only
- A10 ProbeLab sub-reports not read
- A11 iroh `add-a-relay.md`, `dedicated-infrastructure.md` not read
- A12 Trautwein port-mapping effect: figure only
- A13 hairpin: no newer figure read

### w1b (CNV 11; body 8)
- B1 Decoupled DiLoCo Table 14 2B column; B2 Table 15 reference; B3 Table 5 TPU generations; B4 HALoS Table 1 reference and 70M/410M protocol; B5 HeLoCo abstract figures; B6 venues (D-PSGD, AD-PSGD, HALoS, Factored Gossip); B7 NoLoCo pairing (closed, w2b B10); B8 Factored Gossip matching; B9 Momentum Look-Ahead not read; B10 Hivemind averager = Moshpit (closed, w2b B1); B11 SWARM App. A, AD-PSGD App. A, D-PSGD NLP supplement
- Body: B12 figure-only quality claims (Moshpit, DeDLOC, SWARM, Async Local-SGD wall-clock, GASLoC Figs 3/4, NoLoCo Fig 7, Streaming DiLoCo Fig 10, AD-PSGD Fig 6, L@home Fig 5, Decoupled DiLoCo 3.8B MoE); B13 FoMoE not re-read (Stage 0 notes); B14 DiPaCo not re-read; B15 "Not Every Sync Is Safe" abstract only, PALSGD abstract plus grep, EDiT tables garbled; B16 asyncdiloco and Factored Gossip code not read; B17 ring all-reduce cost "my statement, not from a source"; B18 DeDLOC I.5 not read; B19 unopened leads (SeedFlood, Epidemic Learning, SPARTA, GWTF, 1907.11612)

### w1c (CNV 14; body 10)
- C1 Psyche `update` while active; C2 Psyche verification after 2026-03-20; C3 Psyche P2P checkpoint hash check; C4 Psyche relay hostnames and operator; C5 `god_store` host; C6 Tailscale architecture, so its (c) class; C7 Yuma consensus, highest-staked validator; C8 Templar bitwise identity; C9 RepOp licence; C10 HF fine-grained token per repository; C11 GitHub per-path write limits; C12 TOPLOC not read; C13 Agora §5.7.2 divergence and §5.7.1, §6.4 failure results; C14 `prior-work.md` Psyche entry
- Body: C15 server-side enforcement of `parent_commit` (S15 Fit: "was not read"); C16 SAPO abstract only; C17 RL Swarm README grep only; C18 Verde abstract, §1, start of §2 only; C19 PCCL code not read, master failure not described (closed, w2b B8); C20 Gauntlet Algorithm 1 garbled; C21 INTELLECT-2 figures garbled; C22 Gensyn REE not read; C23 IOTA not re-read; C24 prime-diloco 6 s vs 10 s ("presumably")

### w1d (CNV 12; body 12)
- D1 Hub commit limits; D2 "Best-effort" and bucket allowance; D3 BEP 19 web seeds on HF or GitHub; D4 R2 checkout card; D5 GitHub release downloads vs REST limits; D6 `cosign sign-blob --key` and Rekor; D7 pip and PEP 740; D8 DisTrO algorithm; D9 Psyche run-manager image signature; D10 Covenant-72B joiners; D11 SparseLoCo App. J and Table 5 (garbled); D12 prime-diloco = INTELLECT-1 framework
- Body: D13 Xet dedup on training updates (not measured); D14 multi-file Hub commit visibility; D15 figure-only (DeMo Figs 5/6, MuLoCo, OpenDiLoCo FP16, Streaming DiLoCo Fig 11); D16 DisTrO Tables 1/2 garbled (not used), Table 3 garbled (row mapping recovered from §3's 857×, used); D17 Hivemind `state_averager.py` not read, Templar `validator.md` grep only; D18 Covenant validator operator not stated; D19 INTELLECT-1 int8 quality: no ablation; D20 reproducible builds "not searched for beyond the files listed"; D21 HF S3 bucket API page not read; D22 pinning services' terms not read; D23 Prime client distribution not checked; D24 DiLoCoX metadata only, INTELLECT-3 not read

### w2a (CNV 13; body 7)
- E1 Hivemind per-expert averager; E2 PCCL `peer_group` for overlapping holder groups; E3 PCCL NAT and master failover (closed, w2b B8); E4 py-libp2p NAT on Windows and interop; E5 iroh-ffi custom relays (claim) and `--dev`; E6 Psyche current status; E7 prime-diloco 2026 pushes to other branches; E8 issue-count discrepancies (rust-libp2p, Node0); E9 RL Swarm community swarms; E10 Flower native Windows; E11 BOINC Windows client; E12 Python bindings for go/rust-libp2p; E13 `agora` on PyPI
- Body: E14 **js-libp2p mechanisms not read** ("as block 3 in kind (inference)"; listed again under "Not covered"); E15 rust pnet over QUIC (repeat of A5); E16 Hivemind synchronous mode as one group (not tested); E17 Psyche `python/` and iroh blobs not read; E18 docs not fetched (Hivemind site, docs.psyche.network, docs.gensyn.ai, Agora/Node0/PCCL `docs/`); E19 prime-rl lead only; E20 torchft, Hyperswarm leads only

### w2b (CNV 12; body 6)
- F1 Petals threshold 20% vs ~33%; F2 SWARM Table 5 row assignment; F3 SWARM §4.3/§4.4 rebalancing code; F4 Psyche live Consilience settings; F5 Hivemind `k_min` counting; F6 `_load_state_from_peers` timeout; F7 L@home older code; F8 NoLoCo default timeout; F9 Agora backward pinning (grep only); F10 PCCL `test_peer_groups.cpp`; F11 Bamboo 2.4× vs 3.6×; F12 Agora 85% threshold, one run
- Body: F13 figure-only (Petals App. E, SWARM Fig 6, L@home Figs 5/6, Agora Fig 15d); F14 Bamboo §7 garbled, Petals App. F; F15 Node0 code not read, Agora code grep only; F16 SWARM `collaborative.py` semantics "not re-read line by line"; F17 Templar/Covenant churn handling, GWTF, Varuna, DiLoCoX not read; F18 Decoupled DiLoCo §3.2 symbols lost

### w2c (CNV 11; body 12)
- G1 LambdaML and FedLess venues; G2 LambdaML Table 6 garbled; G3 FedLess Fig. 12; G4 STUNMESH-go in practice, docs site, FOSDEM talk, static-host backend; G5 HF²L workflow doc and Exchange service; G6 Hivetrain operating history; G7 Hub `uploadedAt` server-assigned; G8 IPFS/blockchain FL papers (search only); G9 Tailscale "few seconds" author claim; G10 Hyperswarm not read; G11 Flower "Fault Tolerant FedAvg"
- Body: G12 Hivetrain `send_interval` unit not confirmed; G13 BOINC "hundreds of jobs per second" cites [17] (not read), J. Grid Computing not checked; G14 Flower §5.3 dataset not confirmed; G15 Asyn2F grep only; G16 FedLess partly garbled, §V not read; G17 Plexus §4 not read beyond abstract numbers; G18 Templar `hparams.json` not necessarily Covenant-72B's config; G19 HF²L code not read; G20 serverless-FL literature beyond four papers (gap 6 "unverified"); G21 Tailscale blog rest not read; G22 STUNMESH exec plugin with a file host "not tested"; G23 STUNMESH punch mechanism is inference

## 2. Hits in scope, classified

Items with no hit in scope (not used): A1, A2, A9, A11, B1 (2B misprint avoided), B2, B5 (abstract figures), B6 (except two verified venues), B8, B9, B11, B14, B15, B16, B19, C9, C12, C14, C18, C20 to C23, D5, D7, D10, D11, D17, D18, D21, D23, D24, E7, E12, E13, E17 to E20, F1, F2, F5, F6, F9, F11, F12, F13 to F18, G1 to G3, G5, G6 (no history claimed), G8, G9, G10, G11 to G16, G19 to G23.

| Line | Item | Text (short) | Class |
|---|---|---|---|
| 20 | C15 | "conditional ('compare-and-swap') commit log ... (inference, untested; w1c S15)" | OK-pointer (labelled untested; caveat and section 7 pointer at 491) |
| 26 | C2/E6 | Psyche "no default-branch commit since 2026-03-20 (status not confirmed; see section 7)" | OK-pointer |
| 36 | C15 | prototypes include "concurrent conditional commits" | OK-pointer (prototype P4) |
| 51 | E1 | Hivemind R6 "per-expert groups untested (w2a 1, D; section 7)" | OK-pointer |
| 54 | A4, A5, E14 | libp2p row "(go; also rust, py, js)"; ratings cite w1a S3, S4, S5 only | Advisory (see V1) |
| 56 | A3/C4 | Psyche "defaults are project relays and n0 discovery" | OK-verified-elsewhere (defaults and hostnames read in w1a S15 code; operator not claimed) |
| 58 | D12 | "(INTELLECT-1's framework by its own description; section 7)" | OK-pointer |
| 58 | C6 | "Tailscale, (c) by inference only (section 7)" | OK-pointer |
| 59 | E3/C19 | PCCL "'Master Crash = End of Run'"; "open ports needed; no relays" | OK-verified-elsewhere (w2b B8) |
| 59 | E2/F10 | "peer groups per expert unconfirmed (section 7)" | OK-pointer |
| 60 | C16 | "(w1c S9, SAPO abstract only)" | OK-abstract-only |
| 66 | B18 | "DeDLOC used an allowlist authorization server (w1d P10, P)" | OK-verified-elsewhere (w1d P10 read the security appendix) |
| 69, 286, 427, 430 | B7 | NoLoCo code: fixed world; step-counter seed; pairing over a fixed world | OK-verified-elsewhere (w2b B10) |
| 71, 544 | B13 | FoMoE "central coordinator to manage initialization, broadcasting, and aggregation" (§3.1; via note 04a) | OK-verified-elsewhere (Stage 0 note 04a full read; exact wording not in 04a, but confirmed in raw text `audit_sources/a2/fomoe/paper_v2.txt` line 226, §3.1) |
| 91 | A8 | "a TODO cites issue #387" | OK-verified (code TODO read; the issue itself is not cited for content) |
| 105 | A7 | "routing-table persistence in rust-libp2p (not checked; see section 7)" | OK-pointer |
| 113 | B6 | Trautwein "IMC '26" | OK-verified (arXiv comment and ACM block, w1a S1) |
| 114 | A10 | ProbeLab numbers | OK-verified (blog and report sections read; sub-reports not used) |
| 115 | A13 | Ford hairpin 24% / 13% | OK-verified (Table 1); no newer figure claimed |
| 117 | B6 | Richter "IMC 2016" | OK-verified (paper header) |
| 121 | A6 | iroh self-hosted relay "uses a DNS name and TLS on ports 80 and 443" | OK-verified (docs read); `--dev` question not claimed here |
| 122 | A3/C4 | Psyche "project-named relays ... not volunteers' machines" | OK-verified-elsewhere (hostnames fixed in `lib.rs` 105 to 106, w1a S15); operator not claimed |
| 123 | A12 | "UPnP or PMP ... or IPv6 ... neither is measured for home routers today" | OK-search-finding |
| 133 | G4, G22 | STUNMESH-go "reports no success rates"; "For best results" | OK-search-finding; quote confirmed in raw README line 22 |
| 142 | A6 | "whether iroh punches holes when its relay runs without a DNS name and certificate (... not confirmed, see section 7)" | OK-pointer |
| 159 | C1 | Psyche run configuration "changeable only by `main_authority`" | OK-verified (code: signer check); refusal-while-active not claimed |
| 167 | C15 | Q3 table quotes client docstring "will fail if `revision` does not point to `parent_commit`" | OK-verified (docstring) with loss column caveat |
| 177 | G7 | "whether the server assigns it is not confirmed (see section 7)" | OK-pointer |
| 183 | w1c gap | "No system was found ... negative result over the sources read" | OK-search-finding |
| 209 | B4 | HALoS "70M and 410M columns' protocol is not confirmed (section 7)"; "not used here (section 7)" | OK-pointer |
| 210 | B3 | Decoupled DiLoCo "heterogeneous TPUs" (no generation named) | OK (item avoided) |
| 210, 537 | B1 | 2B parity "54.4 against 55.1 (Table 12)" | OK (Table 14's misprinted 2B averages not used) |
| 217, 543 | B12 | Moshpit/DeDLOC quotes "(figures only)" / "(figure only)" | OK-abstract-only (figure-only flagged) |
| 222 | B17 | "w1b's statement of the standard ring cost" | OK (labelled as w1b's own statement) |
| 224 | w1b F6 | "**Not found in this search:**" async holder-group averaging | OK-search-finding |
| 227, 536 | B4 | HALoS "protocol is not confirmed, see section 7" | OK-pointer |
| 240 | C3 | Psyche joiners fetch layer by layer | OK (mechanism documented; hash check not claimed) |
| 243 | D3 | "Whether Hub or GitHub URLs work as web seeds is not confirmed (section 7)" | OK-pointer |
| 249 | D1 | "commit limits exist but are not documented" | OK-search-finding (documented absence) |
| 250, 257 | D2 | bucket "free allowance not quantified" | OK-pointer (section 7 line 632) |
| 253, 448, 525 | D4 | R2 card "not confirmed, section 7"; "possibly paid; section 7" | OK-pointer |
| 254 | D3 | "BEP 19 web seeds can be (b)" | OK (class of a generic web seed; host suitability flagged at 243) |
| 255 | D22 | "pinning services' own terms (not read)" | OK (states not read) |
| 261 | D1, D2, D3, D13, D14 | Q5 Unknown list "See section 7." | OK-pointer |
| 269 | F15 | Agora all-reduce "appears to derive from Hivemind's (inference from its code)" | OK (labelled inference; grep of `ar_runner.py`) |
| 275 | F4 | Psyche config "whether the live run used them is unconfirmed, section 7" | OK-pointer |
| 275 | F8 | NoLoCo timeout "(value not checked; see section 7)" | OK-pointer |
| 270, 276, 277, 506 | E3/C19 | PCCL abort and restore; "Master Crash = End of Run"; "effectively lost" | OK-verified-elsewhere (w2b B8) |
| 278, 279 | C13 | Agora floor (§5.1); §6.4 ablation "from roughly 3.04 to 2.97" | OK-verified-elsewhere (w2b B11 read §5.1, §6.4) |
| 283 | F7 | Learning@home paper vs code | OK (stated as a disagreement; report follows the code read) |
| 285 | F3 | SWARM README "not yet added" | OK (disagreement) |
| 296 | C11 | "GitHub tokens are scoped to repositories, not paths, in the parts read" | OK-search-finding |
| 306, 491 | C10, C11 | "Whether a Hub fine-grained token can limit writes to one repository; GitHub per-path write limits (section 7)" | OK-pointer |
| 311 | D6 | keyless signatures "logged in Rekor" | OK (keyless path read; key-based upload not claimed) |
| 312 | D9 | "Whether Psyche's run-manager verifies an image signature is not confirmed (section 7)" | OK-pointer |
| 312 | T4 scope | "(2 of its 5 files; the rest not queried)", "(sdist not queried)" | OK-search-finding (query scope stated; confirmed against raw PyPI JSON) |
| 313 | D20 | "no candidate's documentation read claims them" | OK-search-finding |
| 327 | A5/E15 | rust-libp2p "Provides toward Chorus: as go-libp2p" (go cell: "pnet over TCP or WebSocket (inference)") | **PROBLEM P2** (minor) |
| 328 | A4/E4 | py-libp2p "as go-libp2p, by its own claims (section 7)" | OK-pointer |
| 329 | E14 | js-libp2p "Provides toward Chorus: as go-libp2p" | **PROBLEM P1** |
| 331 | E5 | iroh-ffi "Python access to iroh, trailing the core" | OK (custom-relay claim not used) |
| 335 to 341 | E9, E10, E11 | RL Swarm README quote; Flower classifiers; BOINC "Windows builds in CI" | OK (no native-support or community-swarm claim) |
| 346 | E8 | Hivemind "70 open issues and 24 open pull requests" | OK (Hivemind counts agree; discrepancies concern rust-libp2p and Node0) |
| 347 | D12 | "(section 7 for the identity caveat)" | OK-pointer |
| 351 | C5 | "master key-value store hosted by the rank-0 process" | OK-verified (global `TCPStore` on rank 0; `god_store` not claimed) |
| 355 | w1c/w2a | Agora run length "Unresolved; neither figure is used" | OK-pointer (section 7 line 686) |
| 366, 367 | D15 | MuLoCo "(figures only)"; OpenDiLoCo "(figure only)" | OK-abstract-only |
| 368 | D19 | INTELLECT-1 "no ablation found" | OK-search-finding |
| 371 | D8, D16 | DisTrO "not described"; 86.8 MB vs 74.4 GB | OK (Table 3 garbled but mapping recovered from §3's stated 857×, recorded in w1d P2; not a declined value) |
| 378 | D8 | DisTrO and DeMo "may not be the same algorithm" | OK (hedged) |
| 409, 440 | C15 | Closer: "other attempts fail"; "the next peer's conditional commit succeeds (w1c S15)" | Advisory (see V2): design premise; server enforcement unconfirmed, caveat only at 491 and 520 |
| 462, 463, 481 | E16 | Option B synchronous mode as one group | OK (section 4 is declared inference) |
| 468 | A4/E4 | "py-libp2p's NAT traversal is unconfirmed" | OK-pointer (section 7 lines 597, 649) |
| 491 | C15 | "provided the Hub enforces `parent_commit` on the server, which is not confirmed (section 7; prototype P4)" | OK-pointer |
| 520, 574 | C15, G7 | P4 dependency and test design | OK-pointer |
| 538 | w1b S11 | HeLoCo "far from converged (inference)" | OK |
| 547 | w1b S11 | HeLoCo "diverges across all configurations" | OK-verified (§4.2 text) |

**Counts by class (77 table rows; a row may group several lines of one item; counted by `audit/rc_count.py`):** OK-pointer 26; OK-verified-elsewhere 8; OK-abstract-only 3; OK-search-finding 9; other OK (verified at source, item avoided, labelled inference or hedged) 27; Advisory 2; **PROBLEM 2**.

## 3. Converse check

- All 22 arXiv IDs cited in scope have a source block in the notes (script `rc_conv.py`).
- All 21 file locators in scope (`dht.go`, `hf_api.py`, `partition.py`, `hparams.json`, `about-rulesets.md`, etc.) appear in the notes.
- Named non-arXiv sources (Richter et al., RFC 7021, BEP 5, ProbeLab, BOINC wiki, Flower docs, Hub docs, GitHub docs, R2 docs, Sigstore, PyPI Integrity API, safetensors, PyTorch, reproducible-builds.org, DisTrO report, STUNMESH-go, HyperDHT, Hivetrain, HF²L, flwr-serverless, Gauntlet, Bamboo, Oobleck, Stage 0 notes 01, 04a, 04b, 06): each has a recorded reading.
- Three details in scope are not written in the notes but are confirmed at the raw source (no rule break; noted for the record):
  - line 304, `about-rulesets.md` "Enterprise only per line 21": w1c S14 records lines 17 to 41 read (grep) but only line 17's content; line 21 confirmed in `sources/w1c/docs/ghdocs/about-rulesets.md`.
  - line 312, Hivemind "2 of its 5 files", Petals "sdist not queried": file count in w2a block 1; provenance files confirmed in `sources/w1d/pypi-api/`.
  - line 71, FoMoE's longer quotation: 04a records "central coordinator, synchronous rounds (§3.1)" only; wording confirmed in `audit_sources/a2/fomoe/paper_v2.txt` line 226. The citation "via note 04a" slightly over-attributes the wording.
- Locator note (outside this rule): line 172 cites Plexus "§3.1, §6"; w2c F3 records the "remain online" passage as §5. The raw text puts it in §6 "Broader Impact and Open Challenges", so the report is right and the note's §5 is the slip.

Result: no source is cited in sections 1 to 6 without a recorded reading.

## 4. Section 7 completeness and accuracy

**Completeness.** Every CNV item of all seven notes appears in section 7 (78 items; Flower and BOINC Windows share one line, 655). Every item pointed to from scope is present. Body-marked items used in scope: only js-libp2p (P1), which section 7 lists only as an unopened lead (line 690).

**Items a later note verified.** Lines 587 to 591 list four. Checks:
- 588 Hivemind averager: accurate (w2b B1, code inference); correctly stated as not used in scope (line 66's "run on Hivemind" rests on DeDLOC §4.1 and w2b B3, not on this item).
- 589 NoLoCo pairing: accurate; used at 69, 275, 286, 427, 430 as line 587 says.
- 590 PCCL: accurate (w2b B8 read `03_MasterOrchestration.md`, all 70 lines; lines 8 to 13 and 65 to 71); used at 59, 270 to 277, 506.
- **591 Agora: inaccurate (S7-1).**

**Changed lines (585, 587, 590, 591, 599, 600, 606, 624, 627, 634, 635).**

| Line | Verdict |
|---|---|
| 585 | Reads correctly on its own, but its claim "Nothing in this section is used as evidence ... except the four" is contradicted by line 692 (S7-2) and by P1/P2 |
| 587 | Correct |
| 590 | Correct |
| 591 | **Wrong (S7-1)** |
| 599 | Correct (w1a gap 8) |
| 600 | Correct (w1a S9 README "dev mode"; w2a 7) |
| 606 | Correct; arithmetic checks (16.1/12.9 = +24.8%; 14.0/11.8 = +18.6%; 16.1/12.3 = +30.9%) |
| 624 | Correct (w1c S15 read the client docstring only). Could add that 4.1's closer and publisher roles also depend on it |
| 627 | Correct but incomplete: §5.7.1 should join §5.7.2 (S7-1) |
| 634 | Correct (w1d S2 question; H1) |
| 635 | Correct (w1d gaps "Not measured") |

**S7-1 (line 591, also 627).** Line 591 says w2b B11 "read v1 §3.5.3 and §6.4 in full, which hold the failure results w1c cited as §5.7.1 and §6.4". In v1, §5.7.1 is its own section: "5.7.1 ALL-REDUCE FAULT TOLERANCE" at line 2653 of `sources/w2b/p/2607.13332v1.txt`, measuring reduce success and averaging success "during the Pluralis-8B run". §3.5.3 (line 1168) is the separate failure-injection test. B11's read list does not include §5.7.1, so w2b's mapping (and line 591) is wrong: §6.4 is closed, §5.7.1 is still open. Scope is unaffected: Q6 uses only §5.1, §5.3.2 and §6.4. Fix: "Agora's all-reduce failure results (w1c): w2b B11 read v1 §6.4 in full, and also §3.5.3 (failure injection). Used in Q6. §5.7.1 (all-reduce success measured during the Pluralis-8B run) and §5.7.2 (inter-replica divergence) stay open (w1c list below)." Line 627: "Agora's measured all-reduce success during the run (§5.7.1) and inter-replica divergence (§5.7.2)."

**S7-2 (lines 585 and 688/692).** Line 692 sits under "**Leads seen but not opened** (no claims made from them)" but lists sources "now read in this study", several of them used as evidence in sections 1 to 6 (HALoS, HeLoCo, Eager Updates, Covenant-72B, INTELLECT-2, Moshpit, DeMo). That contradicts both the heading and line 585 ("seen but not confirmed at source"; "nothing in this section is used"). It also overstates two entries: "Not Every Sync Is Safe" was read at abstract level only, and PALSGD at abstract plus a grep (w1b S19). Fix: move line 692 to section 8, or reword: "Stage 0 leads now read in this study, so no longer leads: EDiT, HALoS, HeLoCo, Eager Updates, Covenant-72B, INTELLECT-2, and Moshpit SGD and DeMo beyond their abstracts; 'Not Every Sync Is Safe' and Pseudo-Asynchronous Local SGD at abstract level only (w1b S19)."

**S7-3 (line 617).** "Psyche's relay hostnames and their operator": w1c's item is that the `USE_RELAY_HOSTNAME` and `USW_RELAY_HOSTNAME` values were not read. w1a S15 read those values in `shared/network/src/lib.rs` lines 105 to 106 (`use1-1` and `usw1-1.relay.nousresearch.psyche.iroh.link`), so that half is closed. Only the operator is open, and line 596 already lists it. Fix: "Psyche's relay operator (the hostname values were read in w1a S15; same as the w1a item above)", or delete the line.

**S7-4 (line 690).** "js-libp2p mechanisms" appears as an unopened lead, while Q9 (line 329) uses it (P1). Fixing P1 resolves this.

## 5. Class (c) check (section 4)

Passes. No design recommends a public third-party network for live coordination by default:
- 4.1 Option A: "Nothing of class (a) or (c)"; the Hub bucket event stream (borderline) and R2 (paid) are flagged "if adopted".
- 4.2 Option B: "Library defaults (n0 relays and discovery, IPFS bootstrap) are class (c) and must be replaced"; bootstrap and relays are our own machines.
- 4.3 Option C: Option A's elements plus our own intermittent relays; direct links only where P2 (custom relay on our machine) shows they work.
- 4.5: ledger "class (c), outside R2 ... flagged for Phase 6", not recommended.
- 4.6: Solana and Bittensor (c) are listed as reasons against Psyche and Templar.
- 4.7: R2 fallback "(possibly paid; section 7; flagged)".
- Section 1 line 34 and Q2 line 135: public STUN is (c), "the owner's decision".
- Note: P1 (section 6) needs some outside observer to compare the router's WAN address with the address seen from outside, and to classify NAT behaviour. That is a one-off measurement, not live coordination. If a public echo or STUN service is used for it, a short note would keep the class rule visible. Not a flag failure.

## 6. PROBLEM list

**P1. Line 329 (Q9 maintenance table), js-libp2p row.**
- Text: `| js-libp2p | TypeScript, Node.js | Apache-2.0 | 2026-10-11 | npm 3.3.12 (2026-10-10) | tested in CI | README | as go-libp2p |`
- Why: "as go-libp2p" asserts discovery, NAT traversal, relays and pnet (the go row's content). w2a block 6 says "as block 3 in kind (inference). Mechanisms were not read in wave 1", and w2a "Not covered" lists "js-libp2p mechanisms". ProbeLab (w1a S14) calls js-libp2p's DCUtR experimental. Section 7 line 690 lists the item as an unopened lead. So unverified content is stated as fact, with neither "(inference)" nor a pointer.
- Fix: "as go-libp2p in kind (inference; mechanisms not read, section 7); ProbeLab calls its DCUtR experimental (w1a S14)".

**P2 (minor). Line 327 (Q9 table), rust-libp2p row.**
- Text: `| rust-libp2p | Rust | MIT | 2026-10-13 | v0.57.0 (2026-09-11) | compile check only | README | as go-libp2p |`
- Why: the go cell reads "pnet over TCP or WebSocket (inference)", an inference from go-libp2p's QUIC transport refusing a pre-shared key. Carrying it to rust-libp2p by "as go-libp2p" states a restriction that w1a S5 and w2a 4 record as "not checked" (section 7 line 598). The rest (Kademlia, relay limits, DCUtR/AutoNAT/pnet crates) is read in w1a S5.
- Fix: "as go-libp2p (w1a S5); whether its pnet runs over QUIC is not checked (section 7)".

**Advisories (no rule break; optional).**
- V1, line 54: the row label "libp2p (go; also rust, py, js)" sits over ratings sourced from go and rust only (w1a S3, S4, S5). Suggest "(go; rust similar; py and js not verified, see Q9 and section 7)".
- V2, lines 409 and 440: Option A's closer ("other attempts fail") and recovery ("the next peer's conditional commit succeeds") rely on server-side `parent_commit` enforcement, which section 4.5 (491) and section 7 (624) mark as unconfirmed. Section 4 is declared inference and 4.7 lists P4 as a dependency, so this is not a violation. A parenthesis "(if the Hub enforces `parent_commit`, section 4.5)" at 409 would make the dependency visible where it is used.
