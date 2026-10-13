# Audit 2b: report lines 336-456 (sections 3.2 and 3.3)

Status: COMPLETE.

- Report: `docs/research/2026-10-11-stage0-literature-report.md`, lines 336-456 ("### 3.2 Question 2" to the line before "### 3.4").
- Rule checked: every number taken from a paper comes from a part of that paper that was actually read (read status per notes 02a, 02b, 03, 04a, 04b, 06 and the audit3 manifest).
- Raw text: `scratchpad/papers/{q2a,q2b,q3,q4a,q4b,r2}/<ID>/paper.txt` (FoMoE tables: `r2/2606.19025/tables_v2.txt`). Every cited paper had raw text; nothing was downloaded. The arXiv stamp in every raw file matches the version the report cites.
- Arithmetic re-run with `scratchpad/audit/scripts2b/calc.py` (Python -I). Every derived value reproduces within rounding.
- "Lines" below are report line numbers. "raw L" means a line of the paper's raw text.

## Counts by class

The unit is one row of the OK table or one PROBLEM entry. A row can hold several numbers from the same paper and locator.

| Class | Count |
|---|---|
| OK-raw | 58 |
| OK-inference | 12 |
| OK-ours | 16 |
| NOTES-ONLY (search counts) | 1 |
| PROBLEM | 13 (3 caused by the known 70% parameter figure; 10 others, all minor) |

## PROBLEM list

