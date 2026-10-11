# Audit 1: header, section 1 (Summary), section 2 (Reading list, 18 entries)

Report audited: `docs/research/2026-10-11-stage0-literature-report.md`, lines 1 to 270 (up to "## 3. Findings by question").
Rule audited: every number taken from a paper must come from a part of that paper that was actually read.
Auditor: audit agent 1, 2026-10-11. Nothing in the repository was modified.

## Method

- Every number in scope was listed by report line. Paper-attributed numbers were grepped (`grep -F` / a Python `-I` script, `scratchpad/audit1_scripts/grepcheck.py` and spec files `spec1.txt` to `spec9.txt`) in the raw text under `scratchpad/papers/` (pdftotext output, plus arXiv HTML text where the notes say HTML was used). Variants tried: "×" mangled to "�", superscript exponents lost ("4-4" = 4e-4), spaced "M   =  4", line-broken quotes.
- Version stamps checked on every paper.txt (`arXiv:<id>vN`): all 31 files match the version the report says was read (DiLoCo v3, Khaled v2, scaling laws v1, Streaming DiLoCo v1, DES-LOC v1, Ro v2, Filippova v1, SDP v5, SPES v1/v2/v3, FoMoE v1 and v2, Gating Dropout v2, 2212.07571 v1, MoEC v1, Fan v1, Demons v2, FlexOlmo v4, HARC v1, 2609.32821 v1, BTM v1, DiPaCo v1, σ-MoE v3, Slicing and Dicing v1, Al-Rfou v2).
- Locators were checked against section headings / table captions in the raw text, and against the read status recorded in the notes (01, 02a, 02b, 03, 04a, 04b, 05, 06).
- All inference arithmetic was recomputed (`scratchpad/audit1_scripts/arith.py`). Perplexity gaps use ln(a)/ln(b) − 1.
- FoMoE: all 126 "mean ± spread" cells of v1 and v2 were compared as multisets: identical.
- Our own numbers were checked against `docs/stage0-report.md` §3.3, `configs/task_b/centralized.toml`, `cassandra_chorus/model/layers.py` (SwiGLU expert, three bias-free matrices) and RESULTS.md (46,050,432 parameters).
- No paper had to be downloaded; every paper in scope was already in the scratchpad.

## Counts

| Class | Header | Summary | Reading list | Total |
|---|---|---|---|---|
| OK-raw | 0 | 31 | 400 | **431** |
| OK-inference | 0 | 16 | 45 | **61** |
| OK-ours | 20 | 17 | 23 | **60** |
| PROBLEM (items) | 0 | 2 | 17 | **19 items** (about 24 numbers) |

Restated numbers (the same value repeated on another line) are counted on each line where they appear. Version dates, entry numbers, arXiv IDs and process times are excluded.

Of the 19 PROBLEM items, 7 are substantive (a wrong value or wrong label, or an unlabelled derivation in the summary), and 12 are low severity (an unlabelled but correct derivation, or a setting value read outside the recorded sections). Three locator imprecisions that do not break the read rule are listed separately.

## PROBLEM list

### Substantive

**P1. Line 34 (Summary, partial updates).**
Text: "a 1.3B model with local steps ranged from −1.6% to +4.3% as slices shrank (Filippova et al., Table 1, v1)".
Wrong: **derived but unlabelled.** Table 1 of 2509.22418v1 prints perplexities only (12.75, 12.24, 12.72, 13.59, 14.21); the percentages are log-perplexity gaps computed in notes 03. Line 154 labels the same numbers "(inference by 03)"; line 34 does not.
Arithmetic: ln 12.24/ln 12.75 − 1 = −1.60%; ln 14.21/ln 12.75 − 1 = +4.26%. Reproduces.
Fix: "(inference from Filippova et al., Table 1, v1; 03)".

