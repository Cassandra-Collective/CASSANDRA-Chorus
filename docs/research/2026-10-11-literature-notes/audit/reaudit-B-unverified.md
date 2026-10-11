# Re-audit B: unverified items stay in section 7

Status: COMPLETE (2026-10-11).

- Report: `docs/research/2026-10-11-stage0-literature-report.md` (final, 760 lines). Scope audited: lines 1-630 (header and sections 1-6). Section 7 = lines 631-733; section 8 = 736-760.
- Notes: `docs/research/2026-10-11-literature-notes/` 01, 02a, 02b, 03, 04a, 04b, 05, 06.
- Independence: none of the earlier auditor's files in this directory were opened. My scripts are `rb_search.py`, `rb_numbers.py` (and two inline runs).
- Method: (1) read every "Could not verify" section and grepped each notes file for unverified / snippet / secondary / second-hand / not confirmed / not opened / figure only / garbled / row order / abstract only / metadata only / not stated / not read; (2) searched the scope by name, arXiv ID, key number and key phrase for every item (`rb_search.py`); (3) mechanical traceability: every decimal number, every comma-grouped number, every integer percentage and every quoted phrase in scope was checked for a verbatim occurrence in some notes file; (4) every arXiv ID in scope was mapped to a notes entry and its read status; (5) read-status locators of partly read papers spot-checked against the cited sections.

## Result in one paragraph

No compiled unverified item is asserted in scope. Every hit is a pointer (detail not stated / unresolved / figure only, usually with "section 7"), a reading verified in another notes file, an abstract-level claim, or a recorded search result. **One PROBLEM** comes from the converse check: a MedMix component value (0.529, "+0.001") in remedies row C3 is in no notes file. Pointer items used in scope but absent from section 7 are minor (two "inner state not stated" cells and several figure-only directions that sit in section 8 or nowhere).

## 1. Compiled items, per notes file

Counting convention: each named paper or value is one item (a bullet naming 10 unopened papers counts 10). "CNV" = under the file's "Could not verify" heading; "else" = marked elsewhere in the file. Garbled tables that a researcher mapped, cross-checked and used (SDP Table 4, PVT Tables 2-3, BTX Table 2, Fan et al. Table 3, MaskMoE Table 1, UniPool Table 1, MoEC Table 1, FedMoE Table 1, Hash Layers Table 4) are not "declined" and are not counted; aux-loss-free Table 2 (row order only, used) is discussed in section 6. Items shared by several files (FoMoE details) are counted once per file.

| File | CNV | Else | Total | Used in scope in any form (pointer, verified-elsewhere, search finding) |
|---|---|---|---|---|
| 01 local averaging | 23 | 24 | 47 | 17 |
| 02a MoE specialization | 39 | 13 | 52 | 9 |
| 02b federated / merged MoE | 43 | 12 | 55 | 9 |
| 03 partial updates | 20 | 6 | 26 | 4 |
| 04a SPES and citers | 16 | 8 | 24 | 8 |
| 04b closest methods | 27 | 13 | 40 | 17 |
| 05 baselines | 29 | 8 | 37 | 11 |
| 06 round-2 chase | 22 | 7 | 29 | 8 |
| **Total** | **219** | **91** | **310** | **83** |

The per-file lists below give the items (grouped where a bullet names several).

