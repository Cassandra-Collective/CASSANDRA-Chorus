# Audit 3, part B: report §3.6 (lines 490-530)

Report: docs/research/2026-10-11-stage0-literature-report.md. Raw text: scratchpad/papers/q6/<ID>/paper.txt unless stated; q2a/2605.11689 for Slicing and Dicing. All raw files carry the arXiv stamp of the version the report cites. Our numbers checked against docs/stage0-report.md (centralized 1.4388/1.4386/1.4353, mean 1.4376; full averaging +6.1%; 163.8M characters; seeds within 0.0035; lr 10⁻³, decay over last 20%; balance 0.01; width 384, 8 experts, k = 2, context 256).

## 1. Counts by class

| Class | Items |
|---|---|
| OK-raw | 50 |
| OK-inference | 21 |
| OK-ours | 24 |
| PROBLEM | 9 |
| NOTES-ONLY | 0 |

A range ("15 to 800 times", "27 to about 1,456 passes") counts as one item. Repeats of the same value on another line count again.

## 2. PROBLEM list

All nine are "derived but unlabelled": the inputs are in raw text inside the read sections and the arithmetic reproduces, but the sentence or table carries only a notes tag "(05)" or nothing, not "(inference ...)". No number in this part was missing from raw text, outside the read sections, wrong in value, or from the wrong version.

| # | Line | Exact text | What is wrong | Proposed fix |
|---|---|---|---|---|
| 1 | 494 | "every one used 15 to 800 times our 0.164B training characters" | Ratio derived by 05 (S2MoE 100k × 48 × 512 = 2.46B, /0.164B = 15.0; D3PM 1M × 512 × 256 = 131B, /0.164B = 800). Tag is "(05)" only. Also "every one" includes Transformer-XL (1.08), whose budget is not stated (05 comparison table). | "every one with a stated budget used 15 to 800 times ... (inference, 05)". |
| 2 | 494 | "that is 27 to about 1,456 passes over the data against our 1.8 (05)" | Pass counts derived (2.46B / 90M = 27.3; 131B / 90M = 1,456). Unlabelled. | Change "(05)" to "(inference, 05)". Name the endpoints' sources too: 1.07 is adaptive span large (1905.07799, Table 1, v2), 1.29 is S2MoE SMoE k = 2 (2503.23007, Table 1, v1). Wording: "every published autoregressive transformer result" is too strong, because S2MoE's own Table 1 also prints 1.30 (SMoE k = 1) and 1.33 to 2.33 (SMoE-Dropout rows) on text8. Say "every headline (best-configuration) result". |
| 3 | 496 | "**1.23** after about 1,456 passes" | Pass count derived (1M steps × batch 512 × 256 / 90M, from App. B.2 and §5.1). Unlabelled. The 1.23, 12-layer and ~70M values are raw. | "after about 1,456 passes (inference from App. B.2)". |
| 4 | 504 | "about the gain from a 5× to 7× larger model or one architecture generation at the same size (05)" | Size ratios derived (T64 219M / T12 41M = 5.3; Transformer-XL 277M / 41M = 6.8). Only "(05)". | Change "(05)" to "(inference, 05)". |
| 5 | 517 | "At 41M on enwik8 (about 18 passes)" | Pass count derived (100k steps × batch 32 × context 512 = 1.64B, /90M = 18.2; inputs in §6 and App. B Table 8). Unlabelled. 41M and 25% are raw (Table 3). | "(about 18 passes, inference)". |
| 6 | 523 | "every published transformer row with a stated budget used 27 to about 1,456 passes" | Same derived pass counts as #2. The table header carries only "(05)". | Append "(inference)" to the cell. |
| 7 | 525 | "T64 at 256 against 512: +0.03 (2.6%) at convergence (Al-Rfou Table 2)" | Difference and percentage derived from Table 2 test 1.16 and 1.13 (0.03 / 1.16 = 2.59%). This table has no inference note. The §3.6 comparison table's "Relative changes are 05's arithmetic" does not cover it. | "+0.03 (2.6%, inference)". |
| 8 | 526 | "σ-MoE's Switch was 0.02 worse without dropout at 18 passes (Table 4)" | 0.02 = 1.10 − 1.08 (σ-MoE Table 4, E8 column) and 18 passes are both derived. The cell's own "(inference)" is in the "Likely direction" column, not in the evidence. | "0.02 worse (1.08 against 1.10) without dropout at about 18 passes (Table 4, v3; inference)". |
| 9 | 529 | "σ-MoE's routing variants moved enwik8 results by at most 0.03 except S-BASE" | Spread derived: the E8 column of Tables 4 and 10 runs 1.08 to 1.11 outside S-BASE (1.17, 1.32). Unlabelled and with no locator. | "by at most 0.03 (1.08 to 1.11), except S-BASE (1.17 and 1.32) (Tables 4 and 10, v3; inference)". |