**P2. Line 106 (Entry 3, FoMoE, differences).**
Text: "experts are about 4% of its parameters against about 61% of ours (inference, 06)".
Wrong: **the inference does not reproduce for "ours".** Notes 06 §6 computed ours as 2 × 384 × 768 × 8 × 6 = 28.3M (two matrices per expert). Our experts are SwiGLU with three matrices (`cassandra_chorus/model/layers.py`, `SwiGLUExpert`: w1, w2, w3, no bias): 3 × 384 × 768 × 8 × 6 = 42,467,328 of 46,050,432 = **92.2%**. Check: 42,467,328 + attention 4 × 384² × 6 = 3,538,944 + router 18,432 + untied embeddings 2 × 27 × 384 = 20,736 + norms 4,992 = 46,050,432 exactly. FoMoE's "about 4%" (2,097,152 of 54,358,784 = 3.86%) depends on the same two-matrix assumption, which 06 states.
Fix: "about 92% of ours (inference: SwiGLU experts, 42.5M of 46.05M)". The same 61% figure probably appears in sections 3 to 5 and in notes 06; other auditors should check it.

**P3. Line 157 (Entry 7, Filippova, question).**
Text: "the holder share and trainable fraction (one half and about 70%, like their 1/2 row at −1.6%)".
Wrong: **our derived number is wrong and unlabelled.** A partial-update worker trains the non-expert part (3,583,104) plus 4 of 8 experts (21,233,664) = 24.8M of 46.05M = **about 54%**. The 70% follows from the same two-matrix error as P2: (46.05 − 14.2)/46.05 = 69%. Their 1/2 row trains 0.87B of 1.3B = 67%, so the analogy weakens.
Fix: "one half and about 54% (inference)". Notes 03 (P1 and P4 questions) repeat "about 70%", so section 3 should be checked too.

**P4. Lines 28 and 137 (Summary item 3; Entry 5 question). Our number, outside the strict paper rule, but wrong.**
Text: "we have about 10M active parameters" / "to about 10M active parameters".
Wrong: the active count is 3,583,104 non-expert + 2/8 × 42,467,328 = **14.2M**. The 10.6M figure is only the active expert part. The comparison with Slicing and Dicing (10M and 20M scales) still holds.
Fix: "about 14M active parameters". If "active expert parameters" was meant, say so.

**P5. Line 129 (Entry 5, DiLoCo scaling laws, setting).**
Text: "nine sizes from 35M to 2.4B (4B and 10B predicted)".
Wrong: **wrong value.** Table 3 of 2503.09799v1 lists seven tuned sizes from 35M to 2.4B (35M, 90M, 180M, 330M, 550M, 1.3B, 2.4B), plus 4B and 10B, which makes nine in total ("9 model sizes", §1).
Fix: "nine sizes from 35M to 10B: seven tuned from 35M to 2.4B, and 4B and 10B with predicted hyperparameters".

**P6. Line 164 (Entry 8, SDP, findings).**
Text: "At 1B (Table 1, v5) with coverage C = 0.69: data parallel 2.452; backward-masked variants 2.437 and 2.437; neuron-level forward-masked 2.434."
Wrong: **wrong label on a correct number.** B-SDP is block-level *forward* masking: "the block is skipped and its parameters excluded" (§3.2). Only Bb-SDP is backward-masked ("active during the forward pass but omitted during the backward pass"). The row mapping (B-SDP 2.437 with average 0.457, Bb-SDP 2.437, N-SDP 2.434, "the lowest validation loss of the four") is confirmed by the §4.1 prose. The same entry's CIFAR sentence correctly treats B-SDP (42.68) as forward masking, so the entry contradicts itself.
Fix: "block forward-masked (B-SDP) 2.437, backward-masked (Bb-SDP) 2.437, neuron forward-masked (N-SDP) 2.434".

**P7. Line 76 (Entry 1, DiLoCo, differences).**
Text: "dense, subword, 3× to 40× our size".
Wrong: **derived, unlabelled, mixed basis.** 60M to 400M against our 46.05M total is 1.3× to 8.7×; against our ~14M active it is 4× to 28× (or 6× to 40× against the stated "10M"). The pair "3× to 40×" (notes 01: "3.3× to 40×") mixes 150M/46M with 400M/10M.
Fix: "1.3× to 9× our 46M total parameters (inference)".