### 01 (47)
CNV: Photon centralized token count; SlowMo "reset buffers" implementation, base algorithm and tau; Streaming DiLoCo venue; Woodworth venue; Outer-Momentum Restarting at ICML 2026; Factored Gossip at ICML 2026 (comment only); garbled: Scaling-laws Fig. 7 best outer lr, Horoi Table 6 (lr 1.2/1.4/1.4/1.6), INTELLECT-1 App. A (mapped by order), Defazio Table 2; Streaming DiLoCo Table 6 batch convention; DES-LOC Fig. 5 legend final vs window-averaged; not opened: EDiT, Pseudo-Async Local SGD, HALoS, HeLoCo, LoRDO, Not Every Sync Is Safe, Eager Updates (abstract only), Distributed Sign Momentum (metadata), Stich 2019, Wang & Joshi; FoMoE seen in OpenAlex, not opened.
Else: Scaling-laws venue (NeurIPS per OpenAlex only); Khaled venue (same); Khaled theory sections not read; OpenDiLoCo appendix not read and inner state not stated; Streaming DiLoCo inner state not stated; Factored Gossip inner state not stated; Factored Gossip Table 1 garbled (text numbers used); figure only: DiLoCo Fig. 4, DiLoCo Fig. 6, Scaling-laws Fig. 9, 2405.10853 Fig. 3, Factored Gossip Fig. 5, Khaled Fig. 4 / Fig. 7, MuLoCo Fig. 6a, Async Local-SGD Fig. 5, Trade-offs (2110.08133), Outer-Momentum Restarting; Gu et al. 2303.01215 abstract only; Moshpit, DeMo abstract only; SlowMo Table 1 garbled (mapped via B.1); Local Adam averaging step not inspected; Covenant-72B, INTELLECT-2/3 not opened.

### 02a (52)
CNV: Dikkala arXiv ID; venues of Hash Layers, Clark, DeepSeekMoE, SMoE-Dropout, Chen et al., Fan et al.; unresolved code links Gating Dropout, X-MoE, Advancing Expert Specialization, bilingual MoE (Gopinath); no code link in text for Hash Layers, aux-loss-free, Demons, Clark, ERC, SimBal; garbled: sigma-MoE Table 9, Advancing Table 1, Mixtral Table 5 Wikipedia row; inconsistencies: Fan 10.667/10.666, Slicing and Dicing multipliers, Advancing silhouette; UniPool v1 title; 15 unopened leads (DeepSeek-V3, 2504.05586, 2506.02813, 2503.22517, 2606.10703, 2608.13565, Motif 3, LibMoE, cluster-aware upcycling, HyperRouter, V-MoE swap, STAR, ProbMoE, MoCE, 2601.14792).
Else: ST-MoE §5/§4 by grep only; OLMoE z-loss and Figs. 9-11 figure only; Mixtral training data / upcycling not stated; Lo et al. §5 not read; aux-loss-free does not measure specialization (DeepSeek-V3 not read); aux-loss-free Fig. 2 values figure only; SimBal results not read (36% abstract-only); Chen et al. theorems not read; ERC results not read; Grouter figure only, model size not stated; Clark Recommendation 1 symbol dropped; SMoE-Dropout Fig. 5b; DeepSeekMoE Figs. 3-4 values figure only.

### 02b (55)
CNV: MergeME, 2408.17280 (metadata only); search-only: EMO, FFT-MoE, pFedMoE, dFLMoE, PM-MoE, FedVLA, IJCAI 2025 paper, ICWS FedMoE, Fed-MoE Empirical Pruning, "Revisiting sparse MoE" workshop, Grouter, M-SMoE/MC-SMoE, REAM, FURINA, TT-LoRA MoE, Connito, Mosaic; FedMix (snippet); prose-only tables: FedMoE-DA II-III, DDOME Table 1, HARC Table 1 TIES/DARE/Fisher rows, FedAlign-MoE Table II MMLU, FlexOlmo Table 1 individual-expert and 1x-FLOPs rows; figure-only: FedAlign-MoE 3b/4d/16/17, HFedMoE 4b/16, DDOME 8, FedMoE 2, FedMoE-DA 3; Router KD App. G not read; licences: HARC null, FLEx link not opened, no code for 10 papers.
Else: FedAlign-MoE v1/v2 Table I differ; HARC Fig. 1 router swap figure only; HARC Qwen3 +0.27 prose vs row order; FlexOlmo HF model not opened; FedMoE local steps/rounds not stated; FedMoE Table 1 labels shifted (fixed); HFedMoE data partition not stated; FedCoE preliminary client count; Symphony-MoE venue; NMoE abstract only; FC-MoE partly read; PHATGOOSE-style gates not opened.