| # | Line | Exact text | What is wrong | Fix (corrected wording) |
|---|---|---|---|---|
| P1 | 368 | DeepSeek-V2 row: "236B, synchronous" | Outside the read sections. 06 records only §2.2.2 and the training-hyperparameter paragraph as read. 236B appears in the abstract (raw L10), §1 (L145) and the model-hyperparameter paragraph (L694), not in those two parts. | Either add "abstract" to 06's read status (this audit read raw L10: "236B total parameters, of which 21B are activated") and write "236B total (abstract, v5), synchronous", or drop the size: "large production MoE, synchronous". |
| P2 | 374 | "though its IID MMLU gap is still +4.9 (0.4641 against 0.5131)" | Derived (0.5131 − 0.4641 = 0.049) but placed after the "(inference from Tables I-II, v2)" label, so its own clause has no label. Inputs are correct (Table I, raw L807/L811). | "...+1.6 under IID, and its IID MMLU gap is still +4.9 (0.4641 against 0.5131) (inference from Tables I-II, v2)." |
| P3 | 374 | "FLEx's advantage from not averaging experts is 2.0 ROUGE-L at α = 0.1 and 0.03 at α = 1.0 (... Table 2, v2)" | Derived, no label: 37.30 − 35.29 = 2.01 and 37.54 − 37.51 = 0.03 (Table 2, raw L455/L462). Wording also over-attributes: the comparison is FLEx against MoE + FedAvg, and FLEx also grafts a personal expert. | "FLEx's advantage over MoE + FedAvg (FLEx freezes the experts and does not average them) is 2.0 ROUGE-L at α = 0.1 and 0.03 at α = 1.0 (inference from Table 2, v2)." |
| P4 | 374 | "finds random per-round assignment loses 7 to 11 points to fitness-based assignment on CIFAR-10" | Derived, no label: 79.48 − 72.03 = 7.45 and 83.00 − 72.03 = 10.97 (Table I, raw L318-326). | "...loses 7 to 11 points (inference from Table I, v2) to fitness-based assignment on CIFAR-10..." |
| P5 | 399 | "the largest value in the aux-loss-free sweep, where 1e-3 (sigmoid) or 3e-4 (softmax) was best (App. C)" | 1e-3 is not called best, and it is not in App. C. §4.1 (raw L254) says the sigmoid baseline uses 0.001 "to achieve a reasonable trade-off between model performance and load balance". Only 3e-4 is "the lowest perplexity", for a softmax gate (App. C.2, raw L626). Both values are from read sections. | "...the largest value in the aux-loss-free sweep (§2.2, Fig. 2), whose sigmoid baseline used 1e-3 as a trade-off between quality and balance (§4.1) and whose best softmax-gate coefficient was 3e-4 (App. C.2)..." |
| P6 | 405 | "Each worker trains about 70% of the parameters (inference, 03, using about 28M expert parameters)." | KNOWN PROBLEM. Wrong value: the experts are SwiGLU with three matrices (42.47M of 46.05M parameters). | "Each worker trains about 54% of the parameters: the shared 3.58M plus 4 of 8 experts, that is 21.2M of the 42.47M expert parameters (inference; experts are SwiGLU with three matrices and hold 92% of the 46.05M)." |
| P7 | 412 | Ro et al. row: "at most 75 local steps" | Derived, no label. The paper gives batch 16, at most 1,200 examples and 1 epoch (App. A, raw L536-541); 75 = 1,200 ÷ 16 is not stated. The table note covers only gaps. | "at most 75 local steps (inference: 1,200 examples at batch 16, one epoch; App. A)" |
| P8 | 416 | ResIST row: "CIFAR −0.2 to −0.6 points (once +0.6); ImageNet −1.7 to −1.9 points" | Derived accuracy differences (Tables 2-3, raw L372-385 and L435-441; computed −0.21 to −0.61, +0.62, −1.72, −1.92). The table note at line 407 covers only "gaps in log-perplexity or loss". | Change the note at line 407 to "(partial against full training under the same scheme; every gap in the last column, except the raw values shown for PVT and SDP on CIFAR, is computed by 03 from the cited table (inference))", or append "(inference)" to the cell. |
| P9 | 417 | FedRolex row: "accuracy −1.9% rolling, −8.7% static, −21% random" | Derived relative accuracy gaps (29.22, 27.21, 23.46 against 29.79, Table 3, raw L469-474; computed −1.91%, −8.66%, −21.25%). Not covered by the note at line 407. | Same fix as P8, or "accuracy −1.9% rolling, −8.7% static, −21% random (inference from Table 3)". |
| P10 | 424-428 | Filippova rows: "≈ 67%", "≈ 52%", "≈ 44%", "≈ 40%"; holders "16", "8", "2"; shares "1/2" to "1/16"; Ro's share "≈ 0.4" | Derived, no label. Fractions are trainable parameters per node ÷ 1.3B (0.87, 0.67, 0.57, 0.52 ÷ 1.3 = 66.9, 51.5, 43.8, 40.0%). Holders are 32 nodes ÷ slices; only "4 nodes out of 32" for 1/8 is stated (raw L485). Shares are 1/N. Line 420's "(03)" is a source tag, not an inference label. | Add a note under the table: "Filippova's trainable fractions (trainable parameters per node ÷ 1.3B, Table 1), holder counts (32 nodes ÷ number of slices) and holder shares, and Ro et al.'s share, are computed by 03 (inference); gaps as in the table above." |
| P11 | 430 | "**Ours, partial arm** / **≈ 70% (inference)**" | KNOWN PROBLEM. Wrong value (see P6). | "**≈ 54% (inference)**" |
| P12 | 432 | "By trainable fraction and holder share we match Filippova's 1/2 row, where partial updates beat full averaging, so our cost is above that range." | Follows from P11. At ≈54% our trainable fraction matches Filippova's 1/4 row (≈52%, −0.1%), not the 1/2 row (≈67%, −1.6%). Only the holder share (1/2) still matches the 1/2 row. The conclusion survives, because both rows are at or below zero against our +1.4%. The Ro sentence ("while training a larger fraction") still holds (54% > 40%). | "By trainable fraction (≈54%) we match Filippova's 1/4 row (≈52%, −0.1%), and by holder share (1/2) their 1/2 row (−1.6%). In both, partial updates cost nothing or beat full averaging, so our cost is above that range." |
| P13 | 453 | "and 3.7 and 8.7 accuracy points on CIFAR-10 and CIFAR-100 at coverage 4/8" | Derived, no label: 92.45 − 88.80 = 3.65 and 68.62 − 59.89 = 8.73 (Table 4, raw L1126-1132). | "...and 3.7 and 8.7 accuracy points (inference from Table 4) on CIFAR-10 and CIFAR-100 at coverage 4/8..." |

Known-problem sweep: in lines 336-456 the only figures that depend on "10M active", "10-11M", "28M expert parameters", "61%" or "70%" are P6, P11 and P12. Line 397 ("10M to 20M active", a Slicing and Dicing range) and line 401 ("10M to 50M") do not assert our active count and stay correct at 14.2M active and 46.05M total.

## Side notes (wording, not number provenance; no class assigned)

