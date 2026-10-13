# Audit 3, part C: section 4 remedies table, rows A1 to B4 (report lines 536 to 546)

Scope: line 536 (ranking key; "about 200M parameters" is a ranking criterion, not a paper number, skipped) and rows A1, A2, A3, B1, B2, B3, B4 (lines 540 to 546).
Method: grep -F on raw text under `scratchpad/papers/` (PDF text; HTML text for Khaled Tables 3-5 and FoMoE Tables 4-6 via `r2/2606.19025/tables_v2.txt`); locator checked against the surrounding text; read sections checked against the notes (manifest). Raw-file versions all match the version cited (arXiv stamps checked).
PAPERS = `.../scratchpad/papers`.

## 1. Counts by class

| Class | Count |
|---|---|
| OK-raw | 147 |
| OK-inference | 1 |
| OK-ours | 3 |
| PROBLEM | 4 (2 substantive, 2 locator-only) |
| NOTES-ONLY | 0 |
| Total numbers checked | 155 |

Counting: one per number token (a list such as "H = 30, 60, 120, 240" counts as 4). A number repeated in the same cell (e.g. 2.881 three times in B1) is counted once per row.

## 2. PROBLEM list

**P-C1. Line 544 (B2, caveats column), substantive: derived but unlabelled.**
- Text: "Averaging moments costs 2× to 3× the communication"
- What is wrong: no locator and no "(inference)" label. The raw text supports only about 3×: DiLoCo Supp. §6.1 (v3) says synchronizing inner optimizer states meant "×3 more data to transmit" (q1/2311.08105/paper.txt line ~768). SlowMo App. B.4 says only "an additional call to ALLREDUCE for each buffer averaged" (qualitative). DES-LOC states no such factor. "2×" was not found; it is the researcher's arithmetic (parameters plus one moment tensor = 2×, plus both = 3×). Note 01 line 770 carries "(2× to 3×)" with no source either.
- Fix: write "Synchronizing optimizer states roughly triples the data sent (DiLoCo Supp. §6.1, v3); averaging only the first moment would double it (inference)". Or keep "2× to 3×" and add "(inference: one or two moment tensors per parameter tensor)".

**P-C2. Line 546 (B4, caveats column), substantive: unsupported derived generalization.**
- Text: "Loss numbers only at 0.6B active and above"
- What is wrong: 0.6B active holds for Demons (model "MoE-3.4A0.6B", Table 1, v2). The other loss numbers in the cell come from aux-loss-free balancing, which reports only total sizes ("two model sizes of 1B and 3B total parameters", §4.1, v1, q2a/2408.15664/paper.txt line 240). Its active-parameter count is not stated in the read sections, and Appendix A (Table 5, architecture) was not read and also gives no active count. A 1B-total DeepSeekMoE-style model is very likely below 0.6B active, so the bound is probably wrong as well as unlabelled. Note 02a line 214 states "0.6B active and up" for Demons only.
- Fix: "Loss numbers only at 1B total parameters and above (0.6B active in Demons; aux-loss-free gives only total sizes)".

**P-C3. Line 541 (A2), locator only.**
- Text: "Streaming DiLoCo, 35M, 4 workers: 3.60 at H = 30 against 3.64 at H = 100, data parallel 3.51 (Table 6, v1)"
- What is wrong: 3.60 and 3.64 are in Table 6. The data-parallel 3.51 is not in Table 6; it is in Table 5, the M = 2 table (q1/2501.18512/paper.txt line 1694). Table 5 was read (01 read status: Supplementary Tables 2, 5, 6, 7), and note 01 line 131 attributes it correctly to Table 5. Only the report's locator is wrong.
- Fix: "data parallel 3.51 (Table 5)", or change the locator to "(Tables 5 and 6, v1)".