### 03 (26)
CNV: DepthFL (and 2303.04887); Ro et al. venue (FL4NLP, snippet); Filippova NeurIPS listing (page title) and no code; TwIST / Every Parameter Matters / NeFL code links; TwIST "4 P100"; 11 unopened (MAST, Liao & Kyrillidis, AsyncDrop, Beton, HtFLlib, GASLoC, two OpenAlex titles, FedPT snippet, EST, RaPTr); holder-count distribution from reading code.
Else: Filippova inner AdamW state "not stated otherwise"; HeteroFL Table 6 garbled; IST theory appendix not read; NeFL project page not opened; Every Parameter Matters Table 1 garbled; SDP gradient propagation through skipped blocks not explicit.

### 04a (24)
CNV: SPES DiLoCo baseline expert aggregation; which runs produced SPES Table 1; SPES Figs. A1/A2 values; FoMoE centralized (Fig. 5), no code, Table 6 M=8 K=32 cell, std definition; FoMoE balance-loss scope/coefficient; Semantic Scholar 429; OpenAlex hits citing FlexOlmo; Gauntlet Table 1; IOTA results; FlexMoRE/MetaMoE/DistMoE code; BAR 49.1/47.8/50.5 from abstract.
Else: SPES 1B node count not stated; FoMoE skip-token figure only; FlexMoRE appendices; IOTA §3-7; Gauntlet tplr.ai and §3-5; EMO unread parts and Fig. 7; abstract-only citers (CORTEX, DistMoE, etc.); MetaMoE/BAR abstract (search hits).

### 04b (40)
CNV: MoE-DisCo code (401, two unlinked repos); MoE-DisCo initialization; MoE-DisCo PPL/loss mismatch; venues of BTX, BTM, DiPaCo; no official code for BTX, SMALLTALK, DEPT, FoMoE; Learning@home licence; FoMoE "±", centralized number, routing-entropy claims; BTM Fig. 7 annotations; OpenDiPaCo README self-reported; DEPT token count (inferred); KALAVAI appendices A-S; abstract-only leads BTS, Nexus, HDEE, c-BTM, BAR, EMO, Optimal Splitting, BlockTrain, SpecDrop.
Else: MoE-DisCo Fig. 6 and Fig. 7 figure only; DiPaCo Table 4 garbled; SMALLTALK Tables 4-5 garbled, Figs. 4-5 figure only; DEPT Tables 15/17/21 garbled, App. B.3 Fig. 7 figure only; Learning@home Fig. 6; FoMoE Fig. 7; FoMoE Tables 4-5 read as full replica (inference); HeterMoE, Hexa-MoE, Lazarus abstract only.

### 05 (37)
CNV: Transformer-XL steps/batch and 12-layer eval length; Cooijmans training length and parameter count; Krause training length and parameter counts; SMoE-Dropout parameter count, segment length, validation vs test; S2MoE parameter count and protocol; Scaling-laws Table 3 70M vs 700M; D3PM chunk overlap; not found x3 (2-pass result, sliding-vs-chunk measurement on text8/enwik8, char-level MoE at 10M with dense baseline); venues of Longformer, Clark, ST-MoE, SMoE-Dropout, S2MoE, DiLoCo, Scaling laws, Discrete Flows; 8 unopened leads; second-hand RHN 1.27, HM-LSTM 1.29, mLSTM dyn-eval 1.19.
Else: adaptive span §2.2-2.3 not read; mLSTM / Cooijmans test-time state handling; Cooijmans 16.3M is an estimate; SMoE-Dropout Fig. 5b symbol lost; Discrete Flows reproducibility disputed; Argmax 1.39 vs 1.38 and likelihood relation not read; Switch App. D Fig. 12 values; MDLM opened, nothing recorded.

