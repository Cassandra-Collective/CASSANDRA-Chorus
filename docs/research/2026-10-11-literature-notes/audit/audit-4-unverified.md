# Audit 4: are unverified items confined to section 7?

Report: `docs/research/2026-10-11-stage0-literature-report.md` (746 lines). Header plus sections 1-6 = lines 1-627; section 7 "Unverified leads" = lines 628-719.
Helper `report_s1to6.md` checked: byte-identical to the current report's lines 1-627 (`diff -q`). `ids_s1to6.txt` regenerated from the current text: identical (92 arXiv IDs).
Status: COMPLETE. No repository file was edited.

## Method

1. Compiled the unverified items in each notes file: its "Could not verify" section, plus body markers (unverified, not confirmed, snippet, second-hand, not opened, abstract only, metadata only, figure only, garbled and not used, not stated, not read). Garbled tables that a researcher mapped with a cross-check and then used (SDP Table 4, PVT Table 2, BTX Table 2, Fan Table 3, Streaming DiLoCo Table 6, X-MoE Table 2 and others) count as verified, not declined, and are not listed.
2. Searched lines 1-627 by name, arXiv ID, key number and key phrase (script `a4_search.py`, output `a4_hits.txt`), then read every hit in context. The full report was read once end to end as well.
3. Classified each true hit. Name collisions (for example "Photon" inside a DES-LOC quote, "47.8" from FlexOlmo, "50.5" from SPES, "1.19" from KALAVAI's −1.19%, "335M" from SMALLTALK) were discarded as false positives.
4. Converse check (script `a4_converse.py`, output `a4_converse.txt`): every one of the 92 arXiv IDs in lines 1-627 has a notes entry with a read record. The 5 papers cited by name only (MuLoCo, post-local SGD, InclusiveFL, Symphony-MoE, MedMix) also have entries. Where a locator looked like it might fall outside the sections read, I checked the notes' read status. Where a note's wording left open whether a claim came from text or from a plot, I grepped the raw paper text in `scratchpad/papers/` (DeepSeekMoE, OLMoE, StableMoE, Grouter, Gating Dropout, MuLoCo, INTELLECT-1, BTM, Demons). Every such claim was in the text.

Classes:
- **OK-pointer**: says a detail is not stated or is unresolved, or points to section 7, without asserting the unverified content.
- **OK-verified-elsewhere**: another note, or the coordinator, verified the item at source; the report uses that reading.
- **OK-abstract-only**: an abstract-level paper, cited as such, with only abstract claims used.
- **OK-search-finding**: a "none found" or "no code" cell that records a search (step 5 of the brief).
- **OK-verified-content**: the hit is on the same paper, but the line uses only content that the note verified at source. The unverified detail is not asserted.
- **PROBLEM**: the unverified content itself appears in lines 1-627 as a statement or as evidence.

## 1. Compiled unverified items (111 item groups)

| Notes file | Item groups | Items |
|---|---|---|
| 01 local averaging | 21 | 01-1 Photon centralized token count; 01-2 SlowMo reset details, base algorithm and τ; 01-3 Streaming DiLoCo venue; 01-4 Woodworth venue; 01-5 Outer-Momentum Restarting at ICML 2026, figures only; 01-6 Factored Gossip at ICML 2026 (arXiv comment); 01-7 scaling-laws Fig. 7 (garbled); 01-8 Horoi Table 6 (garbled); 01-9 INTELLECT-1 App. A (garbled); 01-10 Defazio Table 2 (garbled); 01-11 Streaming DiLoCo Table 6 batch convention; 01-12 DES-LOC Fig. 5 legend, final or window-averaged; 01-13 unopened leads (EDiT, Pseudo-Async, HALoS, HeLoCo, LoRDO, Not Every Sync, Eager Updates, Sign Momentum, Stich, Wang-Joshi, Covenant-72B, INTELLECT-2/3); 01-14 abstract-only Gu et al. 2303.01215, Moshpit, DeMo; 01-15 QSR (abstract and §1 only); 01-16 figure-only results (DiLoCo Figs. 4 and 6, scaling Fig. 9, MuLoCo Fig. 6, Async Fig. 5, Khaled Figs. 4 and 7, Factored Gossip Fig. 5, Sani Fig. 3); 01-17 OpenDiLoCo inner state not stated; 01-18 Khaled theory not read; 01-19 Local Adam averaging step not inspected; 01-20 FedOpt model size not read; 01-21 FoMoE seen in OpenAlex, not opened by 01 |
| 02a MoE specialization | 15 | 02a-1 Dikkala arXiv ID; 02a-2 venues not at source (Hash Layers NeurIPS 34, Clark ICML 2022, DeepSeekMoE ACL 2024, SMoE-Dropout and Chen et al. none, Fan ICLR 2024); 02a-3 unresolved code links; 02a-4 garbled tables (σ-MoE Table 9, Advancing Table 1, Mixtral Table 5 Wikipedia row); 02a-5 inconsistencies (Fan 10.667/10.666, Slicing multipliers, Advancing silhouette); 02a-6 UniPool v1 title; 02a-7 unopened MoE leads (15); 02a-8 SimBal (abstract level, 36%) and ERC (abstract and §1 only); 02a-9 figure-only values (OLMoE Figs. 6 and 9-11, DeepSeekMoE Figs. 3-4, aux-loss-free Fig. 2, Grouter Fig. 1b); 02a-10 SMoE-Dropout Fig. 5b (comparison symbol lost, per 05); 02a-11 Clark Recommendation 1 (symbol dropped); 02a-12 Chen et al. theorems not read; 02a-13 Advancing "up to 23.79%" (abstract); 02a-14 Mixtral training data and upcycling not stated; 02a-15 Lo et al. behavioural sections not read |
| 02b federated and merged MoE | 11 | 02b-1 MergeME and 2408.17280 (metadata only); 02b-2 seen-only leads (EMO, FFT-MoE, pFedMoE, dFLMoE, PM-MoE, FedVLA, IJCAI, FedMoE ICWS, Fed-MoE pruning, Revisiting, Grouter, M-SMoE, REAM, FURINA, TT-LoRA, Connito, Mosaic); 02b-3 FedMix (snippet only); 02b-4 garbled tables (FedMoE-DA II-III, DDOME T1, HARC T1 TIES/DARE/Fisher rows, FedAlign-MoE v2 T2 MMLU, FlexOlmo T1 individual and 1×-FLOPs rows); 02b-5 figure-only effects (FedAlign-MoE 3b/4d/16/17, HFedMoE 4b/16, DDOME 8, FedMoE 2, FedMoE-DA 3, HARC Fig. 1); 02b-6 Router KD App. G not read; 02b-7 licences not established; 02b-8 NMoE abstract only, FC-MoE partial; 02b-9 not stated: HFedMoE data partition, FedCoE preliminary client count, FedMoE local steps, Symphony venue; 02b-10 HARC +0.27 prose against row order; 02b-11 FedAlign-MoE v1/v2 Table I |
| 03 partial updates | 8 | 03-1 DepthFL (403); 03-2 Ro et al. FL4NLP (snippet); 03-3 Filippova NeurIPS 2025 listing, code; 03-4 TwIST/EPM/NeFL code, TwIST "P100"; 03-5 unopened leads (MAST, Liao, AsyncDrop, Beton, HtFLlib, GASLoC, two OpenAlex titles, FedPT, EST, RaPTr); 03-6 holder-count distribution derived from code, not run; 03-7 EPM Table 1 garbled, IST and Shulgin proofs not read, FjORD baseline; 03-8 Filippova inner AdamW state not stated |
| 04a SPES and citers | 11 | 04a-1 SPES DiLoCo expert aggregation; 04a-2 which runs produced SPES Table 1; 04a-3 SPES Figs. A1/A2 values; 04a-4 FoMoE centralized (Fig. 5 only), Table 6 vs Table 4 cell, std definition; 04a-5 FoMoE balance-loss scope and coefficient; 04a-6 Semantic Scholar 429, OpenAlex FlexOlmo hits not confirmed; 04a-7 Gauntlet Table 1 garbled, IOTA quality not read; 04a-8 FlexMoRE/MetaMoE/DistMoE code, abstract-level citers; 04a-9 BAR 49.1/47.8/50.5 (abstract); 04a-10 EMO appendices and rest not read; 04a-11 SPES node count at 1B not stated |
| 04b closest methods | 12 | 04b-1 MoE-DisCo code and licence, initialization, PPL set, Figs. 6-7; 04b-2 BTX/BTM/DiPaCo later venues; 04b-3 no official code (BTX, SMALLTALK, DEPT, FoMoE), Learning@home licence; 04b-4 BTM Fig. 7 end points; 04b-5 OpenDiPaCo README self-reported; 04b-6 DEPT token count against its baseline; 04b-7 KALAVAI appendices; 04b-8 abstract-only leads (BTS, Nexus, HDEE, c-BTM, BAR, EMO, Optimal Splitting, BlockTrain, SpecDrop); 04b-9 FoMoE "Table 3" (04b's undescribed claim); 04b-10 figure-only (MoE-DisCo Figs. 6/7, SMALLTALK Figs. 4-5, DEPT Fig. 7, Learning@home Fig. 6, FoMoE Fig. 7); 04b-11 FoMoE "±", routing-entropy and no-collapse claims; 04b-12 garbled tables not used (SMALLTALK Tables 4-5, DEPT Tables 15/17/21, DiPaCo Table 4) |
| 05 baselines | 16 | 05-1 Transformer-XL training steps and batch, 12-layer evaluation length; 05-2 Cooijmans training length and parameter count; 05-3 Krause text8 training length, parameter counts, state handling; 05-4 SMoE-Dropout parameter count, segment length, validation or test; 05-5 S2MoE parameter count and protocol; 05-6 scaling laws Table 3, 70M or 700M; 05-7 D3PM chunk overlap; 05-8 venues not stated (Longformer, Clark, ST-MoE, SMoE-Dropout, S2MoE, DiLoCo, scaling laws, Discrete Flows); 05-9 unopened leads (8); 05-10 second-hand RHN 1.27, HM-LSTM 1.29, mLSTM-dyn 1.19; 05-11 plot-only (adaptive span Fig. 3, Switch App. D Fig. 12); 05-12 Argmax Flows 1.39/1.38, Discrete Flows disputed; 05-13 Cooijmans and Krause state handling ("continuous"); 05-14 MDLM; 05-15 scaling laws 335M/330M; 05-16 budget of every transformer text8 row (Transformer-XL's not stated) |
| 06 round-2 citation chase | 17 | 06-1 FoMoE "±" definition; 06-2 FoMoE perplexity definition; 06-3 LocalAdamW outer lr and momentum; 06-4 random-placement reshuffle period; 06-5 routing-entropy and no-collapse claims; 06-6 skip-token quality (Fig. 7); 06-7 FoMoE centralized (Figs. 5, 13); 06-8 MoEC mask redraw, top-k, code, AAAI venue; 06-9 2212.07571 backbone, Findings venue; 06-10 LocMoE (figures only); 06-11 DeepSeek-V2 numbers behind "roughly aligned"; 06-12 Routing Drift Table 2 cells; 06-13 abstract-only (HybridEP, DISCO, FedFMX, pFedMoAP, other screened citers); 06-14 Algorithm 2 wording; 06-15 FoMoE parameter breakdown (second expert matrix assumed); 06-16 Occult, TA-MoE not pursued; 06-17 citers without IDs (title only), Google Scholar unreachable |

## 2. Every true hit in lines 1-627, by item

Items with no hit in lines 1-627 (the unverified content never appears outside section 7): 01-3, 01-4, 01-5, 01-6, 01-7, 01-8, 01-13, 01-14, 01-20, 02a-3, 02a-4, 02a-7, 02a-8, 02a-11, 02a-13, 02b-1, 02b-3, 02b-8, 03-1, 03-2, 03-5, 04a-5, 04a-7, 04a-11, 04b-4, 04b-6, 04b-8, 04b-12, 05-4 (no validation/test or size claim), 05-5, 05-6, 05-9, 05-10, 05-11, 05-12, 05-14, 05-15, 06-5, 06-10, 06-16. On these items the paper is either not cited at all, or cited only for other content that its note verified. For example, Streaming DiLoCo, Woodworth and Factored Gossip are cited with no venue; Horoi only through clean Tables 2, 4 and 5; Defazio through a §1 quote; BAR without 49.1, 47.8 or 50.5.

| Item | Line | Class | Note |
|---|---|---|---|
| 01-1 Photon | L278 | OK-pointer | "(inference, 01; details unresolved, section 7)" |
| 01-1 | L320 | OK-pointer | "not equal-compute in our sense (inference, 01; section 7)" |
| 01-1 | L321, L329, L331, L540, L544 | OK-verified-content | §5.2 quote, Table 4, §5.3, App. B.1 (01 A6 read) |
| 01-2 SlowMo | L320, L544 (values) | OK-verified-content | Table B.3 values 4.732 / 2.106 (01 B5) |
| 01-2 | L544 | OK-pointer | "whether SlowMo's did is not described (section 7)" |
| 01-2 | L319, L540, L331 | OK-verified-content | Table B.1 |
| 01-9 INTELLECT-1 | L323 | OK-verified-content | WSD and final-20% cool-down are in §3 text (raw text L470-474), not the garbled App. A |
| 01-10 Defazio | L319 | OK-verified-content | §1 quote; Table 2 not used |
| 01-11 Streaming DiLoCo | L309 | OK-pointer | "batch convention not stated" |
| 01-11 | L29, L322, L541 | OK-verified-content | Table 6 rows (explicit "M H" prefixes, 01 A3) |
| 01-12 DES-LOC | L146, L320, L544 | OK-pointer | legend caveat, "section 7" |
| 01-12 | L30, L144, L311, L312 | OK-verified-content | legend values read at source; they do not say "final". Caveat sits at L146 and L320 only (advisory A1) |
| 01-15 QSR | L323, L560 | OK-abstract-only | marked "abstract and §1 only" / "(abstract, v2)" |
| 01-16 figure-only | L71, L72, L134, L319, L321, L330, L540 | OK-verified-content | each is a text quote or text-stated direction, tagged figure only; no plotted value used |
| 01-16 | L561 MuLoCo | OK-verified-content | "scales better with workers" is stated in the text (§1 contributions, Fig. 6 caption; raw text L125, L760) |
| 01-17 OpenDiLoCo | L310 | OK-pointer | inner state "not stated" |
| 01-18 Khaled theory | L120, L319, L551 | OK-abstract-only | claim from the abstract/§1 contribution statement, read; marked at L112 and L551 |
| 01-19 Local Adam | L143 | OK-verified-elsewhere | description as given by DES-LOC (01 B4; 01 C7) |
| 01-21 FoMoE | all FoMoE lines | OK-verified-elsewhere | 04a, 04b and 06 read v2 in full |
| 02a-1 Dikkala | L343 | OK-pointer | EMNLP 2023 from the PDF footer plus Crossref (verified); "see section 7" for the missing arXiv ID |
| 02a-2 venues | L181 Fan | OK-pointer | "preprint (see section 7)" |
| 02a-2 | L171 Gating Dropout | OK-verified-content | ICML 2022 from the PMLR footer |
| 02a-2 | L391, L395, L399, L515, L517, L523 | OK-verified-content | Hash Layers, Clark, DeepSeekMoE and SMoE-Dropout cited with no venue |
| 02a-5 | L184 | OK-verified-content | uses the Fig. 1 caption pair 10.674/10.667, not the disputed Table 1/Table 3 pair |
| 02a-6 UniPool | L393 | OK-verified-content | v2, Table 1 |
| 02a-9 figure-only | L342 | OK-verified-content | OLMoE 60% (§5.1 text), StableMoE 15.4% (§1 text), Grouter (§2.2 and Fig. 1 caption text, tagged figure only) |
| 02a-9 | L399 | OK-verified-content | DeepSeekMoE "majority of benchmarks" (§4.4 text, raw L671); OLMoE and aux-loss-free directions stated in text |
| 02a-9 | L556, L558 | OK-verified-content | text claims, tagged figure only / normalized plot |
| 02a-10 SMoE-Dropout Fig. 5b | L291, L397 | OK-pointer | shown as unresolved, but it points to the section 3 table, and the item is **absent from section 7** (M1) |
| 02a-12 Chen et al. | L340 | OK-abstract-only | marked "theorems not read"; claims from §1 and §5, which were read |
| 02a-14 Mixtral upcycling | L353 | OK-verified-content | presented as two papers' attribution, not as fact (advisory A5) |
| 02a-15 Lo et al. | L353 | OK-verified-content | §4.1 read |
| 02b-2 EMO | L294, L367, L372, L381, L476, L546, L604 | OK-verified-elsewhere | 04a read §3, §4, §5.1, §5.2 and the start of §5.3 |
| 02b-2 Grouter | L342 | OK-verified-elsewhere | 02a F3 read the abstract, §1 and §2.2 |
| 02b-4 FlexOlmo | L204, L369, L553, L554, L582 | OK-verified-content | clean Table 1 rows only; 46.3 (1× FLOPs) and the individual rows are not used |
| 02b-4 HARC | L214, L553 | OK-verified-content | Table 1 weight-averaging and WUDI rows, Table 7; the TIES/DARE/Fisher rows are not used |
| 02b-4 FedAlign-MoE | L374 | OK-verified-content | MMLU IID 0.4641/0.5131 comes from Table I v2 (02b entry 1), not the garbled Table II MMLU columns |
| 02b-4 DDOME | L340, L370, L554 | OK-verified-content | Theorem 1 statement, App. E prose; Table 1 not used |
| 02b-5 | L374, L555 | OK-pointer | "in figures", "component effects in figures only" |
| 02b-6 Router KD | L487, L553, L559 | OK-verified-content | §4 prose, marked; App. G not used |
| 02b-7 code/licences | L574, L580 | OK-pointer | "licence unknown (section 7)", "licence not established (section 7)" |
| 02b-7 | L573, L578, L579, L581, L583, L584, L585, L586 | OK-search-finding | "no code linked", "none found (section 7)", "none mentioned", "not released" |
| 02b-9 | L374 FedCoE | OK-verified-content | §III numbers; client count not claimed |
| 02b-9 | L581, L586 | OK-pointer | "local steps and rounds not stated", "not recorded in the notes" (FedMoE's local steps are absent from section 7: M4) |
| 02b-10 HARC +0.27 | L214, L553 | OK-verified-content | Table 7 SFT +0.27 (38.08 to 38.35), not the disputed Qwen3 Table 6 +0.27 |
| 02b-11 FedAlign-MoE | L374, L555 | OK-verified-content | v2 cited |
| 03-3 Filippova | L151 | OK-pointer | "the PDF names no venue; see section 7" |
| 03-4 TwIST, EPM | L281, L437 | OK-verified-content | TwIST has no full-model number; EPM Theorem 1 and §6.2 (read) |
| 03-6 holder counts | L13, L34, L405, L430 | OK-verified-elsewhere | coordinator's 100,000-draw simulation; section 7 L705 |
| 03-7 Shulgin | L384, L438 | OK-verified-content | §4.2, Theorem 2 and App. C.2 read (03 P3); only the App. B proofs were not read |
| 03-7 IST, FjORD | L445, L449, L453, L548, L559 | OK-verified-content | Tables 1-3; FjORD §5.3 |
| 03-7 | L455 | OK-pointer | FjORD "has none in the sections read" |
| 03-8 Filippova state | L156 | OK-pointer | "not stated to be reset (03 reads it as kept)"; **absent from section 7** (M3) |
| 04a-1, 04a-2 SPES | L83, L85, L572 | OK-verified-content | 50B is the v3 paper's statement; the DiLoCo score 49.79 is verified |
| 04a-2 | L459 | OK-pointer | "could not be determined (section 7)" |
| 04a-3 SPES Fig. A2 | L88, L322, L541 | OK-verified-content | direction stated in the text (04a tag); values not used |
| 04a-4 FoMoE centralized | L36, L104, L325, L573 | OK-pointer | "no numeric centralized result", "shown only in Fig. 5"; the 106.91 cell is not used |
| 04a-6 | L476 | OK-verified-content | "returned 25 works; of those screened"; the hits are not called citers |
| 04a-8 MetaMoE, DistMoE | L476 | OK-abstract-only | abstract-level characterization, but not marked as abstract-level (advisory A3) |
| 04a-9 BAR | L294 | OK-pointer | its numbers are kept out of sections 1-6; confirmed by grep |
| 04a-9 | L554 | OK-verified-elsewhere | tool use 20.3 against 46.4, §5.3, read by 02b |
| 04a-10 EMO | as 02b-2 | OK-verified-elsewhere | 04a |
| 04b-1 MoE-DisCo | L376, L467 | OK-verified-content | §4.5.1 text quote, tagged figure only; uses the loss column, not the PPL column of unknown set |
| 04b-1 | L574 | OK-pointer | "initialization not stated"; licence "(section 7)" |
| 04b-2 | L221, L231, L468 | OK-verified-content | "preprint" is what the versions read state; section 7 L639 notes later venues are unchecked |
| 04b-3 | L575, L578, L579, L580 | OK-search-finding | with "(section 7)" |
| 04b-5 OpenDiPaCo | L577 | OK-pointer | "(unverified claims, section 7)"; MIT is from the GitHub API |
| 04b-7 KALAVAI | L376, L474, L553, L554 | OK-verified-content | main text §4.5, §4.10, Tables 4, 5, 12 |
| 04b-9 FoMoE "Table 3" | L290 | OK-pointer | "Unresolved. Not used"; **absent from section 7** (M2) |
| 04b-10 | L376 DEPT, L461, L473, L562, L580 | OK-pointer | "figure only", "reported only in a figure", "Fig. 6 only", "Fig. 7 only" with a text quote |
| 04b-11 / 06-1 FoMoE "±" | L104, L289 | **PROBLEM P1** | see section 3 |
| 05-1 Transformer-XL | L509 | OK-verified-content | Table 2, enwik8 |
| 05-1 / 05-16 | L494 | **PROBLEM P2** | see section 3 |
| 05-16 | L523 | OK-verified-content | qualified "with a stated budget" |
| 05-2 / 05-3 / 05-13 | L497 | OK-pointer for "parameter count not stated"; **PROBLEM P3** for "far more training and continuous context" | |
| 05-2 | L511 | OK-verified-content | Table 3 |
| 05-3 | L526 | **PROBLEM P5** | "converged models" |
| 05-4 SMoE-Dropout | L392, L397, L517 | OK-verified-content | Table 1 values; "equal-parameter" follows the paper's caption wording |
| 05-7 D3PM | L496 | OK-pointer | "whether its chunks overlap is not stated, section 7" |
| 05-7 | L500 | **PROBLEM P4** | "protocol-matched" |
| 05-8 venues | L111, L127 | **PROBLEM P6** (low) | NeurIPS 2025 from an OpenAlex DOI record (01 A2 L87, B1 L267); 05 lists the scaling-laws venue under Could not verify; section 7 L639 treats DOI-record venues as unconfirmed |
| 05-8 | L65 DiLoCo | OK-verified-content | "preprint (no venue on the arXiv record or in OpenAlex)" |
| 06-2 perplexity definition | L8, L36, L101, L461 | OK-pointer | the assumption is declared in the header; section 7 L669 |
| 06-3 LocalAdamW | L98, L103, L542, L544, L573 | OK-verified-content | no outer lr or momentum claimed |
| 06-4 reshuffle | L101, L548 | OK-pointer | "(section 7)" |
| 06-6 skip-token | L461, L562 | OK-pointer | figure only, plus the §6.3 text quote |
| 06-7 FoMoE centralized | L104, L573 | OK-pointer | |
| 06-8 MoEC | L38, L174, L364, L372, L545 | OK-verified-content | Table 3; venue, redraw frequency and top-k not asserted |
| 06-9 2212.07571 | L174 | OK-verified-content | Table 2 values; backbone and venue not asserted |
| 06-11 DeepSeek-V2 | L368, L562 | OK-pointer | "no numbers" |
| 06-12 Routing Drift | L214, L385, L399, L553 | OK-verified-content | prose numbers (§3.1, §3.2, §6.2) |
| 06-14 Algorithm 2 | L98, L573 | OK-verified-content | follows §5's wording; does not assert the disputed point |
| 06-15 parameter breakdown | L98, L573 | OK-verified-content | ~51M embeddings = 200,019 × 256, tied (stated) |
| 06-15 | L106 | OK-verified-content (inference) | "experts about 4%" rests on an assumed second expert matrix (advisory A2) |
| 06-17 | L478 | OK-verified-content | coverage statement |

### Counts by class

Computed by `a4_count.py` from the table above. A hit is an (item, line) pair. In the unique-line column, a line hit by several classes is counted once, under the first class in the order PROBLEM, pointer, abstract-only, verified-elsewhere, search-finding, verified-content.

| Class | Hits (item, line) | Unique lines |
|---|---|---|
| PROBLEM | 8 | 8 (L104, L111, L127, L289, L494, L497, L500, L526) |
| OK-pointer | 49 | 35 |
| OK-abstract-only | 7 | 7 (L120, L319, L323, L340, L476, L551, L560) |
| OK-verified-elsewhere | 14 (+2 blanket rows: "all FoMoE lines", EMO) | 12 |
| OK-search-finding | 12 | 6 |
| OK-verified-content | 114 | 66 |
| **Total** | **204** | **134** |

Converse check: 97 cited papers (92 with arXiv IDs plus 5 by name). All 97 have a notes entry recording what was read at source. Every locator checked falls inside the recorded sections. No paper in lines 1-627 lacks a reading record.

## 3. PROBLEM list

**P1. FoMoE "±" stated as settled (06 and 04b both list it under Could not verify; section 7 L668 lists it as open).**
- L289, handling cell: `Settled by 06 as probably not seed spreads (inference)`
- L104: `The "±" values are probably per-sample spreads, not seed spreads, so no seed noise is reported (inference from a near-constant spread-to-mean ratio of 12.6% to 15.7%, 06).`
- Why: "Settled" contradicts the item's open status, and "so no seed noise is reported" states the unresolved conclusion as fact.
- Fix: at L289, replace the cell with "**Unresolved** (section 7); 06 infers they are probably not seed spreads". At L104, replace "so no seed noise is reported" with "so seed noise may not be reported" and add "; section 7" inside the closing parenthesis.

**P2. Training budget of every transformer text8 result (05: Transformer-XL's budget is not stated).**
- L494: `Every published autoregressive transformer result on text8 found lies between 1.07 and 1.29 bits per character, and every one used 15 to 800 times our 0.164B training characters, that is 27 to about 1,456 passes over the data against our 1.8 (05).`
- Why: Transformer-XL's text8 1.08 lies inside 1.07 to 1.29, but its training budget is unverified (05 Could not verify; section 7 L661). "Every one" therefore asserts an unverified budget.
- Fix: replace "and every one used" with "and every one with a stated training budget (Transformer-XL's is not stated; section 7) used". L523 already uses this qualifier.

**P3. Cooijmans and Krause training length and context handling (05: training length not stated; state handling not stated).**
- L497: `... both with far more training and continuous context.`
- Why: 05 records both training lengths as not stated (Could not verify), and the continuous-context state handling as "not stated explicitly in the sections I read". Section 7 L661 covers the training length but not the state handling.
- Fix: replace the clause with "both early-stopped recurrent models whose training length and test-time state handling are not stated (section 7)". Add "and whether the test sequence is scored with carried state" to the Cooijmans and Krause entries at L661.

**P4. D3PM called protocol-matched (05: whether its 256-character chunks overlap is not stated).**
- L500: `our 1.4376 is 0.21 bits per character (16.9%) above D3PM's protocol-matched 1.23`
- Why: "protocol-matched" asserts the very point listed as unverified at L660. L496 carries the caveat, but L500 drops it.
- Fix: replace "protocol-matched" with "chunk-length-matched (overlap not stated; section 7)".

Severity: P1, P2 and P3 are substantive, because each states as fact an item its note filed under Could not verify. P4, P5 and P6 are wording-level, with one-phrase fixes.

**P6. NeurIPS 2025 venues taken from OpenAlex (low; judged by the report's own standard).**
- L111: `Khaled, Kale, Douillard et al., 2025, NeurIPS 2025 per OpenAlex (the arXiv record lists none).`
- L127: `Charles, Teston, Dery et al., 2025, NeurIPS 2025 per OpenAlex (the arXiv record lists none).`
- Why: the source is an OpenAlex DOI record (01 L87, L267). Section 7 L639 files MoEC's and 2212.07571's venues as "not confirmed at source" for exactly this reason, and 05's Could not verify lists the scaling-laws venue. Note 01 treated OpenAlex as sufficient; the report as a whole does not.
- Fix: at both lines, write "2025, preprint (NeurIPS 2025 per an OpenAlex DOI record; section 7)", and add both papers to section 7 L639. Alternatively, accept DOI records everywhere and remove MoEC and 2212.07571 from L639. Either way, apply one standard.

**P5. Krause mLSTM called converged (05: text8 training length not stated).**
- L526, Evidence cell: `converged models need regularization (mLSTM 1.40 to 1.27)`
- Why: "converged" asserts a training state that 05 could not verify.
- Fix: replace "converged models" with "longer-trained models" and add "(training length not stated; section 7)".

## 4. Unverified items absent from section 7 (the other half of the rule)

These are not stated as fact in lines 1-627, but section 7 does not list them either.
- **M1.** SMoE-Dropout Fig. 5b width study: the comparison symbol was lost (05), and 02a's reading is uncertain. It appears only in the section 3 disagreement table (L291) and L397. Fix: add it to section 7 under "Values from garbled tables or figures, not used", and change L291's handling cell to "Unresolved (section 7)".
- **M2.** FoMoE "Table 3": 04b claimed it shows a local-averaging cost, and no note describes it. It appears only at L290. Fix: add it to section 7's "FoMoE open items", and point L290 to section 7.
- **M3.** Filippova et al.: inner AdamW state handling is not stated (03 body; report L156). Fix: add it to section 7's "Measurement definitions not stated in the text read".
- **M4.** Minor items, none used in lines 1-627:
  - FedMoE's local steps and rounds (L581);
  - HFedMoE's data partition;
  - FedCoE's preliminary client count;
  - Symphony-MoE's venue;
  - SPES's node count at 1B;
  - Clark et al.'s Recommendation 1 symbol;
  - Mixtral's training data and initialization;
  - NMoE (abstract only) and FC-MoE (partial);
  - EPM's garbled Table 1;
  - garbled tables not used: SMALLTALK Tables 4-5, DEPT Tables 15, 17 and 21, DiPaCo Table 4;
  - plot-only figures from 01, 02a, 04b and 05 that sections 7 and 8 do not name: Switch App. D Fig. 12, adaptive span Fig. 3, OLMoE Figs. 6 and 9-11, DeepSeekMoE Figs. 3-4, MoE-DisCo Fig. 7, SMALLTALK Figs. 4-5.

  Fix: optionally add one line each, or one catch-all sentence in section 7 pointing to each note's Could not verify section.

## 5. Advisories (not violations)

- **A1.** L30, L144 and L311-312 use the DES-LOC legend values without the "final or window-averaged" caveat. The caveat is at L146, L320 and L544. Consider adding "(section 7)" to the L311-312 table rows.
- **A2.** L106 "experts are about 4% of its parameters (inference, 06)" assumes a second expert weight matrix, which the paper does not describe (06 §6). Add "assuming two matrices per expert".
- **A3.** L476 characterizes MetaMoE and DistMoE from their abstracts (04a). Add "(abstract level)".
- **A4.** The venue standards also differ for arXiv comments. 02a and 05 accept an arXiv comment as the source for σ-MoE's "Findings of EMNLP 2023" (L241). 01 treats an arXiv comment as unverified for Factored Gossip's ICML 2026 (section 7 L636). L241 attributes its source, so it is advisory. The DOI-record case is P6.
- **A6 (out of scope: number fidelity, not verification).** L557 says σ-MoE on enwik8 at 41M shows "no difference (1.08)" between softmax with renormalization and σ-MoE. 02a D4 records "softmax variants 1.09", and L244 itself says "1.08 to 1.11". Flag this for the number-fidelity audit.
- **A5.** L353 says two papers attribute Mixtral's similarity to "probable upcycling". Lo et al., per 02a, say "special schemes" or "specific initialization schemes", not upcycling. This is a fidelity point, not a verification point.