**P-C4. Line 546 (B4), locator only.**
- Text: "Gopinath et al., 86M: routing-category information 0.1482 at coefficient 0.005 against 0.1148 at 0.01 (Table 9, v2)"
- What is wrong: 0.1482 (λ = 0.005) is in Table 9 (App. G). 0.1148 is not. It is the main model's layer-5 MI, given in §5.2, the abstract and Table 3 (q2a/2608.15102/paper.txt lines 28, 316, 325). The coefficient 0.01 is from the setup ("router load-balancing coefficient of 0.01", line 281). All of these were read (02a: abstract, 3, 4.4, 5.1-5.2, App. G).
- Fix: change the locator to "(Table 9 and §5.2, v2)".

## 3. Observations (not counted as PROBLEM; no number at fault, or the number is OK but context matters)

- **Line 544 (B2): Photon locator.** "Photon resets every round at billion scale (App. B.1, v2)". The "stateless local optimization ... resetting optimizer states each round" text is in Appendix A (HYPER-PARAMETERS prose), not B.1 (B.1 is "Modeling Wall Time"; q1/2411.02908/paper.txt lines 1183-1206). No number is involved. Note 01's read status uses the same B.1 label. Suggested locator: "App. A, v2".
- **Lines 540 and 544: DiLoCo "150M".** The Fig. 6 caption, the §3.1 outer-optimizer paragraph and Supp. §6.1 do not state a model size. 150M is DiLoCo's main model (Fig. 2 caption, Table 2, the Fig. 4 text "for a 150M transformer"), so the attribution is reasonable but implicit. Classified OK-raw.
- **Line 542 (A3): SDP masking variant.** 67.33 at C = 7/8 and 58.73 at C = 3/8 are the **Bb-SDP** row of Table 4 (CIFAR-100, RN-18). The N-SDP and B-SDP rows fall to 9.79 and 7.03 at C = 3/8. The cell does not name the variant, so it understates how badly coverage can hurt. Suggest adding "(Bb-SDP)".
- **Line 543 (B1): Decoupled DiLoCo App. D.2.** It names TIES-MERGING, Iso-C and "sparsity-aware merging schemes", not DARE. It also reports that direct averaging and RDA outperformed Iso-C in its setting, which runs against Horoi's Iso-C gain in the same row. That counter-evidence is worth one clause in the caveats.
- **Garbled tables mapped by row order.** These were mapped the same way as the notes and are consistent with the surrounding prose: SlowMo Tables B.1 and B.3, Fan et al. Table 3, aux-loss-free Table 2 and MaskMoE Table 5.

## 4. OK table

Abbreviations: T = Table; files are relative to PAPERS.