### 06 (29)
CNV: FoMoE "±" definition, exp(mean CE) vs per-chunk, balance coefficient/scope, LocalAdamW outer lr/momentum, reshuffle period, routing entropy, skip-token numbers, centralized perplexity; MoEC mask redraw / top-k / code / affiliations; 2212.07571 backbone; LocMoE local fraction and numbers; DeepSeek-V2 numbers behind "roughly aligned"; Routing Drift Table 2 cells; MoEC and 2212.07571 venues (DOI records); citers without arXiv IDs (title only); Google Scholar; HybridEP; DISCO.
Else: FoMoE Fig. 13 centralized sweeps figure only; Gating Dropout citers title only; FedFMX abstract; MoEC appendices not read; Occult, TA-MoE not pursued; FoMoE Algorithm 2 vs §5 wording.

## 2. Hits in scope, with class

### PROBLEM (1)
See section 5.

### OK-pointer (49 item hits, 66 line occurrences): the item appears only as "not stated / unresolved / figure only / not used", without asserting the unverified content
| Line | Item (file) | Pointer form |
|---|---|---|
| 31 | DES-LOC legend definition (01) | "see section 7" |
| 72, 320, 543 | DiLoCo Fig. 6 (01) | "figure only"; claim is a §3.1 text quote |
| 73 | DiLoCo Fig. 4 (01) | quote from §3.1 text |
| 89, 323, 544 | SPES Fig. A2 (04a) | "figure only"; direction from H-ablation text |
| 102 | FoMoE reshuffle period (06) | "not listed, section 7" |
| 105, 290 | FoMoE "±" (04b, 06) | "unresolved (section 7)" |
| 112 | Khaled venue (01) | "venue: see section 7" |
| 113 | Khaled theory not read (01) | read-status statement |
| 128 | Scaling-laws venue (01, 05) | "venue: see section 7" |
| 135 | Scaling-laws Fig. 9 (01) | "figure only"; §5.1 text direction |
| 147 | DES-LOC legend (01) | "(section 7)" |
| 152 | Filippova venue (03) | "see section 7" |
| 157 | Filippova inner state (03) | "not stated (section 7)" |
| 182 | Fan et al. venue (02a) | "see section 7" |
| 279, 321 | Photon token count (01) | "details unresolved, section 7" |
| 292, 398 | SMoE-Dropout Fig. 5b (02a, 05) | "Unresolved (section 7). Not used" |
| 295 | BAR headline averages (04a) | "not used outside section 7" |
| 310 | Streaming DiLoCo batch convention (01) | "batch convention not stated" (no explicit §7 ref; item is in §7) |
| 310, 311 | Streaming DiLoCo and OpenDiLoCo inner state (01) | "not stated" (**not in §7**, see section 4) |
| 312-313, 321, 547 | DES-LOC legend (01) | "section 7" |
| 322 | 2405.10853 Fig. 3 (01) | caption quote, "figure only" |
| 331 | Factored Gossip Fig. 5 (01) | text quote, "figure only" |
| 343 | Grouter (02a) | "figure only"; also OK-verified-elsewhere vs 02b |
| 344 | Dikkala arXiv ID (02a) | "see section 7"; EMNLP venue confirmed via Crossref and PDF footer |
| 354 | Mixtral upcycling (02a) | attributed as OLMoE's / Lo et al.'s hypothesis, not asserted |
| 369, 565 | DeepSeek-V2 numbers (06) | "no numbers" |
| 371 | DDOME Fig. 8 (02b) | App. E text quote, "figure only" |
| 377, 470 | MoE-DisCo Fig. 6 (04b) | §4.5.1 text quote, "figure only" |
| 377 | DEPT App. B.3 Fig. 7 (04b) | text quote, "figure only" |
| 400 | OLMoE Fig. 9; aux-loss-free Fig. 2 (02a) | text-stated directions only |
| 462 | SPES Table 1 provenance (04a) | "could not be determined (section 7)" |
| 464, 565 | FoMoE skip-token (04a, 04b, 06) | "reported only in a figure", "Fig. 7 only" |
| 476, 583, 609 | Learning@home Fig. 6 (04b) | "Fig. 6 only", "claims from a figure" |
| 497 | Transformer-XL budget (05) | "not stated; section 7" |
| 499, 503 | D3PM overlap (05) | "not stated, section 7" |
| 500 | Cooijmans params; Cooijmans/Krause training length and state handling (05) | "not stated (section 7)" |
| 529 | Krause training length (05) | "not stated, section 7" |
| 547 | SlowMo reset implementation (01) | "not described (section 7)" |
| 551 | FoMoE reshuffle period (06) | "not listed (section 7)" |
| 556 | HARC TIES/DARE/Fisher rows (02b) | "row order only (section 7)" |
| 558 | FedAlign-MoE component effects (02b) | "in figures only" |
| 559 | OLMoE z-loss (02a) | "figure only", text direction |
| 561 | DeepSeekMoE Fig. 3 (02a) | "normalized plot", direction only |
| 564 | MuLoCo Fig. 6 (01) | "figure only" (borderline, see section 6) |
| 576 | FoMoE centralized (04a, 04b, 06) | "centralized shown only in Fig. 5" |
| 577 | MoE-DisCo initialization and licence (04b) | "initialization not stated"; "licence unknown (section 7)" |
| 580 | OpenDiPaCo (04b) | "unverified claims, section 7" |
| 583 | Learning@home licence (04b) | "licence not established (section 7)" |
| 584 | FedMoE local steps/rounds (02b) | "not stated in the text read" |