### Low severity (correct but unlabelled derivation, or value read outside the recorded sections)

**P8. Lines 98 and 106 (FoMoE).** "(20, 10 or 5 rounds)" / "5 to 20 rounds". These are 640 optimizer batches divided by K. The paper never states round counts (App. F gives 640 and K only); 04b calls it "my arithmetic". Fix: add "(inference: 640/K)".

**P9. Line 113 (Khaled).** "about 480 to 12 rounds at 150M". This is 24,000/50 and 24,000/2,000. The paper gives only the 24,000-step example (App. A.1.6). Fix: add "(inference)".

**P10. Lines 113 and 116 (Khaled).** "a quarter of the compute". The paper says "the global batch size as the local per-replica batch size"; the quarter is 1/M with M = 4. Trivial. Fix: add "(inference)", or write "at the per-replica batch (1/M of the compute)".

**P11. Line 123 (Khaled question).** "H = 500 (about 48 rounds)" is 24,000/500, and "our further 3 points" is 6.1 − 3.1. Both are unlabelled. Fix: add "(inference)".

**P12. Line 143 (DES-LOC).** "about 3,200 sequential steps at a 2M-token global batch". The paper gives 6.4B tokens and a 2M-token batch (§4.1), but no step count; 6.4B/2M = 3,200. Fix: add "(inference)".

**P13. Line 146 (DES-LOC).** "only about 12.5 rounds at the 256-step period" = 3,200/256. Fix: add "(inference)".

**P14. Line 174 (Gating Dropout, re-test 2212.07571).** "+0.1 to +0.4 chrF++ at p = 0.2 (2212.07571, Table 2, v1)". These are differences of Table 2 cells (44.3 → 44.4, 54.4 → 54.8, 41.9 → 42.3); the paper's prose gives no delta for Gating Dropout ("performs better than the baseline MoE", §5.2). Fix: add "(inference)".

**P15. Line 226 (BTM).** "8× the parameters at equal compute" is the ratio of Table 1's total-parameter columns (125M against 1B, and so on). The text says only "Total parameter counts are in Table 1". Trivial. Fix: "8× the parameters (Table 1 totals)", or add "(inference)".

**P16. Line 246 (σ-MoE).** "10× our characters" = 1.64B/163.84M. Line 243 labels the 1.64B as inference; the ratio is not labelled. Fix: add "(inference)".

**P17. Line 266 (Al-Rfou).** "about 400× our training characters" = 65.5B/163.84M = 400.0. Fix: add "(inference)".

**P18. Line 267 (Al-Rfou question).** "the 0.26 bits per character between our 1.44 and T12's 1.18" is a subtraction, unlabelled. Trivial. Fix: add "(inference)".

**P19. Line 253 (Slicing and Dicing).** "at 10M to 300M active parameters (up to 6.6B total)". The 300M-active upper bound is stated only in the §3 opening paragraph "Model Architecture" ("roughly 10 million to 300 million active parameters") and in figure captions. Neither is in 02a's read status (abstract, §1, the §3.1 "MoEs outperform dense" paragraph, the §3.2 generalists paragraph, §3.3, the App. A hyperparameter table, App. C.3). §1 says "10 million to 6.6 billion total". **Found, but outside the read sections.** Fix: record the §3 "Model Architecture" paragraph as read in 02a (the notes' list of seven sizes shows it was seen), or reword as "10M active and up, to 6.6B total".

### Locator imprecisions (numbers verified; both locations are in read sections, so no breach of the read rule)

- **Line 29.** The Streaming DiLoCo gaps (+2.6%, +3.7%) use the data-parallel loss 3.51 from **Table 5**. Table 6 has no data-parallel row. Suggest "Tables 5 and 6".
- **Lines 39 and 224.** The BTM dense values 22.5, 18.5, 17.0 and 16.3 are the T-LM "All" row of **Table 1**; Table 4 holds only the random-ensemble and ELMForest values. Suggest "Tables 1 and 4".
- **Line 214.** HARC "from layer 11 of 16" appears in the discussion of Fig. 4(a) in the results section, not in §1. The full text was read, so the rule is not breached.
- **Line 27 (precision).** "trails a Nesterov outer step by about 2.9%" holds for Nesterov at outer lr 1.0 (16.38 against 17.75). At lr 0.7 the gap is +1.0% (17.25). Suggest "a Nesterov outer step at lr 1.0".