| Line | Number | Paper | Class | Where found |
|---|---|---|---|---|
| 540 | 150M | Khaled 2509.10439 v2 | OK-raw | q1/2509.10439-html/paper_html.txt T3 (Model Size col.) |
| 540 | 4 workers | Khaled | OK-raw | T3 (replicas col. = 4) |
| 540 | 17.75 (plain) | Khaled | OK-raw | T3, H=50, SGD lr 1.0 |
| 540 | 16.38 (Nesterov) | Khaled | OK-raw | T3, H=50, Nesterov lr 1.0 |
| 540 | lr 1.0 | Khaled | OK-raw | T3 |
| 540 | H = 50 | Khaled | OK-raw | T3 |
| 540 | about 2.9% | Khaled | OK-inference | ln17.75 = 2.8764, ln16.38 = 2.7961; (2.8764-2.7961)/2.7961 = 2.87% → 2.9% (labelled "inference") |
| 540 | 178M | Horoi 2607.03011 v1 | OK-raw | q1/2607.03011/paper.txt T2 (178M rows) |
| 540 | 4 workers | Horoi | OK-raw | T2 column R = 4 |
| 540 | H = 30 | Horoi | OK-raw | §4.1 "synchronization interval is fixed at H = 30" |
| 540 | 2.937 | Horoi | OK-raw | T2 DiLoCo SGD, R=4 (line 505) |
| 540 | 2.911 | Horoi | OK-raw | T2 DiLoCo (Nesterov), R=4 (line 506) |
| 540 | 2.881 | Horoi | OK-raw | T2 caption, AdamW DP 178M |
| 540 | 150M | DiLoCo 2311.08105 v3 | OK-raw | main model (Fig. 2, T2); implicit for Fig. 6 (see Observations) |
| 540 | 20M | Async Local-SGD 2401.09135 v2 | OK-raw | §4 Fig. 5 caption "20M language model", quote in §4 |
| 540 | 2.179 | SlowMo 1910.00643 v2 | OK-raw | T B.1 Local Adam original (row order) |
| 540 | 2.137 | SlowMo | OK-raw | T B.1 Local Adam w/ SlowMo |
| 540 | H = 1,000 | Khaled | OK-raw | T3: Nesterov 1.0 18.75 vs SGD 18.18 |
| 540 | H = 2,000 | Khaled | OK-raw | T3: Nesterov 1.0 18.36 vs SGD 18.11 |
| 540 | lr 1.0 (caveat) | Khaled | OK-raw | T3 |
| 540 | outer lr 0.1 | Photon 2411.02908 v2 | OK-raw | Fig. 6 caption "we set ηs = 0.1" (§5.3 area) |
| 540 | 125M | Photon | OK-raw | Fig. 6 caption |
| 540 | 4 clients | Photon | OK-raw | Fig. 6 caption "N = 4 clients per round" |
| 540 | local batch 32 | Photon | OK-raw | §5.3 "Bl = 32 (local batch size)" |
| 540 | K = 128 | FoMoE 2606.19025 v2 | OK-raw | r2/.../tables_v2.txt T5 (DiLoCo) K=128: 507.21/420.49/647.11 vs ≤145.64 at K≤64 |
| 541 | 178M | Horoi | OK-raw | T4 H=30 DiLoCo 2.950 = T2 178M R=8 |
| 541 | 8 workers | Horoi | OK-raw | §4.2 "fixed to R = 8" |
| 541 | 2.950 | Horoi | OK-raw | T4 |
| 541 | 2.957 | Horoi | OK-raw | T4 |
| 541 | 2.976 | Horoi | OK-raw | T4 |
| 541 | 3.008 | Horoi | OK-raw | T4 |
| 541 | H = 30 | Horoi | OK-raw | T4 header |
| 541 | H = 60 | Horoi | OK-raw | T4 header |
| 541 | H = 120 | Horoi | OK-raw | T4 header |
| 541 | H = 240 | Horoi | OK-raw | T4 header |
| 541 | 35M | Streaming DiLoCo 2501.18512 v1 | OK-raw | T6 (Supp., line 1771) |
| 541 | 4 workers | Streaming DiLoCo | OK-raw | T6 M = 4 rows |
| 541 | 3.60 | Streaming DiLoCo | OK-raw | T6, M=4 H=30 |
| 541 | 3.64 | Streaming DiLoCo | OK-raw | T6, M=4 H=100 |
| 541 | H = 30 | Streaming DiLoCo | OK-raw | T6 |
| 541 | H = 100 | Streaming DiLoCo | OK-raw | T6 |
| 541 | 1.1B | OpenDiLoCo 2407.07852 v1 | OK-raw | §3 text and T2 caption |
| 541 | 4 workers | OpenDiLoCo | OK-raw | T2 "4 replicas" |
| 541 | 10.76 | OpenDiLoCo | OK-raw | T2 (in §3, main body) |
| 541 | 11.14 | OpenDiLoCo | OK-raw | T2 |
| 541 | H = 125 | OpenDiLoCo | OK-raw | T2 |
| 541 | H = 500 | OpenDiLoCo | OK-raw | T2 |
| 541 | 10.52 | OpenDiLoCo | OK-raw | T2 "4× batch size with DP" |
| 541 | 1.5B | Factored Gossip 2606.22768 v1 | OK-raw | §5.1 |
| 541 | 8 workers | Factored Gossip | OK-raw | §5.1 |
| 541 | 18.65 | Factored Gossip | OK-raw | prose: §5 "(18.65/15.52 at 10B/30B)"; §6 "28.65 vs. 28.17 ... 23.17 vs. 22.67 ... 19.42 vs. 18.65" |
| 541 | 22.67 | Factored Gossip | OK-raw | §6 prose |
| 541 | 28.17 | Factored Gossip | OK-raw | §6 prose |
| 541 | H = 100 | Factored Gossip | OK-raw | §5-§6 prose |
| 541 | H = 500 | Factored Gossip | OK-raw | §6 prose |
| 541 | H = 1,000 | Factored Gossip | OK-raw | T1 rows "1k" plus §6 (symbol garbled in prose) |
| 541 | 17.53 | Factored Gossip | OK-raw | §5 prose "Sync-DP ... (17.53)" |
| 541 | 1B | SPES 2602.11543 v3 | OK-raw | App. E ablations (1B setting) |
| 541 | H = 50 | SPES | OK-raw | App. E "declines when H increases from 50 to 200 or 400" (line 1204) |
| 541 | 200 | SPES | OK-raw | App. E, Fig. A2 |
| 541 | 400 | SPES | OK-raw | App. E, Fig. A2 |
| 541 | H = 250 | Khaled | OK-raw | PDF A.1.2 "stay stable from H = 250 to H = 2000" (q1/2509.10439/paper.txt line 1126) |
| 541 | 2,000 | Khaled | OK-raw | same |
| 542 | 1.3B | Filippova 2509.22418 v1 | OK-raw | T1 caption |
| 542 | 32 nodes | Filippova | OK-raw | T1 caption |
| 542 | H = 100 | Filippova | OK-raw | §3 setup (line 345) |
| 542 | 14.21 | Filippova | OK-raw | T1, 1/16 mlps |
| 542 | 13.59 | Filippova | OK-raw | T1, 1/8 |
| 542 | 12.72 | Filippova | OK-raw | T1, 1/4 |
| 542 | 12.24 | Filippova | OK-raw | T1, 1/2 |
| 542 | 1/16 | Filippova | OK-raw | T1 |
| 542 | 1/8 | Filippova | OK-raw | T1 |
| 542 | 1/4 | Filippova | OK-raw | T1 |
| 542 | 1/2 | Filippova | OK-raw | T1 |
| 542 | 12.75 | Filippova | OK-raw | T1 Streaming DiLoCo (full-model local training) |
| 542 | 54M | FoMoE | OK-raw | T1 "Small Proxy ∼54M" |
| 542 | 4 workers | FoMoE | OK-raw | T6 M=4 |
| 542 | 1, 2, 4 holders | FoMoE | OK-raw | T6 Oe columns |
| 542 | 143.72 | FoMoE | OK-raw | T6 LocalAdamW, K=128, Fixed, M=4, Oe=1 |
| 542 | 123.50 | FoMoE | OK-raw | T6, Oe=2 |
| 542 | 111.89 | FoMoE | OK-raw | T6, Oe=4 |
| 542 | K = 128 | FoMoE | OK-raw | T6 |
| 542 | 21M | Ro 2204.09715 v2 | OK-raw | T4 "Large Transformer 100% 21.0M" |
| 542 | 32.61 | Ro | OK-raw | T4, 20% |
| 542 | 30.45 | Ro | OK-raw | T4, 40% |
| 542 | 29.15 | Ro | OK-raw | T4, 100% |
| 542 | 20%, 40%, 100% | Ro | OK-raw | T4 trainable % |
| 542 | 67.33 | SDP 2507.09029 v5 | OK-raw | T4 CIFAR-100 RN-18 Bb-SDP, C=7/8 (see Observations) |
| 542 | 7/8 | SDP | OK-raw | T4 |
| 542 | 58.73 | SDP | OK-raw | T4 Bb-SDP, C=3/8 |
| 542 | 3/8 | SDP | OK-raw | T4 |
| 542 | 8 workers | FoMoE | OK-raw | T6 M=8 |
| 542 | K = 128 | FoMoE | OK-raw | T6 |
| 542 | 138.88 | FoMoE | OK-raw | T6 K=128 Fixed M=8 Oe=4 |
| 542 | 159.71 | FoMoE | OK-raw | T6 M=8 Oe=8 (full replica; also T4) |
| 543 | 178M | Horoi | OK-raw | T1 DiLoCo SGD 2.990 = T2 178M R=8 |
| 543 | 2.990 | Horoi | OK-raw | T1 |
| 543 | 2.929 | Horoi | OK-raw | T1 Iso-C |
| 543 | 8 workers, H = 30 | Horoi | OK-raw | §3.2 "R = 8 workers and H = 30" |
| 543 | 2.881 | Horoi | OK-raw | T1 AdamW DP |
| 543 | 4 workers | Horoi | OK-raw | T2 R=4 |
| 543 | 2.864 | Horoi | OK-raw | T2 IsoLoCo R=4 |
| 543 | 2.911 | Horoi | OK-raw | T2 DiLoCo R=4 |
| 543 | H = 240 | Horoi | OK-raw | T4 |
| 543 | 2.991 | Horoi | OK-raw | T4 IsoLoCo H=240 |
| 543 | 3.008 | Horoi | OK-raw | T4 DiLoCo H=240 |
| 543 | 1B | Horoi | OK-raw | T3 caption |
| 543 | 2.421 | Horoi | OK-raw | T3 |
| 543 | 2.450 | Horoi | OK-raw | T3 |
| 543 | 2B-9B | Decoupled DiLoCo 2604.21428 v1 | OK-raw | §5.1/Fig. "2B, 5B, and 9B parameters" (line 791) |
| 543 | 2.997 (TIES) | Horoi | OK-raw | T1 and §3.2 text |
| 543 | 2.993 (DARE) | Horoi | OK-raw | T1 and §3.2 text |
| 544 | 135M | DES-LOC 2505.22549 v1 | OK-raw | §4.1 |
| 544 | 4 workers | DES-LOC | OK-raw | §4.1 "M = 4 workers" |
| 544 | 16 steps | DES-LOC | OK-raw | Fig. 5(a) "Kx = 16" |
| 544 | 12.77 (keep) | DES-LOC | OK-raw | Fig. 5(a) legend FAVG+OPT |
| 544 | 26.77 (reset) | DES-LOC | OK-raw | Fig. 5(a) FAVG-OPT |
| 544 | 12.27 (average) | DES-LOC | OK-raw | Fig. 5(a) Local Adam |
| 544 | 10.20 (DP) | DES-LOC | OK-raw | Fig. 5(a) DDP |
| 544 | 256 steps | DES-LOC | OK-raw | Fig. 5(b) "Kx = 256" |
| 544 | 17.79 | DES-LOC | OK-raw | Fig. 5(b) FAVG+OPT |
| 544 | 17.72 | DES-LOC | OK-raw | Fig. 5(b) FAVG-OPT |
| 544 | 17.22 | DES-LOC | OK-raw | Fig. 5(b) Local Adam |
| 544 | 54M | FoMoE | OK-raw | T1 Small Proxy |
| 544 | 4 workers | FoMoE | OK-raw | T4/T5 M=4 |
| 544 | 104.47 | FoMoE | OK-raw | T4 LocalAdamW M=4 K=64 |
| 544 | 124.17 | FoMoE | OK-raw | T5 DiLoCo (Nesterov) M=4 K=64 |
| 544 | K = 64 | FoMoE | OK-raw | T4/T5 |
| 544 | 150M | DiLoCo | OK-raw | implicit (see Observations); quote in Supp. §6.1 "Inner Optimizer States" |
| 544 | 4.732 (reset) | SlowMo | OK-raw | T B.3 (App. B.4), row order |
| 544 | 2.106 (maintain) | SlowMo | OK-raw | T B.3 |
| 544 | H ≈ 125 | ours | OK-ours | stage0-report line 212 (H = 125) |
| 544 | β2 = 0.95 | ours | OK-ours | stage0-report line 67 |
| 545 | 124M | StableMoE 2204.08396 v1 | OK-raw | §4.1 T1 "# Shared Params 124M" |
| 545 | 454M | StableMoE | OK-raw | same, "# Expert Params 454M" |
| 545 | 6K | StableMoE | OK-raw | §4.1 "60K steps in total (6K for training stage 1" |
| 545 | 60K | StableMoE | OK-raw | same |
| 545 | 20.04 | StableMoE | OK-raw | T5 BASE Layer |
| 545 | 19.41 | StableMoE | OK-raw | T5 + Fixed Routing |
| 545 | 124M | Fan 2402.13089 v1 | OK-raw | setup (lines 62-82) |
| 545 | 9.810 (frozen) | Fan | OK-raw | T3 Layer-wise Frozen, token (row order) |
| 545 | 9.907 (learned) | Fan | OK-raw | T3 Layer-wise Learned, token |
| 545 | 11.752 (re-randomized) | Fan | OK-raw | T3 Layer-wise Random, token |
| 545 | 468M active | MaskMoE 2407.09816 v4 | OK-raw | T1 "Activated Params 468M" |
| 545 | 4 visible | MaskMoE | OK-raw | T5 row "/ 4 4 6.551" (§5.2) |
| 545 | 64 visible | MaskMoE | OK-raw | T5 row "/ 64 64 6.618" |
| 545 | 6.551 | MaskMoE | OK-raw | T5 |
| 545 | 6.618 | MaskMoE | OK-raw | T5 |
| 545 | 32.50 | MoEC 2207.09094 v1 | OK-raw | T3 cluster-level, rate 0.5 |
| 545 | 32.21 | MoEC | OK-raw | T3 rate 0 |
| 545 | 31.53 | MoEC | OK-raw | T3 global-level, rate 0.5 |
| 545 | 50% | MoEC | OK-raw | T3 "0.5" dropout rate (trivial conversion) |
| 545 | 27 characters | ours (text8 alphabet) | OK-ours | text8 = 26 letters + space; labelled "(inference, 02a)" |
| 546 | 3.4B | Demons 2501.11873 v2 | OK-raw | T1 "MoE-3.4A0.6B" |
| 546 | 8.038 | Demons | OK-raw | T1 LBL+sync, BSZ 512 |
| 546 | 8.167 | Demons | OK-raw | T1 LBL, BSZ 4 |
| 546 | 0.008 | Demons | OK-raw | T4 |
| 546 | 0.004 | Demons | OK-raw | T4 |
| 546 | 8.154 | Demons | OK-raw | T4 |
| 546 | 1B | Aux-loss-free 2408.15664 v1 | OK-raw | §4.1, T2 |
| 546 | 3B | Aux-loss-free | OK-raw | §4.1, T2 |
| 546 | 9.56 | Aux-loss-free | OK-raw | T2 (row order) |
| 546 | 9.50 | Aux-loss-free | OK-raw | T2 |
| 546 | 7.97 | Aux-loss-free | OK-raw | T2 |
| 546 | 7.92 | Aux-loss-free | OK-raw | T2 |
| 546 | 86M | Gopinath 2608.15102 v2 | OK-raw | §4.4 "86.4 million" (line 251) |
| 546 | 0.1482 | Gopinath | OK-raw | T9 (App. G) load balancing λ = 0.005 |
| 546 | 0.005 | Gopinath | OK-raw | T9 |
| 546 | 0.01 | Gopinath | OK-raw | setup "load-balancing coefficient of 0.01" (line 281) |
| 546 | 14B | EMO 2605.06663 v2 | OK-raw | §3/§4 "1B-active, 14B-total"; global balancing in §3.3 (line 333) |

Rows marked PROBLEM (not in the OK table): line 541 "3.51" (P-C3); line 544 "2× to 3×" (P-C1); line 546 "0.6B active" (P-C2); line 546 "0.1148" (P-C4).