### OK-verified-elsewhere (8 items)
| Lines | Item | Verified in |
|---|---|---|
| 13, 35, 406, 431, 590, 605 | holder-count distribution (03: read from code) | coordinator's 100,000-draw simulation (header); section 7 records it |
| 37, 95-108, 281, 363, 464, 545, 547, 551, 576 | FoMoE (01: seen, not opened) | 04a, 04b full text; 06 v1 and v2 |
| 288 | FoMoE cost figures "1.6 to 2.1%" slip (04a) | 06 §8 |
| 289 | FoMoE "O_e ≥ 4" (04b) | 06 §1 (≈) |
| 368, 382, 479, 607 | EMO (02b search-only; 04b abstract-only) | 04a §3, §4, §5.1-§5.2 |
| 557, 479 | BAR (04a, 04b abstract-only) | 02b §1-§6 (only §5.3 values used; the abstract averages are not) |
| 343 | Grouter (02b search-only) | 02a §2.2 |
| 175, 364 | Gating Dropout Fig. 6 dose-response 0.23 | 06 re-read, §4.4 text |

### OK-abstract-only (7 items)
2410.21676 critical batch (319, abstract); Khaled theory claim "greater than 1" (121, 320, 554, 601, abstract); QSR (324, 563: abstract and §1); MetaMoE and DistMoE characterised only as remedies "read at abstract level" (479); StableMoE and Demons abstract quotes (195, 352; papers otherwise read in sections); SPES v3 abstract motivation (462).

### OK-search-finding (28 hits)
"not found in this search" or equivalent, with the search in the notes or section 8: lines 23, 45, 97 ("No code linked"), 299, 324, 335, 346, 359, 402, 450, 451, 458 (FjORD "none in the sections read"), 479 (no SPES citer; no round-2 citer on more than one axis), 481, 491, 501, 505, 530, 563, 565 (D1), 578, 581, 582, 586, 587 ("none mentioned"), 588 ("not released"), 589. Venue "preprint" labels for DiLoCo (66: arXiv and OpenAlex both checked) also fall here.