### Minor notes (not counted as PROBLEM)

- **Line 515, the table note.** "Relative changes are 05's arithmetic." I accepted this as the table's stated inference note: it says plainly that the column was computed by researcher 05. All six values reproduce. For consistency with the header convention, it could read "Relative changes are 05's arithmetic (inference)."
- **Line 517, Clark et al. locator "§1, §4".** §1 holds the claim ("across all sizes", Fig. 1). The numbers sit elsewhere: 15M is in App. A (model table) and App. F.1, and 130B tokens is in §2 ("Training Details") and App. F.1. All of these were read (note 05). Suggested locator: "(§1, §2, App. A, v2)".
- **Line 517, ST-MoE quote "vanish, or even reverse" (§7).** This is not a number. In the v2 raw text the paragraph "Generalizing findings from small to large scale" sits under "9 DISCUSSION" (raw line 1432; §9 starts at line 1391), not §7 "Tracing Tokens". Notes 02a and 05 also say §7, so the paragraph was read but mis-numbered. Suggested locator: §9.
- **Line 494, endpoints.** 1.07 and 1.29 are raw values inside the read sections, but the report names neither paper. See PROBLEM #2 for the locator fix.

## 3. OK table

| Line | Number | Paper | Class | Where found |
|---|---|---|---|---|
| 492 | about 1.44 bpc | ours | OK-ours | stage0-report §3.3 (mean 1.4376) |
| 494 | 1.07 | Adaptive span 1905.07799 v2 | OK-raw | Table 1, large 24-layer, test 1.07 (§3, read) |
| 494 | 1.29 | S2MoE 2503.23007 v1 | OK-raw | Table 1, text8, SMoE k = 2 (§4.2, read) |
| 494 | 0.164B characters | ours | OK-ours | stage0-report: 20,000 × 32 × 256 = 163.8M |
| 494 | our 1.8 passes | ours | OK-ours | 163.8M / 90M = 1.82 |
| 495 | 512 characters of context | Al-Rfou 1808.04444 v2 | OK-raw | "Evaluation": "a context of 512 characters" (full text read) |
| 495 | 32k windows | Longformer 2004.05150 v2 | OK-raw | §4.2: "length 32,256 ... step of size 512" (read) |
| 496 | 256-character chunks | D3PM 2107.03006 v3 | OK-raw | §5.1: "chunks of length 256" |
| 496 | 12-layer | D3PM v3 | OK-raw | Table 1 caption: "standard 12-layer transformers" |
| 496 | ~70M | D3PM v3 | OK-raw | App. B.2: "12 layers and 70 million parameters"; the decoder has "the same number of parameters" (read) |
| 496 | 1.23 | D3PM v3 | OK-raw | Table 1, "Transformer decoder (ours) 256 1.23" |
| 497 | 1.43 | Cooijmans 1603.09025 v5 | OK-raw | Table 3, LSTM (ours) 1.43 (§5.3, read) |
| 497 | 2,000-unit | Cooijmans v5 | OK-raw | §5.3: "LSTMs with 2000 units" |
| 497 | 1.40 | mLSTM 1609.07959 v3 | OK-raw | Table 2, "unregularised mLSTM (RMSprop) 1.40" (§4.3, read) |
| 498 | about 2 passes | ours | OK-ours | our budget |
| 500 | 1.4376 | ours | OK-ours | stage0-report: (1.4388 + 1.4386 + 1.4353) / 3 |
| 500 | 1.23 | D3PM v3 | OK-raw | Table 1 (as above) |
| 500 | 0.21 | inference (05) | OK-inference | 1.4376 − 1.23 = 0.2076 |
| 500 | 16.9% | inference (05) | OK-inference | 0.2076 / 1.23 = 16.88% |
| 500 | about 7× active parameters | inference (05) | OK-inference | 70M / ~10M ≈ 7 |
| 500 | 800× data | inference (05) | OK-inference | 131.07B / 0.16384B = 800 |
| 502 | length 256 | Shortformer 2012.15832 v2 | OK-raw | Table 1 (§3, read) |
| 502 | 18.86 | Shortformer v2 | OK-raw | Table 1, L = 256, sliding stride 1 (dev). The PDF table is garbled; rows mapped by order, confirmed by the last row 18.65 = baseline in text |
| 502 | 21.45 | Shortformer v2 | OK-raw | Table 1, L = 256, non-overlapping |
| 502 | 4.38% | inference (05) | OK-inference | (ln 21.45 − ln 18.86) / ln 18.86 = 0.12868 / 2.93704 = 4.381% |
| 502 | 1.205 | inference (05), from Al-Rfou Table 2 | OK-inference | (32 × 1.34 + 32 × 1.26 + 64 × 1.20 + 128 × 1.16) / 256 = 308.48 / 256 = 1.205; inputs are raw Table 2 test values (labels shifted one row in pdftotext; 512 → 1.13 matches Table 1) |
| 502 | +0.045 (+3.9%) | inference (05) | OK-inference | 1.205 − 1.16 = 0.045; 0.045 / 1.16 = 3.88% |
| 502 | +0.075 (+6.6%) | inference (05) | OK-inference | 1.205 − 1.13 = 0.075; 0.075 / 1.13 = 6.64% |
| 502 | +6.1% | ours | OK-ours | stage0-report line 161 |
| 502 | about 6.3% to 6.5% | inference (05) | OK-inference | 0.0877 / 1.39 = 6.31%; 0.0877 / 1.34 = 6.54% |
| 504 | 5% allowance | ours (criterion) | OK-ours | project criterion |
| 504 | 1.4376 | ours | OK-ours | as above |
| 504 | 0.072 | inference (05) | OK-inference | 0.05 × 1.4376 = 0.0719 |
| 508 | 41M (T12) | Al-Rfou v2 | OK-raw | Table 1 row "44 41 1.18" (inference count); text: "T12 with 41M parameters" |
| 508 | 219M (T64) | Al-Rfou v2 | OK-raw | Table 1 row "235 219 1.13" |
| 508 | 1.18, 1.13 | Al-Rfou v2 | OK-raw | Table 1; text: "1.18 bpc", "1.13 bpc" |
| 508 | 4.2% | inference (table note) | OK-inference | 0.05 / 1.18 = 4.24% |
| 509 | 41M, 277M | Transformer-XL 1901.02860 v3 | OK-raw | Table 2: "12L ... 41M 1.06", "24L ... 277M 0.99" (§4.1, read) |
| 509 | 1.06, 0.99 | Transformer-XL v3 | OK-raw | Table 2 |
| 509 | 6.6% | inference (table note) | OK-inference | 0.07 / 1.06 = 6.60% |
| 510 | 38M | Adaptive span v2 | OK-raw | Table 1, Adaptive-Span (S = 8192) 12 layers, 38M |
| 510 | 1.18, 1.11 | Adaptive span v2 | OK-raw | Table 1: T12 test 1.18; adaptive span small test 1.11 |
| 510 | 5.9% | inference (table note) | OK-inference | 0.07 / 1.18 = 5.93% |
| 511 | 1.43, 1.36 | Cooijmans v5 | OK-raw | Table 3, LSTM 1.43, BN-LSTM 1.36 |
| 511 | 4.9% | inference (table note) | OK-inference | 0.07 / 1.43 = 4.90% |
| 512 | context 256 vs 512 | Al-Rfou v2 | OK-raw | Table 2 context column |
| 512 | 1.16, 1.13 | Al-Rfou v2 | OK-raw | Table 2 test column, contexts 256 and 512 |
| 512 | 2.6% | inference (table note) | OK-inference | 0.03 / 1.16 = 2.59% |
| 513 | 41M | σ-MoE 2310.10837 v3 | OK-raw | Table 3, Enwik8, Dense 41M and σ-MoE 41M (§6.3, read) |
| 513 | 1.08 against 1.08 | σ-MoE v3 | OK-raw | Table 3: "Dense 41M 100.0% 1.08", "σ-MoE 41M 25.0% 1.08" |
| 513 | 0% | inference (table note) | OK-inference | identical values |
| 515 | 0.072 | inference (05) | OK-inference | as line 504 |
| 515 | 1.8 passes | ours | OK-ours | as above |
| 515 | 15M | Clark 2202.01169 v2 | OK-raw | App. F.1: "15M with no routing ... still far from having saturated" (read) |
| 515 | 130B tokens | Clark v2 | OK-raw | §2: "250,000 steps, i.e. 130 billion tokens"; F.1: "despite being trained for 130 billion tokens" |
| 515 | 35M | Scaling laws 2503.09799 v1 | OK-raw | Table 4, first row 35M (§4 Finding 1, read) |
| 515 | +2.0% (4 workers) | Scaling laws v1 | OK-raw | Table 4: "3.554 (+2.0%)", M = 4; printed by the paper, not derived |
| 515 | +3.9% (8 workers) | Scaling laws v1 | OK-raw | Table 4: "3.621 (+3.9%)", M = 8 |
| 515 | under 5% | ours (criterion) | OK-ours | project criterion |
| 517 | about 10M active | ours | OK-ours | Stage 0 setup |
| 517 | 15M dense base | Clark v2 | OK-raw | App. A table "15M 512 6 ..."; App. F.1 (read). Locator note in §2 |
| 517 | 130B tokens | Clark v2 | OK-raw | §2, App. F.1 (read). Locator note in §2 |
| 517 | 41M | σ-MoE v3 | OK-raw | Table 3 |
| 517 | 25%-active | σ-MoE v3 | OK-raw | Table 3, "% FLOPs 25.0%" |
| 517 | 4-layer | SMoE-Dropout 2303.01610 v1 | OK-raw | §4.1: "has 4 layers, 256-dimensional" (read) |
| 517 | 2.35% | inference (05) | OK-inference | Table 1: (1.1896 − 1.1623) / 1.1623 = 2.349% (dense with dropout against SMoE (k = N)) |
| 517 | 10M to 20M active | Slicing and Dicing 2605.11689 v1 | OK-raw | §3.1: "At 10M and 20M scales, MoEs consistently fail to outperform dense baselines"; App. C.3 (both read) |
| 517 | 1.8 passes | ours | OK-ours | as above |
| 523 | 1.8 passes, 163.8M characters | ours | OK-ours | stage0-report line 83 |
| 524 | 256-character scoring | ours | OK-ours | stage0-report line 81 |
| 524 | ~0.045 | inference (Al-Rfou Table 2 bound) | OK-inference | labelled "(inference)" in the cell; as line 502 |
| 525 | context 256 in training | ours | OK-ours | stage0-report line 82 |
| 526 | 1.8 passes | ours | OK-ours | as above |
| 526 | mLSTM 1.40 to 1.27 | mLSTM v3 | OK-raw | Table 2: unregularised 1.40; "large mLSTM +emb +WN +VD 1.27" |
| 527 | 1e-3, last 20% | ours | OK-ours | stage0-report line 67 |
| 528 | balance loss 0.01 | ours | OK-ours | stage0-report line 84 |
| 528 | sweep 1e-1 to 1e-5 | Switch 2101.03961 v3 | OK-raw | §2.2: "swept ... from 10⁻¹ to 10⁻⁵ ... found 10⁻² balanced load" (read) |
| 529 | top-2 of 8, width 384 | ours | OK-ours | stage0-report line 82 |
| 530 | seeds within 0.0035 | ours | OK-ours | stage0-report line 166 |
| 530 | 1.062 to 2.482 dev | Al-Rfou v2 | OK-raw | Table 4: "T64 (Baseline) 1.062", "T64 w/out Multiple Positions 2.482" |

The PROBLEM rows' raw inputs were all found: S2MoE App. A Table 3 (512, 48, 100k); D3PM App. B.2 (1M steps, batch 512); σ-MoE §6 and App. B Table 8 (100k steps, batch 32, context 512); σ-MoE Tables 4 and 10, E8 column (Switch 1.08, no dropout 1.10; non-S-BASE range 1.08 to 1.11; S-BASE 1.17 and 1.32); Al-Rfou Table 2 (1.16, 1.13); sizes 41M, 219M and 277M as above.