## OK checks (compact)

Classes: R = OK-raw, I = OK-inference, O = OK-ours. "Where" names the scratchpad paper directory and the table, section or caption in the raw text.

### Header and summary

| Line | Numbers | Source | Class | Where found |
|---|---|---|---|---|
| 13 | 29.6%, 44.5%, 22.2%, 3.7%, mean 2, 100,000 draws, about 30%, exactly 2 (rolling) | coordinator | O | coordinator fact (holders_sim) |
| 14 | 5,000 steps, 100 warm-up, 1e-3, 1e-4, 20%, 125 steps | ours | O | configs/task_b/centralized.toml; header fact |
| 15 | 20,000 steps, batch 32 (×2), 5,000 steps (×2), batch 128 | ours | O | header fact; stage0-report §3 |
| 22, 24, 32 | +10.8%, +6.1% (×3), +1.4%, +3.2% | ours | O | stage0-report §3.3 tables |
| 26 | 4× steps | ours | O | 20,000 against 5,000 |
| 26 | 8× | DiLoCo 2311.08105v3 | R | Table 2 rows |
| 26 | 1.44%, 0.75% | DiLoCo v3 | I | ln15.30/ln14.72 − 1 = 1.437%; ln15.02/ln14.72 − 1 = 0.750% |
| 27 | 150M, 4 workers, H = 50 | Khaled 2509.10439v2 | R | Table 3 (PDF and HTML) |
| 27 | about 2.9% | Khaled v2 | I | ln17.75/ln16.38 − 1 = 2.87% (Nesterov lr 1.0) |
| 28, 44 | +2.0% (35M, M = 4), +0.3% (2.4B), 35M, 2.4B, 4 workers | scaling laws 2503.09799v1 | R | Table 4 prints the % column (§4, read) |
| 29 | 35M, H = 30, H = 100 | Streaming 2501.18512v1 | R | Table 6 rows "4 30", "4 100" |
| 29 | +2.6%, +3.7% | Streaming v1 | I | 3.60/3.51 = +2.56%; 3.64/3.51 = +3.70% (DP from Table 5) |
| 29 | H = 125 | ours | O | header |
| 30 | 16, 256 | DES-LOC 2505.22549v1 | R | §4.1 "Kb = 16, 256"; Fig. 5 panels |
| 34 | 21M, 40% | Ro 2204.09715v2 | R | Table 4 "Large Transformer 21.0M", "40%" |
| 34 | +1.3% | Ro v2 | I | ln30.45/ln29.15 − 1 = 1.29% |
| 34 | 1.3B | Filippova 2509.22418v1 | R | §3.1, Table 1 caption |
| 34 | 1B | SPES v3 | R | Table 1 caption, Table 2 |
| 34 | 1 to 2% | SPES / 04a | I | labelled; near-chance benchmark argument (04a) |
| 34 | 29.6% | coordinator | O | header |
| 36 | 2 holders of 4, K = 32, 64, 128 | FoMoE 2606.19025v2 | R | Table 6; App. F sweep grid |
| 36 | +1.6%, +2.9%, +2.1% | FoMoE v2 | I | 1.61, 2.90, 2.09 (Table 6 cells) |
| 36 | +4.4% | ours | I | mean bpc 1.59247/1.52537 − 1 = 4.40% |
| 38 | 25%, 50%, 75% | MoEC 2207.09094v1 | R | Table 3 rates 0.25, 0.5, 0.75 |
| 38 | 1.0%, 2.1%, 7.7% | MoEC v1 | I | 1 − 31.88/32.21 = 1.02%; 2.11%; 7.70% |
| 39 | 3.0% to 5.3% | BTM 2208.03306v1 | I | 3.00, 5.15, 4.30, 5.30 (inputs in Tables 4 and 1) |
| 40 | 4 held experts | ours | O | setup |
| 44 | 10M, 20M | S&D 2605.11689v1 | R | §3.1 paragraph "At 10M and 20M scales" |
| 44 | 1.44, 1.8 passes, 256 characters, 5% | ours | O | stage0-report; 163.84M/90M = 1.82 |