### Compiled items not used anywhere in scope (227)
All other compiled items, including: every unopened lead in 01, 02a, 02b, 03, 05 and 06; MergeME, 2408.17280, FedMix; Horoi Table 6, INTELLECT-1 App. A, Defazio Table 2, Scaling-laws Fig. 7 values; sigma-MoE Table 9; Advancing Table 1 and silhouette; Mixtral Wikipedia row; Clark Recommendation 1; SimBal 36%; Slicing and Dicing multipliers; Fan 10.666 (the report uses the Fig. 1 caption's 10.667, which is not the disputed Table 1/3 pair); FedMoE-DA, DDOME Table 1, FlexOlmo individual and 1x-FLOPs rows (the report uses only the 2x row, 51.5); FedAlign Table II MMLU; Router KD App. G; Gauntlet, IOTA, FlexMoRE; BAR 49.1/47.8/50.5 (the 47.8 and 50.5 in scope are FlexOlmo and SPES values, checked); SPES DiLoCo aggregation; SPES 1B node count; FoMoE balance scope, LocalAdamW outer lr, routing entropy, Table 6 106.91 cell, Algorithm 2 wording; MoEC redraw and top-k; 2212.07571 backbone; LocMoE; Routing Drift Table 2 cells; DEPT |S_t| token estimate; BTM Fig. 7; Scaling-laws Table 3 70M; Argmax and Discrete Flows; second-hand RHN, HM-LSTM, mLSTM dyn-eval; TwIST P100; DepthFL.

## 3. Converse check

All 93 distinct arXiv IDs cited in scope map to a notes entry with a read status (full text or sections read; QSR and 2410.21676 abstract plus §1, used only for abstract claims). The two papers cited in scope without an arXiv ID (InclusiveFL, line 562; Dikkala et al., via DOI, line 344) are also recorded as read (03 P15; 02a E3). No paper in scope lacks a read record.

Mechanical traceability: every decimal number, comma-grouped number and integer percentage in scope occurs verbatim in some notes file, except **0.529 (line 558, MedMix)** and three header numbers that are the coordinator's own code facts (100,000; 42,467,328; 46,050,432). Every quoted phrase in scope occurs in the notes except two quotes of the prior survey (276, 278), the report's own phrases (617, 623), and one paraphrase in quotation marks (323, see section 6).

Two claims about a read paper rest on a reading not recorded in any notes file:
- **Line 558, MedMix:** "the similarity-based expert aggregation alone adds +0.001, 0.529 to 0.530". 02b records only 0.523 to 0.530 (full method) and 0.446 to 0.481 (modality-exclusive). This is used as evidence: PROBLEM 1.
- **Line 291, FoMoE "Table 3 is the parent caption of Tables 4 and 5"**: no notes file records it (section 7, line 719, attributes it to "a re-read of the v2 HTML" without naming a file). The load-bearing part, "no centralized number", is verified in 06 §2, so I class it as a record-keeping gap, not a PROBLEM.

## 4. Used in scope (even as a pointer) but missing from section 7

1. **Streaming DiLoCo inner-optimizer state "not stated"** (line 310; 01 anchor table). Section 7 has only its batch convention.
2. **OpenDiLoCo inner-optimizer state "not stated"** (line 311; 01 A4: "presumably kept ... not stated in the text read").
3. **Figure-only directions used as pointers whose figures are in section 8, not section 7:** DiLoCo Figs. 4 and 6 (72, 73, 320, 543), Scaling-laws Fig. 9 (135), Factored Gossip Fig. 5 (331), Learning@home Fig. 6 (476, 583, 609), MuLoCo Fig. 6 (564).
4. **Figure-only directions in neither section 7 nor section 8:** Async Local-SGD Fig. 5 (320, 543), 2405.10853 Fig. 3 (322), Grouter Fig. 1b (343), MoE-DisCo Fig. 6 (377, 470; section 7 lists only its Fig. 7), DEPT App. B.3 Fig. 7 (377), aux-loss-free Fig. 2 (400).
5. Not compiled items but same pattern: the "not recorded in the notes" cells for FedMoE and HFedMoE routing, FLEX-MoE masking and HFedMoE local steps (584, 586, 589). These are gaps in the notes rather than failed verifications; section 7 lists only FedMoE local steps/rounds and HFedMoE data partition.

All of these assert nothing unverified (only text-stated directions or "not stated" are used), so they are low severity. Fix for 1-2: add to section 7's "Measurement definitions not stated": "Streaming DiLoCo and OpenDiLoCo: inner optimizer state handling not stated in the text read (01)." Fix for 3-4: extend the "Plotted values not read" bullet (line 660) with "DiLoCo Figs. 4 and 6, Scaling-laws Fig. 9, Factored Gossip Fig. 5, MuLoCo Fig. 6, Async Local-SGD Fig. 5, 2405.10853 Fig. 3 [01]; Grouter Fig. 1b, aux-loss-free Fig. 2 [02a]; MoE-DisCo Fig. 6, DEPT Fig. 7, Learning@home Fig. 6 [04b]".

## 5. PROBLEM list

| # | Line | Exact text | Why | Fix |
|---|---|---|---|---|
| 1 | 558 (section 4, row C3, Evidence cell) | "the similarity-based expert aggregation alone adds +0.001, 0.529 to 0.530 (Table 3 and ablation prose, v1; inference)" | The component value 0.529 and its attribution to the similarity-based aggregation are in no notes file. 02b (MedMix entry and synthesis item 5) records only "average F1 0.523 (base) → 0.530 (full)" and "0.446 → 0.481". It is unverifiable against the record, yet used as evidence. | Delete the clause, leaving "MedMix, medical classification: full method 0.530 against 0.523 average F1 (+0.007) (Table 3, v1; inference)". If the value was read at source by the writer, add that reading (locator, row label) to 02b's MedMix entry; otherwise list it in section 7. |

Nature of PROBLEM 1: it is a converse-check failure, not a compiled section-7 item leaking into scope. Checked: 0.529 and the component claim appear in neither section 7 nor section 8 (MedMix appears in section 7 only in the no-code list, line 709) nor any notes file.

None of the 310 compiled unverified items is itself asserted in scope.

## 6. Borderline or advisory (not PROBLEMs under the rule)

- **Line 564, MuLoCo:** "better worker-count scaling relative to data parallel (Fig. 6, v3, figure only)". 01 records this only as a tag and a "figure only" Fig. 6a direction, with no text quote, and section 8 (line 756) says MuLoCo's scaling figures were not read. Suggest adding the text locator 01 used, or rewording to "figure only; direction as recorded by 01, values not read".
- **Line 549, aux-loss-free Table 2 (9.56 to 9.50, 7.97 to 7.92):** 02a mapped these rows "by row order", the same method that makes HARC's other rows a section-7 item. 02a did not decline them, so they are not an unverified item, but the treatment is inconsistent with HARC's. Suggest "(rows mapped by order, 02a)".
- **Line 107, FoMoE "with no renormalization":** 06 marks this "inference from the equations"; the report states it as fact. Add "(inference, 06)".
- **KALAVAI (377, 477, 556, 557):** main-text numbers are used with no pointer to section 7's note that unread appendices (evaluation correction, integrity audit) may qualify them. Suggest one "(appendices not read; section 7)" at line 477.
- **Line 479:** "no citer matches more than one of our four axes" partly rests on title-only screening of citers without arXiv IDs (06; section 7 line 732). Suggest "(some citers screened by title only)".
- **Lines 30, 323:** the Streaming DiLoCo gaps (+2.6%, +3.7%) carry no caveat, though they depend on the unresolved batch convention flagged at line 310.
- **Outside this rule, noted for the record:** line 323 puts "replicas drift apart" in quotation marks, but the paper's words (01) are "replicas drifting apart"; line 520 cites ST-MoE "§9" where 05 recorded "§7" (02a's §7 is token tracing, so 05's label may be the wrong one); lines 321 and 547 cite Photon "App. A" for the reset, where 01 quotes it from App. B.1.

## 7. Counts by class

| Class | Hits |
|---|---|
| PROBLEM | 1 (converse check; no compiled item asserted) |
| OK-pointer | 49 item hits (66 line occurrences) |
| OK-verified-elsewhere | 8 items (about 30 lines) |
| OK-abstract-only | 7 |
| OK-search-finding | 28 |
| Compiled items not used in scope | 227 of 310 |
