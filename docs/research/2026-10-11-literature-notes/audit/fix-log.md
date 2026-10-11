# Fix log: audit fixes applied to the Stage 0 literature report

Report: `docs/research/2026-10-11-stage0-literature-report.md` (746 lines before, 760 after).
"Line before" is the line number in the unedited report, as the audits cite it.
Date: 2026-10-11. Nothing was committed.

## Totals

| Audit file | PROBLEMs | Applied | Applied with adaptation | Not applied |
|---|---|---|---|---|
| audit-1-summary-readinglist.md | 19 | 19 | 0 | 0 |
| audit-2a-s3intro-q1.md | 5 | 5 | 0 | 0 |
| audit-2b-q2-q3.md | 13 | 13 | 0 | 0 |
| audit3-parts/part-a.md | 3 | 3 | 0 | 0 |
| audit3-parts/part-b.md | 9 | 9 | 0 | 0 |
| audit3-parts/part-c.md | 4 | 4 | 0 | 0 |
| audit-3d-remedies-B5-D1-and-gaps.md | 12 | 11 | 1 (P-D2) | 0 |
| audit-4-unverified.md | 6 | 6 | 0 | 0 |
| **Total** | **71** | **70** | **1** | **0** |

## 1. Every PROBLEM

| Audit file | Item | Line before | What changed |
|---|---|---|---|
| audit-1 | P1 | 34 | Filippova locator became "(inference from Filippova et al., Table 1, v1; 03)". |
| audit-1 | P2 | 106 | "about 61% of ours" became "about 92% of ours (inference: SwiGLU experts, 42.5M of 46.05M)"; FoMoE's 4% now says "assuming two matrices per expert" (also audit-4 A2). |
| audit-1 | P3 | 157 | Entry 7 question reworked per coordinator (a): about 54% trainable is close to the 1/4 row (about 52%, −0.1%); a holder share of one half matches the 1/2 row (−1.6%); fractions labelled as inferences. |
| audit-1 | P4 | 28, 137 | "about 10M active parameters" became "about 14M active parameters" (both lines). |
| audit-1 | P5 | 129 | "nine sizes from 35M to 2.4B (4B and 10B predicted)" became "nine sizes from 35M to 10B: seven tuned from 35M to 2.4B, and 4B and 10B with predicted hyperparameters". |
| audit-1 | P6 | 164 | SDP 1B rows relabelled: block forward-masked (B-SDP) 2.437; backward-masked (Bb-SDP) 2.437; neuron forward-masked (N-SDP) 2.434. |
| audit-1 | P7 | 76 | "3× to 40× our size" became "1.3× to 9× our 46M total parameters (inference)". |
| audit-1 | P8 | 98, 106 | L98: "(20, 10 or 5 rounds; inference: 640 optimizer batches ÷ K, Table 7)"; L106: "5 to 20 rounds (inference)". |
| audit-1 | P9 | 113 | "about 480 to 12 rounds at 150M (inference)". |
| audit-1 | P10 | 113, 116 | L113: "(1/M of the compute, a quarter here)". L116 was already inside "(inference, 01)", so it was left as is. |
| audit-1 | P11 | 123 | "(about 48 rounds, inference)" and "our further 3 points (inference)". |
| audit-1 | P12 | 143 | "about 3,200 sequential steps (inference)". |
| audit-1 | P13 | 146 | "about 12.5 rounds at the 256-step period (inference)". |
| audit-1 | P14 | 174 | "(2212.07571, Table 2, v1; inference)". |
| audit-1 | P15 | 226 | "8× the parameters at equal compute (Table 1 totals; inference)". |
| audit-1 | P16 | 246 | "10× our characters (inference)". |
| audit-1 | P17 | 266 | "about 400× our training characters (inference)". |
| audit-1 | P18 | 267 | "the 0.26 bits per character (inference)". |
| audit-1 | P19 | 253 | Reworded to "10M active parameters and up, to 6.6B total" (notes could not be edited to record §3 as read). The same wording was applied to row C6 (L558, "10M-300M active"). |
| audit-2a | P1 | 298 | "about 10M active" became "about 14.2M active". |
| audit-2a | P2 | 302 | "~10M active" became "~14.2M active". |
| audit-2a | P3 | 321 | "~10M active" became "~14.2M active". |
| audit-2a | P4 | 287 | The FoMoE cost-figures handling cell now carries "(inference, 06: relative cross-entropy gap of 2 holders against full replica, fixed placement, M = 4, FoMoE Table 6, v2)". |
| audit-2a | P5 | 305, 306, 310, 311, 312 (note 314) | Note under the 3.1 table replaced: round counts are 01's estimates (total steps ÷ H, inference) except DiLoCo's stated 128, with each input's locator. |
| audit-2b | P1 | 368 | DeepSeek-V2 "236B" replaced by "large production MoE" (the abstract is not in 06's read status, and notes could not be edited). |
| audit-2b | P2 | 374 | The FedAlign-MoE MMLU clause moved inside "(inference from Tables I-II, v2)". |
| audit-2b | P3 | 374 | FLEx sentence reworded: "advantage over MoE + FedAvg (FLEx freezes the experts and does not average them) ... (inference from 2506.00965, Table 2, v2)". |
| audit-2b | P4 | 374 | FLEX-MoE "7 to 11 points (inference from Table I, v2)". |
| audit-2b | P5 | 399 | Aux-loss-free sentence reworded: largest value in the sweep (§2.2, Fig. 2); sigmoid baseline 1e-3 as a trade-off (§4.1); best softmax coefficient 3e-4 (App. C.2). |
| audit-2b | P6 | 405 | "about 70% ... about 28M expert parameters" became "about 54%: the shared 3.58M plus 4 of 8 experts, that is 21.2M of the 42.47M expert parameters (inference; SwiGLU, three matrices, 92% of 46.05M)". |
| audit-2b | P7 | 412 | "at most 75 local steps (inference: 1,200 examples at batch 16, one epoch; App. A)". |
| audit-2b | P8 | 416 | Table lead-in (L407) now says every value in the last column, except the raw values shown for PVT and for SDP on CIFAR, is computed by 03 (inference). |
| audit-2b | P9 | 417 | Covered by the same L407 lead-in change. |
| audit-2b | P10 | 424-428 | Note added under the table: Filippova's fractions, holder counts and shares, and Ro's share, are computed by 03 (inference); ours is from the header. |
| audit-2b | P11 | 430 | "≈ 70% (inference)" became "≈ 54% (inference)". |
| audit-2b | P12 | 432 | Reworded per coordinator (a): fraction ≈54% matches the 1/4 row (≈52%, −0.1%); share 1/2 matches the 1/2 row (−1.6%); both at or below zero, so +1.4% is above them; holder count matches the 1/16 row (+4.3%). |
| audit-2b | P13 | 453 | "3.7 and 8.7 accuracy points (inference from Table 4)". |
| part-a | 1 | 572 | SPES cell now gives the raw averages: "50.95 against 50.02 for centralized and 49.79 for DiLoCo". |
| part-a | 2 | 573 | "(20, 10, 5 rounds; inference from 640 optimizer batches, Table 7)". |
| part-a | 3 | 585 | "−0.6% to −0.7% in loss (inference; 2.437 and 2.434 against 2.452)". |
| part-b | 1 | 494 | Now "Every one with a stated training budget ... (inference, 05)"; combined with part-b 2 and audit-4 P2. |
| part-b | 2 | 494 | Pass counts labelled "(inference, 05)"; endpoints named (1.07 adaptive span, 1905.07799 Table 1; 1.29 an SMoE with k = 2 in S2MoE, 2503.23007 Table 1); "headline (best-configuration)" added. |
| part-b | 3 | 496 | D3PM: "passes are an inference from App. B.2". |
| part-b | 4 | 504 | "(05)" became "(inference, 05)". |
| part-b | 5 | 517 | "(about 18 passes, inference)". |
| part-b | 6 | 523 | "27 to about 1,456 passes (inference)". |
| part-b | 7 | 525 | "+0.03 (2.6%, inference)". |
| part-b | 8 | 526 | "0.02 worse (1.08 against 1.10) without dropout at about 18 passes (Table 4, v3; inference)". |
| part-b | 9 | 529 | "by at most 0.03 (1.08 to 1.11), except S-BASE (1.17 and 1.32) (Tables 4 and 10, v3; inference)". |
| part-c | P-C1 | 544 | "2× to 3× the communication" became "Synchronizing optimizer states roughly triples the data sent (DiLoCo Supp. §6.1, v3); averaging only the first moment would double it (inference)". |
| part-c | P-C2 | 546 | "0.6B active and above" became "1B total parameters and above (0.6B active in Demons; aux-loss-free gives only total sizes)". |
| part-c | P-C3 | 541 | Streaming DiLoCo: "(Table 6), data parallel 3.51 (Table 5) (v1)". |
| part-c | P-C4 | 546 | Gopinath locator "(Table 9 and §5.2, v2)". |
| audit-3d | P-D1 | 553 | BTX: "47.9 against 43.4 average for BTM, both top-2, +4.5 points (Table 2, v1; inference)". |
| audit-3d | P-D2 | 553 | **Applied with adaptation.** The old "+0.50" lower bound was wrong, as the audit says. The proposed "+0.17" is Fisher's Table 1 row, which section 7 lists as read by row order only and not used. So the range covers the three confirmed rows: "+0.44 to +0.88 ... weight averaging +0.50 (Table 1), RegMean +0.44 and WUDI +0.88 (Table 7) (v1; inference); the other three Table 1 rows are read by row order only (section 7); full fine-tuning +0.27 (Table 7)". |
| audit-3d | P-D3 | 555 | MedMix: "full method 0.530 against 0.523 average F1 (+0.007); the similarity-based expert aggregation alone adds +0.001, 0.529 to 0.530 (Table 3 and ablation prose, v1; inference)". |
| audit-3d | P-D4 | 557 | σ-MoE enwik8: "1.09 against 1.08 bits per character (Table 4, v3)". |
| audit-3d | P-D5 | 560 | QSR: "Local AdamW on ViT-B gains +1.12% (16 GPUs) and +0.84% (64 GPUs) ...; ResNet results described as consistent improvements". |
| audit-3d | P-D6 | 551, 598 | B9: Khaled locator "(theory, abstract, v2)"; caveat replaced with the Khaled Table 4 sweep (best at lr 0.5, 16.63, against 19.21 at 1.0; nothing above 1; only Horoi tunes above 1). Gap 2: "(Horoi et al. tuned plain outer SGD to lr 1.6; Khaled et al.'s theory says it should sometimes exceed 1, though their own SGD sweep was best at 0.5)". For consistency, also L319 ("can be larger than 1", with the same qualifier) and L120 ("Theory (abstract)"). |
| audit-3d | P-D7 | 600 | "subword models of 35M and above: dense in the DiLoCo family, MoE in SPES (1B, Table A5) and FoMoE (54M, Tables 3-6)". |
| audit-3d | P-D8 | 597 | "~10M-active" became "~14M-active". |
| audit-3d | P-D9 | 601 | "fraction about 70%" became "fraction about 54%". |
| audit-3d | P-D10 | 624 | "about 10M and 46M" became "about 14M (matching active parameters) and 46M". |
| audit-3d | P-D11 | 553 | Router KD locator "(§5.4, prose, v1)"; L487 also corrected from §4 to §5.4. |
| audit-3d | P-D12 | 554 | KALAVAI: "(§4.4 and Table 5, v2: +17.0% against +14.7% at 20,000 steps)". |
| audit-4 | P1 | 289, 104 | L289 handling: "**Unresolved** (section 7); 06 infers they are probably not seed spreads" (coordinator d). L104: "The paper calls its "±" values per-dataset spreads in §5 and per-seed spreads in App. F, so whether they are seed spreads is unresolved (section 7)". 06's ratio inference moved to section 7's FoMoE item. |
| audit-4 | P2 | 494 | "Every one with a stated training budget (Transformer-XL's is not stated; section 7)". |
| audit-4 | P3 | 497 | "Both were early-stopped; their training length and test-time state handling are not stated (section 7)" (early stopping is recorded by 05). Section 7's Cooijmans and Krause entries gain "whether the test sequence is scored with carried state". |
| audit-4 | P4 | 500 | "protocol-matched" became "chunk-length-matched (overlap not stated; section 7)". |
| audit-4 | P5 | 526 | "converged models" became "longer-trained models ... (training length not stated, section 7)". |
| audit-4 | P6 | 111, 127 | Coordinator (b): both citations became "preprint (venue: see section 7)"; section 7's venue list gains both (NeurIPS 2025 per OpenAlex DOI records, not confirmed in the paper). |

## 2. Coordinator decisions

| Decision | Where | What changed |
|---|---|---|
| a. Parameter counts | header; L28, 76, 106, 137, 157, 298, 302, 321, 405, 430, 432, 500, 517, 587, 597, 601, 624 | Header bullet "Parameter counts" added. Every 10M-active, 28M, 61% and 70% figure replaced. D3PM "about 7×" became "about 5×" (inference; the sentence notes it uses the header's count). Section 5 Chorus row "~14.2M active". |
| b. OpenAlex venues | L111, L127; section 7 | See audit-4 P6. |
| c. FoMoE "Table 3" | L290; section 7 | Row resolved with the coordinator's wording. Not listed as an open FoMoE item; one resolved line added under section 7 "Status differences between strands", following the holder-count precedent. |
| d. FoMoE "±" | L289, L104; section 7 | See audit-4 P1. The summary does not mention ±, so it needed no change. |
| e. SMoE-Dropout Fig. 5b | L291, L397; section 7 | The disagreement row now points to section 7 ("Unresolved (section 7). Not used"). L397 sentence replaced by a pointer. Full description added to section 7 "Values from garbled tables or figures, not used". |
| f. Filippova inner state | L156; section 7 | Entry 7: "inner optimizer state handling not stated (section 7)". Section 7 "Measurement definitions" gains the item. |
| g. Audit-4 "missing from section 7" | section 7 | M1: SMoE-Dropout (see e). M2: FoMoE Table 3, resolved, recorded as in c. M3: Filippova (see f). M4: FedMoE local steps and rounds, HFedMoE data partition, FedCoE client count, Mixtral data and upcycling (measurement definitions); Symphony-MoE venue (venues); SPES 1B node count (SPES items); Clark Recommendation 1 symbol, EPM Table 1, SMALLTALK Tables 4-5, DEPT Tables 15/17/21, DiPaCo Table 4, plot-only figures (OLMoE 6, 9-11; DeepSeekMoE 3-4; MoE-DisCo 7; SMALLTALK 4-5; Switch App. D 12; adaptive span 3) (garbled or figures); NMoE and FC-MoE (federated leads). |

## 3. Locator corrections, observations and advisories applied

| Source | Line before | What changed |
|---|---|---|
| audit-1 locator | 29 | Streaming DiLoCo "Tables 5 and 6" (also L309 table cell and L322). |
| audit-1 locator | 39, 224 | BTM "Tables 1 and 4" / "(Table 4) against ... (Table 1)". Same fix at L376 ("Tables 1 and 4"). |
| audit-1 locator | 214 | HARC: "(§1; the layer is from the results discussion of Fig. 4a)". |
| audit-1 locator | 27 | "a Nesterov outer step at lr 1.0". |
| audit-2a O1 | 309, 322 | Streaming DiLoCo data-parallel 3.51 attributed to Table 5. |
| audit-2a O2 | 323 | INTELLECT-1 locator "§3.1, v1". |
| audit-2a O3 | 290 | Applied via coordinator (c). |
| audit-2a O4 | 294 | EMO read status "§3, §4, §5.1, §5.2 and the start of §5.3". |
| audit-2a O5 | 291 | No change was needed; the row was replaced anyway under coordinator (e). |
| audit-2a O6 | 318 | Woodworth "§2 and §5, v2". |
| audit-2a O7 | 319 | Khaled A.1.3 qualifier "for momentum-based outer optimizers". |
| audit-2b side note | 446 | Filippova: "'required almost 50% more tokens to match' the smaller-slice runs; at 37B tokens it reached 12.68, against 12.75 for full training at 26B". Same correction to the quote's object at L154. |
| audit-2b side note | 399 | "at about 1B and above". |
| audit-2b side notes | 352, 343 | No change (352 needs a notes edit; 343 is fine as written). |
| part-a minor | 469 | BTM "(inference from Tables 1 and 4)". |
| part-a minor | 474 | KALAVAI "(Table 4; 3× from §4.6)". |
| part-a minor | 575 | BTX "averaged uniformly over the 3 domain branches and the seed model". |
| part-a minor | 572 | SPES H: "(2B, 7B, 9B; 50 after 70% of tokens for 2B and 7B)". |
| part-b minor | 515 | "Relative changes are 05's arithmetic (inference)". |
| part-b minor | 517 | Clark locator "§1, §2, App. A, v2"; ST-MoE "§9". |
| part-c obs | 320, 544 | Photon reset statement "App. A, v2". |
| part-c obs | 542 | SDP CIFAR-100 row named "backward-masked (Bb-SDP)". |
| part-c obs | 543 | DARE no longer attributed to Decoupled DiLoCo; App. D.2's comparison of TIES-Merging, Iso-C and sparsity-aware merging added, with direct averaging and RDA ahead of Iso-C. |
| part-c obs | 540, 544 | DiLoCo "150M" left as is (implicit but reasonable). |
| audit-3d obs | 548 | FoMoE fixed against random: "best trade-offs (§6.1); cell by cell the sign varies, e.g. 112.00 against 113.65 at K = 32 but 119.53 against 114.88 at K = 64". IST "3-layer FC network". |
| audit-3d obs | 553 | BTX freezing contrast "34.6 without load balancing against 34.7 without load balancing and with experts frozen, at 10B fine-tune tokens (Table 5, v1)". |
| audit-3d obs | 555 | FedAlign-MoE "Switch fine-tuning on AGNews". |
| audit-3d obs | 620 | "(inference, 01)" added. |
| audit-4 A1 | 30, 311, 312 | DES-LOC "Fig. 5 legend, v1; section 7" in the summary and the 3.1 table rows. |
| audit-4 A2 | 106 | "assuming two matrices per expert". |
| audit-4 A3 | 476 | "MetaMoE and DistMoE, read at abstract level". |
| audit-4 A4 | 241 | Not changed: an arXiv comment is author metadata on the arXiv record; coordinator (b) scoped the venue rule to OpenAlex and DOI records. |
| audit-4 A5 | 353 | Mixtral: OLMoE suggests upcycling; Lo et al. point to "specific initialization schemes". |
| audit-4 A6 | 557 | Same as P-D4. |

## 4. Notes files

A correction line was inserted directly under the first heading of 01, 02a, 03, 05 and 06, the five notes that state 10M or 10-11M active, 28M, 61% or 70% for our model. Each of these files grew by exactly one line, and nothing else in them changed. 02b, 04a and 04b state none of these figures and were not touched.