### Reading list

| Line | Numbers | Paper (dir) | Class | Where found |
|---|---|---|---|---|
| 67 | 60M, 150M, 400M | DiLoCo v3 (q1) | R | Table 1 |
| 67 | 1,024, 512, 88,000, 24,000, 8 workers, H = 500 | DiLoCo v3 | R | §3 setup text; Table 5 |
| 67 | 4e-4 ("4-4"), wd 0.1, outer lr 0.7, momentum 0.9 | DiLoCo v3 | R | Table 5; §3.1 |
| 69 | 16.23, 15.30, 14.72, 15.02; 8× | DiLoCo v3 | R | Table 2 (perplexity column, row order checked) |
| 69 | +0.75%, −0.68%, +1.44% | DiLoCo v3 | I | 0.750, −0.677, 1.437 |
| 72 | H = 1,000; 2.9%; H = 50 | DiLoCo v3 | R | §3.1 text |
| 74 | −0.1 PPL | DiLoCo v3 | R | §3, Fig. 3 text |
| 76 | 8 workers, H = 500 | DiLoCo v3 | R | §3 |
| 77 | 8× updates | DiLoCo v3 | R | Table 2 |
| 77 | +6.1%, batch 128, 5,000 steps | ours | O | stage0-report; header |
| 83 | 1B; 0.3B/1.1B; 16 experts; top-2 | SPES v3 (q4a) | R | Table 2 |
| 83 | 50B (v3); 100B (v1, v2) | SPES v1/v2/v3 | R | v3 Table 1 caption and App. B; v1/v2 §4.2 |
| 83 | 2B on 16 nodes, one expert each; 7B on 4 nodes; 9B upcycled | SPES v3 | R | §3.3, §4.1 |
| 83 | H = 50 (1B), 100 (larger) | SPES v3 | R | Table A1 (HTML) |
| 83 | 0.01, 0.001 | SPES v3 | R | App. B |
| 85 | 50.02, 49.79, 50.95; 8 tasks | SPES v3 | R | Table 1 (PDF and HTML) |
| 85 | 49.7, 50.5, 51.0 | SPES v1, v2 | R | Table 1 averages (HTML) |
| 86 | 48.99, 50.95 | SPES v3 | R | Table 4; §4.2 text |
| 86 | 50.5, 51.3 | SPES v1, v2 | R | Table 4; §4.2 text |
| 87 | 100B; 2, 4, 8 nodes; 50.6, 49.7, 49.5 | SPES v3 | R | Table A5; App. B; App. E text |
| 88 | H 50, 200, 400 | SPES v3 | R | App. E text ("declines when H increases from 50 to 200 or 400") |
| 91 | 1.1B, 16 experts, H = 50 | SPES v3 | R | Table 2, Table A1 |
| 91 | 1 to 2% | SPES / 04a | I | labelled |
| 91, 92 | 1 to 4 holders; +1.4% | ours | O | header; stage0-report |
| 92 | H = 50 | SPES v3 | R | Table A1 |
| 98 | M = 2, 4, 8; K = 32, 64, 128 | FoMoE v2 (r2) | R | App. F, Table 7 sweep grid |
| 98 | 0.7, 0.9 | FoMoE v2 | R | App. F ("server learning rate 0.7 and momentum 0.9") |
| 98 | ~54M; 4 layers; width 256; 8 experts; hidden 128; top-2 | FoMoE v2 | R | Table 1 (PDF and HTML) |
| 98 | 200,019; about 1.34B tokens | FoMoE v2 | R | App. F, Table 7 |
| 98 | about 51M of 54M | FoMoE v2 | I | 200,019 × 256 = 51,204,864 |
| 100 | 121.42, 112.00, 103.91; 130.79, 119.53, 104.47; 143.72, 123.50, 111.89; M = 4 | FoMoE v2 and v1 | R | v2 Table 6 = v1 Table 7 (all 126 cells identical) |
| 101 | +1.6, +2.9, +2.1; +3.4, +4.8, +5.3; random +1.9, +2.0, +2.4 | FoMoE v2 | I | 1.61, 2.90, 2.09; 3.35, 4.83, 5.31; 1.93, 2.04, 2.41 |
| 102 | M = 8, K = 128, 138.88, 159.71 | FoMoE v2 | R | Table 6 |
| 103 | 420.49, 111.89 | FoMoE v2 | R | Tables 4 and 5 |
| 104 | 12.6% to 15.7% | FoMoE v2 | I | 126 cells: min 0.1264, max 0.1565 |
| 106 | about 4% (FoMoE) | FoMoE v2 / 06 | I | 2,097,152/54,358,784 = 3.86% (two-matrix assumption stated in 06) |
| 107 | +4.4%; FoMoE's 2% | ours / FoMoE | I | as line 36; rounded 1.6 to 2.9% |
| 113 | 150M, 400M, 1B; 512; 1,024; M = 4; H 50 to 2,000; lr 1; 4× batch | Khaled v2 (q1) | R | §4.2; Table 3 caption "sequence length 1024 and batch size 512"; Methods paragraph |
| 115 | 18.07, 16.89 | Khaled v2 | R | Table 3 (PDF and HTML) |
| 116 | 17.75, 17.58, 18.20, 18.44, 18.18, 18.11; H = 250 | Khaled v2 | R | Table 3 (row mapping confirmed in HTML) |
| 116 | +1.8, +1.4, +2.6, +3.1, +2.6, +2.5% | Khaled v2 | I | 1.76, 1.42, 2.64, 3.11, 2.60, 2.47 |
| 117 | 16.38, 16.79, 17.12, 18.15, 18.75, 18.36; lr 0.7 rows | Khaled v2 | R | Table 3 (HTML) |
| 118 | 16.88, 17.59, 17.18; lr 2.0 | Khaled v2 | R | Table 3 (HTML) |
| 119 | H = 250 to 2,000 | Khaled v2 | R | App. A.1.2 |
| 120 | greater than 1 | Khaled v2 | R | abstract |
| 123 | H = 500; +3.1% (restated inference) | Khaled v2 | R / I | Table 3; line 116 |
| 129 | 35M, 2.4B, 4B, 10B | scaling laws v1 (q1) | R | Table 3 |
| 129 | β2 0.99; 5%; momentum 0.9; H = 30; M = 1, 2, 4, 8 | scaling laws v1 | R | §3 "Algorithms and optimizers"; §3.1 |
| 131 | 3.485; −0.1, +0.7, +2.0, +3.9%; 90M +1.5%; 2.4B +0.3%, +1.1% | scaling laws v1 | R | Table 4 (prints %) |
| 134 | H = 1 | scaling laws v1 | R | §5.1, Fig. 9 text |
| 137 | +2.0% at 35M, +0.3% at 2.4B | scaling laws v1 | R | Table 4 |
| 143 | 135M; 6.4B; 2M tokens; M = 4; 16, 256 | DES-LOC v1 (q1) | R | §4.1 |
| 144 | 10.20, 12.77, 26.77, 12.27, 12.11; 10.19, 17.79, 17.72, 17.22, 17.33 | DES-LOC v1 | R | Fig. 5 legends (caption at "Figure 5:") |
| 146 | β2 = 0.9999 | DES-LOC v1 | R | §4.1 Optimizers |
| 147 | 125 steps; β2 = 0.95 | ours | O | config |
| 153 | 1.3B; K = 32; batch 16; outer lr 0.4 ("4 × 10-1"); momentum 0.9; H = 100 | Filippova v1 (q3) | R | §3.1 |
| 154 | 26B; 12.75, 12.24, 12.72, 13.59, 14.21 | Filippova v1 | R | Table 1 |
| 154 | −1.6, −0.1, +2.5, +4.3% | Filippova v1 | I | −1.60, −0.09, +2.51, +4.26 |
| 154 | almost 50%; 12.68; 37B | Filippova v1 | R | §3.2; Table 1 "overtrained … 37" |
| 154 | 1.7×; 2.41 | Filippova v1 | R | Fig. 3 caption text |
| 156 | 1.3B; 32 nodes | Filippova v1 | R | abstract; §3.1 |
| 157 | +4.3%, −1.6% (restated) | Filippova v1 | I | line 154 |
| 157 | +1.4%; about 2 holders; one half | ours | O | stage0-report; header |
| 163 | 134M, 500M, 1B; 8 workers | SDP v5 (q3) | R | §4.1; App. E |
| 164 | C = 0.69; 2.452, 2.437, 2.437, 2.434 | SDP v5 | R | Table 1 (values right; label wrong, see P6) |
| 164 | C = 3/8; 87.91, 22.56, 42.68 | SDP v5 | R | Table 4 (RN-18, CIFAR-10); §4.2 text for 87.91 |
| 166 | H = 1 (every-step sync) | SDP v5 | R | §3 |
| 167 | +1.4% | ours | O | stage0-report |
| 173 | 128 experts; 5.6 billion; 16 GPUs; 64 experts; 10 billion; 64 GPUs; k = 1; 0.01 | Gating Dropout v2 (q2a) | R | §3, §4 setup |
| 174 | 24.60, 25.06 (p = 0.3), 25.12 (p = 0.2), 23.06 | Gating Dropout v2 | R | Table 2 |
| 174 | 28.63, 29.22, 28.85 | Gating Dropout v2 | R | Table 4 |
| 174 | p = 0.2 best; p = 0.5 −0.23; p = 1 | Gating Dropout v2 | R | §4.4 text (Fig. 6 discussion); §3 |
| 174 | p = 0.2 (re-test) | 2212.07571v1 (r2) | R | Table 2 row "pgd=0.2" |
| 174 | 25%, 50%, 75%; 32.21; 32.50 | MoEC v1 (r2) | R | Table 3 |
| 174 | 1.0%, 2.1%, 7.7% | MoEC v1 | I | as line 38 |
| 176 | 64 to 128 experts | Gating Dropout v2 | R | §4 |
| 176 | 125 steps; p = 1 within a round | ours | O | setup analogy |
| 183 | 124M; 4 experts; top-1, top-2; ~6B tokens; 0.01 | Fan v1 (q2a) | R | §2 setup; App. |
| 184 | 9.810, 9.907, 11.752; 22.687, 22.632, 26.879 | Fan v1 | R | Table 3 (garbled; mapping checked against Table 1 learned values and §3.2.1 text) |
| 184 | 11.815, 26.195 | Fan v1 | R | Table 1 dense row |
| 184 | 10.674, 10.667 | Fan v1 | R | Fig. 1 caption |
| 187 | 125 steps | ours | O | setup |
| 193 | 3.4B / 0.6B; 64 experts; top-4; 4 shared; 43B / 6.6B; 120B, 400B | Demons v2 (q2a) | R | §4.1 |
| 194 | 4 → 8.167; 32 → 8.062; 512 → 8.038; 8.041 | Demons v2 | R | Tables 1 and 2 |
| 194 | 7.283, 7.322, 7.199 | Demons v2 | R | Table 3 |
| 194 | 0.15, 0.2 | Demons v2 | R | §4.2 |
| 197 | 4 held experts | ours | O | setup |
| 203 | 7B; two experts | FlexOlmo v4 (q2b) | R | §4.4; §3.3.1 |
| 204 | 46.7, 47.8, 45.8, 44.4, 38.8; 39.6, 42.2, 43.4, 40.0, 51.5; 2× FLOPs; four-expert | FlexOlmo v4 | R | Table 1 and caption |
| 213 | OLMoE-1B-7B; 16 layers; Qwen3-30B-A3B | HARC v1 (q2b) | R | §5 setup; App. D.2 |
| 214 | 50.11%; 99.98%; layer 11 of 16 | HARC v1 | R | §1; Fig. 4(a) discussion |
| 214 | 34.43, 34.93, 38.08, 38.96, 40.05 | HARC v1 | R | Table 1; §5 text |
| 214 | +0.27, +0.88 | HARC v1 | R | App. D.3 prose ("+0.88 … SFT's … +0.27") |
| 214 | 77.7 to 96.9%; AUROC 0.47 to 0.52; −0.133 to +0.236 | 2609.32821v1 (r2) | R | §3.1; §3.2; §6.2 prose |
| 217 | top-2 over 4, over 8 | ours | O | setup |
| 223 | 125M to 1.3B; 8 domains | BTM v1 (q4b) | R | §4.1 |
| 224 | 19.8 against 22.5 | BTM v1 | R | Table 1 |
| 224 | 24.7, 21.5, 19.2, 18.9 | BTM v1 | R | Table 4 |
| 224 | 22.5, 18.5, 17.0, 16.3 | BTM v1 | R | Table 1 T-LM "All" (report says Table 4) |
| 224 | +3.0% to +5.3% | BTM v1 | I | 3.00 to 5.30 |
| 224 | 40% to 60% | BTM v1 | R | §5.2 |
| 233 | 2×4, 8×8, 16×16; 150M; 0.7, 0.9; τ = 150 | DiPaCo v1 (q4b) | R | Table 1; §4; §7.1 |
| 234 | 14.72, 15.02, 14.86, 14.62; 8 workers, 8× | DiPaCo v1 | R | Table 1 |
| 234 | +0.8%, +0.4% | DiPaCo v1 | I | 0.750; 0.352 (rounds to 0.4) |
| 234 | 11.41, 11.38, 12.39; every 64 tokens; 1B | DiPaCo v1 | R | Table 3; §5 text |
| 237 | 46M | ours | O | setup |
| 243 | 41M; 12 layers; width 512; 16 experts; 128; K = 4; 25%; 100k steps; batch 32; context 512 | σ-MoE v3 (q2a) | R | Table 8 (App. B); §6 text; Table 9 |
| 243 | 1.64B; about 18 passes | σ-MoE v3 | I | 100,000 × 32 × 512 = 1.638B; /90M = 18.2 |
| 243 | 47M, 262M | σ-MoE v3 | R | §6 |
| 243 | 2 of 8 | ours | O | setup |
| 244 | dense 1.08, σ-MoE 1.08, Switch 1.08; 1.08 to 1.11; S-BASE 1.17 | σ-MoE v3 | R | Tables 3, 4, 10 |
| 244 | 11.59, 12.01, 11.89 (47M) | σ-MoE v3 | R | Table 4 |
| 247 | 46M; 1.8 passes | ours | O | setup |
| 247 | 18 passes | σ-MoE v3 | I | as line 243 |
| 253 | over 2,000 runs; 10M; up to 6.6B total; 1e-3; 1e-2, 1e-4 | S&D v1 (q2a) | R | abstract; §3.1; App. A.3 table |
| 254 | 10M, 20M; 1e-4 | S&D v1 | R | §3.1 paragraph; §3.3 |
| 257 | 20,000 steps | ours | O | setup |
| 263 | 90M/5M/5M; T12 12 layers 44M/41M; T64 64 layers 235M/219M; context 512 | Al-Rfou v2 (q6) | R | data section; Table 1; model section |
| 263 | 8M steps; batch 16; 512 | Al-Rfou v2 | R | "Results" text; training section |
| 263 | about 65.5B | Al-Rfou v2 | I | 8e6 × 16 × 512 = 65.5B |
| 264 | 1.18, 1.13 | Al-Rfou v2 | R | Table 1 |
| 264 | contexts 32, 64, 128, 256, 512 → 1.34, 1.26, 1.20, 1.16, 1.13 | Al-Rfou v2 | R | Table 2 (confirmed in paper_raw.txt) |
| 264 | +0.045 bpc (+3.9%) | Al-Rfou v2 | I | (32·1.34 + 32·1.26 + 64·1.20 + 128·1.16)/256 = 1.2050; −1.16 = 0.045; 3.88% |
| 267 | 1.44 | ours | O | stage0-report |