- Line 446: the paper says 1/8 slicing "required almost 50% more tokens to match the performance of smaller-slice configurations" (raw L485), not full training. The numbers in the parenthesis are correct (12.68 at 37B, raw L523; 12.75 full at 26B, raw L516; 37/26 = +42%). Suggested: "...'required almost 50% more tokens to match' the smaller-slice runs; at 37B tokens it reached 12.68, against 12.75 for full training at 26B".
- Line 352: "one main run per condition" is stated outright only in Gopinath §5.6 (raw L443-445), which is not among the read sections. The abstract ("A replication at a second training seed", raw L37-38) and App. G.1 (read) support it. Acceptable; 02a could add §5.6 to its read status.
- Line 399: "but did at 1B and above (OLMoE Fig. 9; aux-loss-free Fig. 2)". The aux-loss-free experiments are 1B and 3B (§4.1). The model size of OLMoE's balance-loss ablation is not stated in the text read; the ablations are runs "that have led to OLMoE-1B-7B" (§4 opening). "At about 1B and above" would be safer.
- Line 343: Dikkala App. C.4 gives "(70.34% vs 70.27%)" without saying which is the frozen router (raw L829-831). The report does not assign them either, so it is fine as written.

## OK table

| Line | Number(s) | Paper | Class | Where found (raw line; read section) |
|---|---|---|---|---|
| 336 | +3.2% | ours | OK-ours | stage0-report L21, L175 |
| 342 | up to 60% of top-8, after 1%; layer 0 slower | OLMoE 2409.02060 v2 | OK-raw | L1213-1218, §5.1 (read) |
| 342 | around 1K steps | Grouter 2603.06626 v2 | OK-raw | L88, Fig. 1 caption, §2.2 (read) |
| 342 | 15.4% after 80% | StableMoE 2204.08396 v1 | OK-raw | L46-47, §1 / Fig. 2 (read) |
| 342 | 10% of training; −0.63 PPL | StableMoE v1 | OK-raw | L402, L379, L421, §4.4 / Table 5 (read) |
| 343 | 70.34% vs 70.27%; width 32 | Dikkala, EMNLP 2023 (ACL PDF) | OK-raw | L831-833, App. C.4 (read) |
| 343 | GPT-2-small | Fan 2402.13089 v1 | OK-raw | L82, full text |
| 351 | 4 of 64 visible: 6.551 vs 6.618 | MaskMoE 2407.09816 v4 | OK-raw | L474-476, Table 5, §5.2 (read) |
| 351 | 11.752 vs 9.810; dense 11.815 | Fan v1 | OK-raw | L184-185, L69 (scrambled; 02a mapping), full text |
| 352 | 3.4B to 43B | Demons 2501.11873 v2 | OK-raw | L244-245, §4.1 (read) |
| 352 | 86M; 0.1148 at 0.01 → 0.1482 at 0.005 | Gopinath 2608.15102 v2 | OK-raw | L251, L281 (§4.4), L723 (Table 9, App. G) |
| 352 | one main run per condition | Gopinath v2 | OK-raw | abstract L37-38 + App. G.1 (see side note) |
| 356 | layer 0 onto one or two experts | OLMoE v2 | OK-raw | L823-826, §4.1.6 (read) |
| 356 | 3 to 5 of 8 experts (Task B) | ours | OK-ours | stage0-report L84 |
| 358 | 13, 12 queries; 34, 12 citers; 20 arXiv API queries | notes 02a, 02b, 06 | NOTES-ONLY | 02a query log (13); 02b query log (12 WebSearch); 06 citation table (34, 12) and method (20) |
| 362 | 54M; O_e 2 of M = 4; K = 32/64/128 | FoMoE 2606.19025 v2 | OK-raw | tables_v2 L28, L77-89 (Table 6), full text |
| 362 | +1.6%, +2.9%, +2.1% | FoMoE v2 | OK-inference | ln(112.00)/ln(103.91) etc.: 1.61, 2.90, 2.09 |
| 363 | 5.6B, 10B | Gating Dropout 2205.14336 v2 | OK-raw | L305, L394, full main text |
| 363 | +0.46 at p = 0.3; +0.52 at p = 0.2; −0.23 at p = 0.5; p = 1 | Gating Dropout v2 | OK-raw | L325, L394, L442-446, L222-226 |
| 364 | 64 experts; −1.0%, −2.1%, −7.7% | MoEC 2207.09094 v1 | OK-inference | Table 3, L409-412: −1.02, −2.11, −7.70 |
| 364 | +0.29 BLEU at 50% | MoEC v1 | OK-raw | L397 (stated); Table 3 L411 |
| 365 | 468M active; 6.551 vs 6.618 | MaskMoE v4 | OK-raw | L319-339, L474-476 |
| 366 | 47M, 41M; 11.59 vs 12.01; 1.08 both | σ-MoE 2310.10837 v3 | OK-raw | Table 4 L625-626, §6 (read) |
| 367 | 1B active / 14B | EMO 2605.06663 v2 | OK-raw | L357, §4.1 (read) |
| 368 | 3 of 8 devices | DeepSeek-V2 2405.04434 v5 | OK-raw | L709-710 (training-hyperparameter paragraph); §2.2.2 L516 |
| 369 | 7B; 46.7 → 38.8 | FlexOlmo 2507.07024 v4 | OK-raw | L474, L480 (Table 1); L676 (§4) |
| 370 | top-2 (K = 2) | DDOME 2306.08586 v3 | OK-raw | L593, §4 (read) |
| 372 | p ≈ 0.3 | Gating Dropout v2 | OK-raw | L446 |
| 372 | half the experts | ours | OK-ours | 4 of 8 held |
| 374 | +7.8, +3.8, +1.6 points | FedAlign-MoE 2603.21276 v2 | OK-inference | Tables I-II L807-811, L882-886: 0.0782, 0.0377, 0.0161 |
| 374 | 81.51 vs 78.93; 50.60 vs 55.78; α = 0.1 | FedCoE 2605.21264 v1 | OK-raw | L198-212, §III (read) |
| 374 | H = 125 | ours | OK-ours | stage0-report setup |
| 376 | 0.82 × div − 2.72; R² 0.856; six points; 3.3% | KALAVAI 2603.22755 v2 | OK-raw | L14-17 (abstract), L833-904 (§4.10, Table 12 in main body; §1-§7 read) |
| 380 | about half / about a quarter of tokens; 1 to 4 copies | ours | OK-ours | top-2 of 4 versus top-2 of 8; coverage policy |
| 382 | 2 of 4; 2 of 8 | ours | OK-ours | setup |
| 391 | 16-32 tie; 64, 128 beat; 8K; 267K | Hash Layers 2106.04426 v3 | OK-raw | L224, L259-263, L362-370, L478-481, §5 (read) |
| 391 | 15M to 1.3B | Clark 2202.01169 v2 | OK-raw | L572 (§5.3), L879-885 (App. A) |
| 391 | 23.06 vs 24.60 BLEU | Gating Dropout v2 | OK-raw | L350-351, Table 2 |
| 392 | about a quarter (0.0274 vs 0.1148) | Gopinath v2 | OK-inference | 0.0274 / 0.1148 = 0.239; Table 9 L722 |
| 392 | 1.1486 vs 1.1896 bpc | SMoE-Dropout 2303.01610 v1 | OK-raw | L458-461, Table 1 (row mapping by the FLOPs column) |
| 393 | 1.0 to 1.6 points | UniPool 2605.06665 v2 | OK-raw | L45 (abstract), L163-175 (§3, Table 1) |
| 395 | 15M to 1.3B | Clark v2 | OK-raw | as above |
| 395 | 27 characters / 8 experts → 3 or 4 | ours | OK-ours | 27/8 = 3.375 (labelled inference, 02a) |
| 395 | about half its accuracy; almost nothing | ours (Task A) | OK-ours | stage0-report L17, L130 |
| 397 | 10M to 20M active | Slicing and Dicing 2605.11689 v1 | OK-raw | L445, §3.1 (read) |
| 397 | 41M, equal total size | σ-MoE v3 | OK-raw | Table 3 L549-550 |
| 397 | 2.35% | SMoE-Dropout v1 | OK-inference | 1.1896 / 1.1623 − 1 = 2.35% |
| 397 | 8 or fewer experts | SMoE-Dropout v1 | OK-raw | 02a's reading of Fig. 5b (§4.4, read); the report flags it as unresolved |
| 399 | 2B | DeepSeekMoE 2401.06066 v1 | OK-raw | L116, §1 (read) |
| 399 | 6.51 → 6.48 | MaskMoE v4 | OK-raw | L457, Table 3 (with / without shared expert) |
| 399 | 1B and above | OLMoE / aux-loss-free | OK-raw | aux-loss-free §4.1 (1B, 3B); see side note |
| 399 | 3.4B to 43B | Demons v2 | OK-raw | L244-245 |
| 399 | 0.01 default | Switch 2101.03961 v3; OLMoE v2 | OK-raw | Switch L407/L413 (§2.2); OLMoE L829 (§4.1.6) |
| 399 | sweep 1e-2, 1e-3, 1e-4, 0 (0.01 largest) | aux-loss-free 2408.15664 v1 | OK-raw | L149 (§2.2) |
| 399 | 3e-4 best for softmax | aux-loss-free v1 | OK-raw | L626 (App. C.2) |
| 399 | 1e-4 without bias worst | Slicing and Dicing v1 | OK-raw | L711-712, §3.3 (read) |
| 401 | 10M to 50M; 8 experts | ours (unknowns list) | OK-ours | consistent with 14.2M active, 46.05M total |
| 405 | +1.4 (+1.3 to +1.6) | ours | OK-ours | stage0-report L174 |
| 405 | +1.37%; +0.021 bpc | ours (03 arithmetic) | OK-ours | per-seed mean 1.366%; 1.5462 − 1.5254 = 0.0208 |
| 405 | 8 experts, updates 4; 1 to 4 holders; 29.6/44.5/22.2/3.7% | ours | OK-ours | coordinator-verified |
| 411 | 1.3B, 32 nodes, H = 100, 26B; 1/2 to 1/16 | Filippova 2509.22418 v1 | OK-raw | L14, L345, L516-521, full text |
| 411 | −1.6, −0.1, +2.5, +4.3% | Filippova v1 | OK-inference | table note; −1.60, −0.09, +2.51, +4.26 |
| 412 | 21M; 800 clients; 40% / 20% | Ro 2204.09715 v2 | OK-raw | L121, L590-606 (Table 4) |
| 412 | +1.3/+3.3; +1.0/+2.4; +0.65/+1.9% | Ro v2 | OK-inference | 1.29, 3.33, 1.00, 2.40, 0.65, 1.92 |
| 413 | 1,024 clients; 5 local steps; 10% | PVT 2110.05607 v1 | OK-raw | L179-181, full text |
| 413 | 4.8 vs 4.8; 5.0 vs 4.9 | PVT v1 | OK-raw | Tables 2-3 L136-147 (rows mapped by the memory column: AVT 1372MB, PVT 1074MB) |
| 414 | 1B, 8 workers, C = 0.69 | SDP 2507.09029 v5 | OK-raw | L396-398, L1055, full text |
| 414 | −0.6% loss | SDP v5 | OK-inference | 2.437 / 2.452 − 1 = −0.61% |
| 415 | 88.80 vs 92.45; 59.89 vs 68.62; 4/8 | SDP v5 | OK-raw | L1126-1132, Table 4 |
| 416 | ResNet-101; 2 to 8 machines; 15 to 50 steps | ResIST 2107.00961 v2 | OK-raw | L235, L338, L372-385 |
| 417 | 3-layer; 200 clients; 1 to 1/16 | FedRolex 2212.01548 v2 | OK-raw | L387, L412, L427 |
| 418 | up to 19.3M | HeteroFL 2010.01264 v3 | OK-raw | L533 |
| 418 | +4.3% to +8.8% | HeteroFL v3 | OK-inference | ln 3.55 / ln 3.37 etc.: 4.28, 8.79 |
| 428 | 40%; ≈320 of 800 (inference); +1.0 to +1.3% | Ro v2 | OK-inference | 0.4 × 800 = 320 |
| 429 | ≈69%; ≈5.5 of 8 (inference); −0.6% | SDP v5 | OK-inference | 0.69 × 8 = 5.52 |
| 430 | 1 to 4 per round, mean 2; 1/2; +1.4% | ours | OK-ours | coordinator facts; stage0-report |
| 432 | 1/16 row +4.3% | Filippova v1 | OK-raw | Table 1 |
| 432 | about 2 holders | ours | OK-ours | coverage policy |
| 436 | 1/N variance reduction | SPES 2602.11543 v3 | OK-raw | L898, App. A (full text) |
| 437 | minimum holders 1 (coverage), 2 (rolling) | ours | OK-ours | 03 code reading |
| 439, 441 | 125 steps; about 2 trajectories, sometimes 1 | ours | OK-ours | setup |
| 445 | 100% > 40% > 20%; coverage 7/8 to 3/8 | Ro v2; SDP v5 | OK-raw | Table 4; Table 4 L1128-1132 |
| 446 | almost 50% more tokens; 12.68 at 37B vs 12.75 at 26B | Filippova v1 | OK-raw | L485, L516, L523 (see side note) |
| 448 | H = 1 (−0.6%), H = 100 (−1.6 to +4.3%), H = 125 (+1.4%) | SDP / Filippova / ours | OK-inference | labelled (inference, 03) |
| 449 | 200K rounds; 1.3B and 1B | PVT v1; Filippova; SDP | OK-raw | PVT L191-192 (§3.4.1) |
| 451 | H = 50 | SPES v3 | OK-raw | App. B / H ablation L1203-1206 (full text) |
| 453 | 500M (2.72 vs 2.73) and 1B; coverage 0.69 | SDP v5 | OK-raw | L385-386 |
