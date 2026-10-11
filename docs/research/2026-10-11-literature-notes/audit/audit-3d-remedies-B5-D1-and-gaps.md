# Audit 3d: section 4 remedies rows B5 to D1 (lines 547-562) and section 6 gaps (lines 591-626)

Status: FINAL.

Scope: report `docs/research/2026-10-11-stage0-literature-report.md`, rows B5-D1 (lines 547-562) and every paper-attributed number in section 6 (lines 591-626). Proposed run settings in section 6 (H and R values, worker counts, slice sizes, batch and step settings, note 05's sweep ranges) are skipped as instructed.
Method: grep -F on raw text under `scratchpad/papers/` (PDF text; HTML text for Khaled Tables 3-4, FoMoE Table 6 via `r2/2606.19025/tables_v2.txt`, SPES Table 4 via `paper_html.txt` of v1, v2, v3). Each locator was checked against the surrounding text, and each read status against the manifest and notes. The arXiv version stamp in every raw file matches the version cited. Arithmetic was re-run in `scratchpad/audit3d_scripts/arith.py`. No downloads were needed.
Counting follows part-c: one count per number token; a number repeated within a row is counted once.

## 1. Counts by class

| Class (number tokens) | Section 4, B5-D1 | Section 6 | Total |
|---|---|---|---|
| OK-raw | 115 | 5 | 120 |
| OK-inference | 4 | 0 | 4 |
| OK-ours | 2 | 13 | 15 |
| PROBLEM | 9 | 5 | 14 |
| Total numbers checked | 130 | 23 | 153 |
| PROBLEM entries | 8: 5 substantive (P-D1 to P-D5), 1 claim-level (P-D6, which also covers line 598), 2 locator-only (P-D11, P-D12) | 4: 3 known wording (P-D8 to P-D10), 1 claim-level (P-D7) | 12 |

The PROBLEM tokens are: 4.5; +0.50; +0.007; 1.08; +1.12% and +0.84%; "lr 1" (551); "8 experts" locator; +2.4 locator; "exceeds 1" (598); 35M "dense" (600); ~10M (597); about 70% (601); about 10M (624).

## 2. PROBLEM list

### Substantive (number provenance or value)

**P-D1. Line 553 (C1), derived without a label.**
- Text: "BTX, 7B continued pretraining: router fit plus 80B tokens gives +4.5 average points over BTM"
- What is wrong: the paper does not state 4.5. It is 47.9 (BTX Top-2) − 43.4 (BTM Top-2) from Table 2 (v1; garbled in pdftotext, but the row order maps and the notes 04b line 52 record the same mapping). The subtraction is unlabelled.
- Fix: "router fit plus 80B tokens gives 47.9 against 43.4 average for BTM, both top-2, +4.5 points (Table 2, v1; inference)".

**P-D2. Line 553 (C1), range wrong and lower bound unlabelled.**
- Text: "HARC, OLMoE fine-tune merges: +0.50 to +0.88; full fine-tuning +0.27 (Tables 1 and 7, v1)"
- What is wrong: the lower bound is broken without relying on row order. Table 7 (App. D.3, read) confirms RegMean 37.14 → 37.58 with HARC, which is +0.44. By the Table 1 row order, the six merging methods gain WA +0.50, TIES +0.54, DARE +0.53, WUDI +0.88, Fisher +0.17 and RegMean +0.44. Only +0.88 (WUDI) and +0.27 (SFT) are stated in the prose. +0.50 is an unlabelled subtraction (34.93 − 34.43). Note 02b line 508 already gives "+0.17 to +0.88".
- Fix: "HARC, OLMoE fine-tune merges: +0.17 to +0.88 overall points across six merging methods (Table 1, v1; inference, row order; RegMean +0.44 and WUDI +0.88 confirmed by Table 7); full fine-tuning +0.27 (Table 7)".

**P-D3. Line 555 (C3), derived without a label, and the wrong contrast for this row.**
- Text: "MedMix, medical classification: +0.007 F1 (Table 3)"
- What is wrong: the ablation prose states 0.523 (base, without CEA, CRA or MCR) and 0.530 (complete). The +0.007 is an unlabelled subtraction. It is also the gain of the whole method. The component this row is about, similarity-based expert aggregation (CEA), adds only 0.529 → 0.530, +0.001 (same prose).
- Fix: "MedMix, medical classification: full method 0.530 against 0.523 average F1 (+0.007); the similarity-based expert aggregation alone adds +0.001, 0.529 to 0.530 (Table 3 and ablation prose, v1; inference)".

**P-D4. Line 557 (C5), value misreported.**
- Text: "enwik8 41M: no difference (1.08)"
- What is wrong: in Table 4 (v3), "softmax (renorm.)" on E8 (41M) is **1.09** and σ-MoE is 1.08. App. Table 10 agrees ("softmax (after top-k) … 1.09"). The "1.08 both" in note 02a lines 312-313 belongs to the dropout and init ablations, not to softmax renormalization.
- Fix: "enwik8 41M: 1.09 against 1.08 bits per character (Table 4, v3)".

**P-D5. Line 560 (C8), numbers attached to the wrong setting.**
- Text: "QSR, ViT and ResNet on ImageNet: +1.12% and +0.84% top-1 over data parallel (abstract, v2)"
- What is wrong: both numbers are for Local AdamW on ViT-B, with 16 and 64 GPUs. As written, one reads as a ResNet result.
- Fix: "QSR, ImageNet: Local AdamW on ViT-B gains +1.12% (16 GPUs) and +0.84% (64 GPUs) top-1 over data parallel; ResNet results described as consistent improvements (abstract, v2)".

### Claim-level (a statement about a read part contradicted by its raw text)

**P-D6. Line 551 (B9, caveats), and line 598 (gap 2).**
- Text (551): "No paper read reports the loss at lr 1 against the tuned value side by side."
- Text (598): "(Horoi et al. and Khaled et al. suggest the best plain outer step exceeds 1)"
- What is wrong: Khaled Table 4 (v2, read) gives an outer-SGD sweep with a cosine schedule: 0.3 → 17.68, **0.5 → 16.63**, 0.7 → 18.84, **1.0 → 19.21**; nothing above 1 was tested. So a paper does report lr 1 next to a tuned value, but the tuned value is below 1. Khaled's "greater than 1" is a theoretical "sometimes" (abstract). Only Horoi's tuned 1.6 (Table 5, App. A) supports a value above 1. Also, the "greater than 1" quote is in the abstract only, not in §1.
- Fix (551): "Khaled's outer-SGD sweep (Table 4, cosine schedule, single runs) is best at lr 0.5 (16.63) against 19.21 at lr 1.0 and tests nothing above 1; only Horoi tunes above 1 (1.6), and reports no lr-1 run beside it".
- Fix (598): "(Horoi et al. tuned plain outer SGD to lr 1.6; Khaled et al.'s theory says it should sometimes exceed 1, though their own SGD sweep was best at 0.5)".

**P-D7. Line 600 (gap 4).**
- Text: "Published worker-count curves come from dense subword models of 35M and above."
- What is wrong: 35M itself is right (DiLoCo scaling laws 2503.09799 v1, Table 4, M = 1/2/4/8 at 35M; q1/2503.09799 pt l.392). "Dense" is not. SPES Table A5 (1B MoE, 2/4/8 nodes), cited in the same sentence, and FoMoE Tables 3-6 (54M MoE, M = 2/4/8) are MoE worker-count curves. The sentence is copied from note 01 G3, whose scope was dense local-averaging papers.
- Fix: "Published worker-count curves come from subword models of 35M and above: dense in the DiLoCo family, MoE in SPES (1B, Table A5) and FoMoE (54M, Tables 3-6)."

### Known wording problems (coordinator facts)

**P-D8. Line 597 (gap 1).**
- Text: "No character-level or ~10M-active H curve exists."
- Fix: "No character-level or ~14M-active H curve exists." (About 14.2M active per token.)

**P-D9. Line 601 (gap 5).**
- Text: "8 workers with 4 of 8 experts (fraction about 70%, about 4 holders)"
- Fix: "8 workers with 4 of 8 experts (fraction about 54%, about 4 holders)". Check: (46.05 − 42.47 + 42.47/2) / 46.05 = 24.82 / 46.05 = 53.9%.

**P-D10. Line 624 (Not answerable paragraph).**
- Text: "dense baselines at about 10M and 46M parameters [01 G8; 05 4]"
- Fix: "dense baselines at about 14M (matching active parameters) and 46M parameters".

### Locator-only

**P-D11. Line 553 (C1).** Text: "Router KD: gains "relatively marginal for Mixtral" (8 experts) (§4, prose)". The quote and "only 8 experts per layer" are in §5.4 Results ("Coarse-grained Experts" paragraph, read), not §4 (the method section). Note 02b line 367 carries the same wrong locator. Fix: "(§5.4, prose, v1)".

**P-D12. Line 554 (C2).** Text: "KALAVAI, fine-tuning: frozen early layers +2.4 points only beyond 10,000 specialist steps (Table 5, v2)". The "+2.4pp" is stated in the §4.4 prose and the abstract. Table 5 itself gives 17.0% against 14.7% at 20,000 steps, a difference of 2.3. Fix: "(§4.4 and Table 5, v2: +17.0% against +14.7% at 20,000 steps)".

## 3. Observations (accurate numbers, but the claim around them could be tightened; not counted as PROBLEMs)

- **Line 548 (B6), FoMoE "fixed placement better than random, e.g. 112.00 against 113.65".** Several Table 6 cells reverse this. At LocalAdamW, M = 4, K = 64, O_e = 2: fixed 119.53 against random 114.88. At M = 8, K = 128: O_e = 2 gives 156.84 against 146.16, and O_e = 4 gives 138.88 against 131.86. The paper's §6.1 claim is about the communication-quality and compute-quality frontier, including migration costs. Suggest: "fixed placement gives the best communication- and compute-quality trade-offs (§6.1); cell by cell the sign varies, e.g. 112.00 against 113.65 at K = 32 but 119.53 against 114.88 at K = 64 (Table 6, v2)".
- **Line 548 (B6), IST "re-sampling 0.84 against fixed 0.74 at 2 nodes".** These are the 3-layer network numbers; the 2-layer network gives 0.82 against 0.82. "Fixed" is an ensemble trained without synchronization and aggregated once, so re-sampling is confounded with synchronization. Suggest adding "3-layer".
- **Line 553 (C1), BTX "34.7 against 34.7".** This pairs BTX (with load balancing) with "no LB & freeze experts". The like-for-like freezing contrast is 34.6 (no LB) against 34.7 (no LB, experts frozen), Table 5, at 10B fine-tune tokens. The conclusion is unchanged.
- **Line 555 (C3), FedAlign-MoE +1.6 / +7.8.** The arithmetic reproduces (0.9424 − 0.9263 = 1.61; 0.8522 − 0.7740 = 7.82). These are Switch-base-16 on AGNews only; MMLU under IID is +4.9. Suggest adding "Switch, AGNews".
- **Line 620 (gap 18), "Khaled et al.'s plain averaging at H ≥ 250 was no better than such a floor".** Verified: the one-replica data-parallel perplexity is 18.07; SGD at H = 250/500/1,000/2,000 gives 18.20/18.44/18.18/18.11, while H = 150 gives 17.58 (Table 3, v2). Line 116 labels the same comparison "(inference, 01)"; adding the label here would be consistent.

## 4. OK table

Abbreviation: PAPERS = `.../scratchpad/papers`. "pt" = paper.txt.

| Line | Number(s) | Paper | Class | Where found |
|---|---|---|---|---|
| 547 | 1.3B; 1/8; 13.59; 26B; 12.68; 37B; 12.75 | Filippova 2509.22418 v1 | OK-raw (7) | q3/2509.22418 pt l.514-528, Table 1 (12.75 is the "Streaming DiLoCo" full-model row); full text read |
| 547 | 1B; 2.437; 2.452 | SDP 2507.09029 v5 | OK-raw (3) | q3/2507.09029 pt l.392-401, Table 1 (B-SDP and Bb-SDP both 2.437; DDP 2.452); FLOP matching l.368-371 |
| 548 | 54M; 112.00; 113.65; K = 32; 2 holders | FoMoE 2606.19025 v2 | OK-raw (5) | r2/2606.19025/tables_v2.txt Table 6, LocalAdamW, M = 4, fixed and random rows; pt l.1704 (54M) |
| 548 | 3-layer; 29.22; 27.21; 23.46; 29.79 | FedRolex 2212.01548 v2 | OK-raw (5) | q3/2212.01548 pt l.387 (3-layer), l.469-474 Table 3, Stack Overflow column (HeteroFL, Fed. Dropout, FedRolex, Homogeneous largest) |
| 548 | 200K | PVT 2110.05607 v1 | OK-raw (1) | q3/2110.05607 pt §3.4.1, l.191-192 |
| 548 | 0.84; 0.74; 2 nodes | IST 1910.02120 v7 | OK-raw (3) | q3/1910.02120 pt l.394, Table 3 (3-layer, IST vs Ensemble); §3.2 read |
| 548 | 79.48; 83.00; 72.03 | FLEX-MoE 2512.23070 v2 | OK-raw (3) | q2b/2512.23070 pt l.316-326, Table I, IID, CIFAR10 |
| 549 | 150M; 2×4; 14.86; 14.62; 8×; 14.72 | DiPaCo 2403.10616 v1 | OK-raw (6) | q4b/2403.10616 pt l.751-770, Table 1 |
| 549 | 1B; 64 tokens | DiPaCo | OK-raw (2) | pt l.796-800 (§4.4, Table 3); §6 quote l.889-893 |
| 549 | 335M; 1.3B; 3.85%; 17.56% | SMALLTALK LM 2410.03529 v2 | OK-raw (4) | q4b/2410.03529 pt l.1340-1363, App. Table 3 (min and max of the gain column) |
| 549 | 125M; 1.3B | BTM 2208.03306 v1 | OK-raw (2) | q4b/2208.03306 pt Tables 1 and 4 |
| 549 | +3.0%; +5.3% | BTM | OK-inference (2) | ln ratios of Table 4 random ensemble to Table 1 T-LM: 3.00%, 5.15%, 4.30%, 5.30%; labelled inference; unit is log-perplexity per the report's line 8 convention |
| 550 | 1B; 8-task; 48.99; 50.95; 50.5; 51.3 | SPES 2602.11543 | OK-raw (6) | q4a/2602.11543v3 paper_html.txt l.659-683 (Table 4, 8 columns + Avg.); v1/v2 paper_html.txt l.668-683 (50.5, 51.3) |
| 551 | 178M; 1.6; 8 workers; H = 30 | Horoi 2607.03011 v1 | OK-raw (4) | q1/2607.03011 pt l.925-929 (Table 5, App. A, for Table 1), l.377 (R = 8, H = 30) |
| 551 | "greater than 1" | Khaled 2509.10439 v2 | OK-raw (1) | q1/2509.10439 pt l.23 (abstract only; see P-D6) |
| 551 | lr 1 (Remark 1) | FedOpt 2003.00295 v5 | OK-raw (1) | q1/2003.00295 pt l.388 |
| 552 | 150M; 4 workers; 17.18; 18.44; H = 500; 17.59; 18.11; H = 2,000 | Khaled v2 | OK-raw (8) | q1/2509.10439-html/paper_html.txt Table 3 rows (H, M, algorithm, lr, perplexity, size) |
| 553 | 7B; 80B; 34.7 | BTX 2403.07816 v1 | OK-raw (3) | q4b/2403.07816 pt l.283 (80B), l.513-517 (Table 5) |
| 553 | 7B; 46.7; 47.8 | FlexOlmo 2507.07024 v4 | OK-raw (3) | q2b/2507.07024 pt l.474, 482 (Table 1) |
| 553 | 410M; 6.9B; −1.19%; +7.70% | KALAVAI 2603.22755 v2 | OK-raw (4) | q4b/2603.22755 pt l.547-553 (§4.5) |
| 553 | +0.88; +0.27 | HARC 2606.03391 v1 | OK-raw (2) | q2b/2606.03391 pt l.477-478, l.1051-1055 (Table 7 prose) |
| 553 | −0.133; +0.236 | Routing Drift 2609.32821 v1 | OK-raw (2) | r2/2609.32821 pt l.642-643 (§6.2) |
| 554 | 7B; 38.8; 46.7 | FlexOlmo v4 | OK-raw (3) | pt l.474, 480 (Table 1, "no training to coordinate") |
| 554 | 66% | DDOME 2306.08586 v3 | OK-raw (1) | q2b/2306.08586 pt l.1083-1084 (App. E prose) |
| 554 | 10,000 | KALAVAI v2 | OK-raw (1) | pt l.529-535 (§4.4); +2.4 see P-D12 |
| 554 | 7B; 20.3; 46.4 | BAR 2604.18473 v1 | OK-raw (3) | q2b/2604.18473 pt l.504-535 (§5.3) |
| 555 | 0.5B; 1.5B; 44.07; 33.94 | Symphony-MoE 2509.18542 v2 | OK-raw (4) | q2b/2509.18542 pt l.433-435 (Table 3, 1.5B×4, discussed in §4.7, read) |
| 555 | +1.6; +7.8 | FedAlign-MoE 2603.21276 v2 | OK-inference (2) | q2b/2603.21276 pt l.807-811, Table I, Switch AGNews: 1.61 and 7.82; labelled inference |
| 555 | Dirichlet 0.1 | FedAlign-MoE v2 | OK-raw (1) | Table I caption l.819-820 |
| 555 | 125 steps | ours | OK-ours (1) | stage0-report l.83, l.188 (H = 125) |
| 556 | 20k; 3 of 3; 4 of 6; −1.741; −1.755; ±0.02 | ST-MoE 2202.08906 v2 | OK-raw (6) | q2a/2202.08906 pt l.322-325, l.448-458 (Table 4, §3.3) |
| 557 | 47M; 11.89; 11.59; 41M | σ-MoE 2310.10837 v3 | OK-raw (4) | q2a/2310.10837 pt l.612-627 (Table 4, WT-S column) |
| 558 | 2B | DeepSeekMoE 2401.06066 v1 | OK-raw (1) | q2a/2401.06066 pt §4.4, "about 2B" |
| 558 | 6.51; 6.48 | MaskMoE 2407.09816 v4 | OK-raw (2) | q2a/2407.09816 pt l.457 (Table 3, §5.1) |
| 558 | 10M; 300M; 2,000 | Slicing and Dicing 2605.11689 v1 | OK-raw (3) | q2a/2605.11689 pt l.25, l.247-248; quote l.686 (§3.2) |
| 559 | +0.10 | FjORD 2102.13451 v5 | OK-raw (1) | q3/2102.13451 pt l.580-585 (§5.3; metric negative perplexity, l.415) |
| 559 | 83.15; 53.28; 85.72 | InclusiveFL 2202.08036 v2 | OK-raw (3) | q3/2202.08036 pt l.495-499 (Table 2 Avg.) |
| 561 | 150M; 15B | MuLoCo 2505.23725 v3 | OK-raw (2) | q1/2505.23725 pt l.17, l.23 |
| 562 | 20%; 30%; 50% | Gating Dropout 2205.14336 v2 | OK-raw (3) | q2a/2205.14336 pt l.325 (0.3/0.2 defaults), l.441-447 (0.5: BLEU −0.23; §4.4, Fig. 6 prose) |
| 562 | 3; 8 devices | DeepSeek-V2 2405.04434 v5 | OK-raw (2) | r2/2405.04434 pt l.516 (§2.2.2, M ≥ 3), l.709 (training hyperparameters, D = 8, M = 3; read) |
| 562 | top-2 | ours | OK-ours (1) | stage0 design |
| 597 | batch 128 | ours | OK-ours (1) | 4 workers × 32 (stage0-report l.48, 66, 83) |
| 601 | about 4 / 1 / 3 holders | ours (derived) | OK-ours (3) | 8×4/8 = 4; 4×2/8 = 1; 4×6/8 = 3 |
| 601 | holder counts 1, 2, 4 | FoMoE v2 | OK-raw (1) | tables_v2.txt Table 6, O_e columns 1/2/4/8 |
| 602 | 1 to 4 holders; exactly 2 | ours | OK-ours (2) | coverage and rolling definitions (stage0) |
| 607 | 16; 256 | DES-LOC 2505.22549 v1 | OK-raw (2) | q1/2505.22549 pt l.540-555 (Fig. 5 legend: keep 12.77, reset 26.77 at Kx = 16; 17.79, 17.72 at Kx = 256) |
| 611 | H = 125; β2 = 0.95 | ours | OK-ours (2) | stage0-report l.67, l.83 |
| 612 | +6.1%; +7.6%; +10.8% | ours | OK-ours (3) | stage0-report l.161-163 |
| 620 | H ≥ 250 | Khaled v2 | OK-raw (1) | Table 3: DP one replica 18.07; SGD H = 250-2,000 ≥ 18.11 (see observation) |
| 621 | 0.072 | ours | OK-ours (1) | 0.05 × mean(1.4388, 1.4386, 1.4353) = 0.0719 |
| 622 | 1/8 | Filippova v1 | OK-raw (1) | Table 1 |
| 624 | 46M | ours | OK-ours (1) | 46.05M total |

Locators without numbers checked in passing: FoMoE App. B.3.2 sigmoid routing (paper_html.txt l.1359) and §6.3 skip-token quote (pt l.858-879); SDP Theorem 3.1 (pt l.269); FlexOlmo §5.1 router-embedding similarity (pt l.564-570); DES-LOC loss spikes on reset (§1, pt l.42); FedOpt Discussion (ii) (pt l.406-410). All are present in read parts.
