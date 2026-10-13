# Audit 2a: report lines 271-335 (section 3 intro, "Where the notes disagree" table, section 3.1)

Report audited: `docs/research/2026-10-11-stage0-literature-report.md`, lines 271-335 only.
Rule checked: every number taken from a paper comes from a part of that paper that was actually read.
Raw text: `scratchpad/papers/{q1,q4a,q4b,q6,r2}/<ID>/`. Every raw file's arXiv stamp matches the version the report cites (checked: 2311.08105v3, 2509.10439v2, 2607.03011v1, 2503.09799v1, 2501.18512v1, 2407.07852v1, 2505.22549v1, 2606.22768v1, 1910.00643v2, 2401.09135v2, 2411.02908v2, 2604.21428v1, 2512.17131v3, 2003.00295v5, 2310.14423v2, 1812.06162v1, 2410.21676v4, 2002.07839v2, 2405.10853v3, 2412.01152v1, 2410.05021v5, 2602.11543v1/v2/v3; FoMoE v2 from HTML).
Arithmetic re-run with `scratchpad/audit/calc2a.py` (Python, ln-ratio for perplexities, plain ratio for losses).
No paper had to be downloaded; all raw text was present.

## Counts by class (rows of the OK table plus PROBLEM rows)

| Class | Rows |
|---|---|
| OK-raw | 59 |
| OK-inference | 18 |
| OK-ours | 8 |
| PROBLEM | 9 rows, in 5 entries (3 of them the known "10M active" issue) |

Plus 7 observations (locator or read-status wording, not number violations).

## PROBLEM list

**P1. Line 298 (known issue).** Text: "character-level, about 10M active parameters, an MoE". Our model has about 14.2M active parameters per token (SwiGLU experts, three matrices). Fix: "character-level, about 14.2M active parameters, an MoE".

**P2. Line 302 (known issue).** Text: "| **Ours** (stage0-report §3.3) | 46M MoE, ~10M active, characters |". Fix: "46M MoE, ~14.2M active, characters".

**P3. Line 321 (known issue).** Text: "Extrapolating the scaling-law trend down to our ~10M active parameters would predict a gap larger than at 35M (inference, 01)." Fix: "down to our ~14.2M active parameters". The conclusion still holds, since 14.2M is below 35M.

**P4. Line 287: derived but unlabelled; the metric is not stated.** Text: "04a gave +2.1% (K = 128) and wrote "1.6 to 2.1%" in one place; 04b gave +1.6% to +2.9% | Settled by 06: +1.6%, +2.9%, +2.1% at K = 32, 64, 128". These percentages are not printed in FoMoE. 06 computed them as ln(PPL)/ln(PPL) − 1 from FoMoE v2 Table 6 (LocalAdamW, M = 4, fixed placement, O_e = 2 against O_e = 4 full replica): 112.00/103.91, 119.53/104.47 and 123.50/111.89. Re-run: +1.61%, +2.90%, +2.09%. The inputs are in the raw v2 HTML tables (`r2/2606.19025/tables_v2.txt`, lines 77, 83, 89), and the arithmetic reproduces. Only the label is missing. Fix: "Settled by 06: +1.6%, +2.9%, +2.1% at K = 32, 64, 128 (inference, 06: relative cross-entropy gap of 2 holders against full replica, fixed placement, M = 4, FoMoE Table 6, v2); the "1.6 to 2.1%" was a slip".

**P5. Lines 305, 306, 310, 311, 312: round counts are derived but unlabelled.** The note at line 314 covers only the gaps and Horoi's round count. The other round counts are total steps ÷ H, and no paper states them:
- Line 305 "≈160 / ≈48" and line 306 "≈480" (Khaled): 24,000 steps (App. A.1.6, "24,000 steps for 150M") ÷ 150, 500 and 50. Arithmetic: 160, 48, 480.
- Line 310 "352 / 88" (OpenDiLoCo): 44,000 steps (Table 2 caption) ÷ 125 and 500. Arithmetic: 352, 88.
- Lines 311-312 "≈200 / ≈12.5" (DES-LOC): 6.4B tokens ÷ 2M-token global batch (§4.1) = 3,200 steps, then ÷ 16 and 256. Arithmetic: 200, 12.5.

DiLoCo's "128" (line 303) is stated in the paper ("T = 128 times H = 500 inner steps (64,000", §2, v3), so it is OK-raw. A bare "≈" is not an inference label.

Fix: replace the note at line 314 with: "Gaps in this table are relative increases in log-perplexity or loss computed by 01. Round counts are 01's estimates (total steps ÷ H) except DiLoCo's 128, which the paper states: Khaled about 24,000 steps (App. A.1.6); OpenDiLoCo 44,000 steps (Table 2 caption); DES-LOC 6.4B tokens ÷ 2M tokens per step ≈ 3,200 steps (§4.1); Horoi about 3.56B tokens ÷ 524k tokens per step ÷ 30." Alternatively, retitle the column "Rounds (inference unless stated)".

## Observations (not counted as PROBLEMs)

- **O1. Lines 309 and 322, Streaming DiLoCo.** Table 6 has no data-parallel row. The DP reference 3.51 behind +2.6% and +3.7% comes from Table 5 (35M, raw line 1694). Table 5 was read (Supp. Tables 2, 5, 6, 7), so the read-sections rule holds, but the locator is incomplete. Suggested wording: "(Table 6, with DP 3.51 from Table 5, v1)".
- **O2. Line 323, INTELLECT-1.** The locator "(sections read)" is not a locator. The "final 20%" cool-down and "10 billion parameter" both sit in §3.1 (raw lines 466-474), which was read. Suggested: "([2412.01152](...), §3.1, v1)".
- **O3. Line 290, FoMoE "Table 3".** This can be resolved. In v2 HTML, "Table 3: Evaluation for FoMoE with LocalAdamW and DiLoCo across different configurations of workers M and synchronization frequencies K" is the parent caption of Table 4 (LocalAdamW) and Table 5 (DiLoCo). These are full-replica perplexities for M ∈ {2, 4, 8} and K ∈ {32, 64, 128}, with no centralized number. Any "cost" in Table 3 is therefore relative to more frequent synchronization or fewer workers, not to centralized training. The report's choice not to use it stands.
- **O4. Line 294, read status.** "04a read EMO's §3 to §5.3" overstates the read: 04a records §3, §4, §5.1, §5.2 and only the "start of §5.3". BAR's "§1 to §6" matches 02b (Abstract, 1-4, 5.1-5.3, 6). 02b also read BAR's Table 1 (49.1, 47.8, 50.5), so these three averages were in fact read once, by 02b. The report's conservative handling is fine.
- **O5. Line 291, SMoE-Dropout "8 or fewer experts".** The raw text (q6/2303.01610, line 549; paper_raw.txt line 492) reads "small network widths such as [glyph lost] 8 experts". The widths tested are 2, 4, 8 and 16, and the next clause contrasts with "16 experts", which fits "≤ 8" but does not confirm it. The report already marks the row unresolved and uncertain. No change needed.
- **O6. Line 318, Woodworth.** The phrase about first-order algorithms that "compute M KR stochastic gradients sequentially" is in §5 (raw line 556; 01 read §5 only in fragments), not §2. §2 discusses KR serial steps on one machine and the KM-minibatch baseline (Eq. 3, raw lines 64 and 202-206). Suggested locator: "§2 and §5, v2".

- **O7. Line 319, Khaled A.1.3.** The 30% to 10% cosine-similarity fall is stated for "momentum-based methods (Nesterov, SF-SGD)" (raw l.1167). The numbers are right, but the report drops the qualifier. Suggested: "Khaled A.1.3 measures cosine similarity, for momentum-based outer optimizers, falling from 30% at 2 workers to 10% at 16 even with IID data".

## OK table

| Line | Number | Paper | Class | Where found |
|---|---|---|---|---|
| 275 | 1B, token-matched | SPES | OK-raw | v3 Table 1 caption ("same 1B-parameter MoE architecture and 50B training tokens"), paper.txt l.303-304 |
| 275 | 8-task average | SPES | OK-raw | v3 Table 1, 8 benchmark columns, l.306 |
| 275 | 2B, 7B, 9B in Table 3 | SPES | OK-raw | v3 HTML Table 3 rows SPES-2B/7B/9B (paper_html l.533, 602, 619); §4 text l.681 |
| 275 | 48.99 to 50.95 (v3) | SPES | OK-raw | v3 Table 4, paper.txt l.450-451; §4.2 text l.469-470 |
| 275 | 50.5 to 51.3 (v1, v2) | SPES | OK-raw | v1 and v2 paper.txt l.449-451 and §4.2 text l.458-460 |
| 276 | 1B dense; re-route every 64 tokens; Table 3 | DiPaCo 2403.10616 v1 | OK-raw | q4b paper.txt l.703, 796-797 (11.38, "matching the performance of a" 1B), Table 3 l.825 |
| 277, 293 | 8×-batch DP; 8× more sequential steps (8× updates) | DiLoCo 2311.08105 v3 | OK-raw | Table 2, l.220-228 (rows: 16.23, 15.30, 15.30, 14.72, 15.02 by row order); §5 "8× updates row" l.574 |
| 287 | K = 32, 64, 128 | FoMoE 2606.19025 v2 | OK-raw | Table 6 rows, tables_v2.txt l.75-92 |
| 288 | O_e ≈ 4 | FoMoE v2 | OK-raw | §6.2, paper_html.txt l.656 ("O_{e}\approx 4") |
| 289 | "±" per dataset (§5) / per seed (App. F) | FoMoE v2 | OK-raw | paper_html l.625 (under §5, heading l.557), l.1762 (under App. F, heading l.1741) |
| 291 | 8 experts (comparison glyph lost) | SMoE-Dropout 2303.01610 v1 | OK-raw | q6 paper.txt l.546-552 (§4.4 width study); see O5 |
| 292 | exactly 2 holders | ours (02b's assumption about our design) | OK-ours | not a paper number |
| 298 | 4 workers, H = 125, 40 rounds, 4× more steps | ours | OK-ours | stage0-report l.83, 212 |
| 302 | 46M; 4; 125; 40; 4× steps; +6.1% | ours | OK-ours | stage0-report §3.3 l.82-83, 161 |
| 303 | 150M, 8 workers, H = 500 | DiLoCo v3 | OK-raw | Table 2 caption and §3 setup; l.258 |
| 303 | 128 rounds | DiLoCo v3 | OK-raw | l.258 "T = 128 times H = 500 inner steps (64,000" |
| 303 | Nesterov 0.7/0.9 | DiLoCo v3 | OK-raw | §3.1 l.407-408 |
| 303 | +0.75% | DiLoCo v3 | OK-inference | ln15.02/ln14.72 − 1 = 0.75%; column labelled "(inference)" |
| 304 | −0.68% | DiLoCo v3 | OK-inference | ln15.02/ln15.30 − 1 = −0.68% |
| 305 | 150M, 4 workers, H 150/500, 4× batch | Khaled 2509.10439 v2 | OK-raw | Table 3 (HTML; PDF l.1270-1316 garbled) |
| 305 | +1.4% / +3.1% | Khaled v2 | OK-inference | 17.58, 18.44 vs DP-4× 16.89: 1.42%, 3.11% |
| 306 | H = 50, Nesterov lr 1.0 | Khaled v2 | OK-raw | Table 3: 16.38 |
| 306 | −1.1% | Khaled v2 | OK-inference | ln16.38/ln16.89 − 1 = −1.08% |
| 307 | 178M, 4 workers, H = 30 | Horoi 2607.03011 v1 | OK-raw | Table 2 l.499-506; setup l.341-345 |
| 307 | ≈226 rounds | Horoi v1 | OK-inference | note l.314; 20 × 178M = 3.56B tokens (l.341) ÷ 524k (l.342) ÷ 30 = 226.5 |
| 307 | +1.9% / +1.0% | Horoi v1 | OK-inference | 2.937, 2.911 vs DP 2.881 (l.500, 505-506): 1.94%, 1.04% |
| 308 | 35M, 4 workers, H = 30 | DiLoCo scaling laws 2503.09799 v1 | OK-raw | Table 4 l.383-398 |
| 308 | +2.0% | Scaling laws v1 | OK-raw | printed "3.554 (+2.0%)", l.392 (and 3.554/3.485 = +1.98%) |
| 309 | 35M, 4 workers, H 30/100 | Streaming DiLoCo 2501.18512 v1 | OK-raw | Table 6 l.1768-1774 |
| 309 | Nesterov 0.4 | Streaming DiLoCo v1 | OK-raw | §3.2 l.443 ("optimal at small scale at 0.4") |
| 309 | +2.6% / +3.7% | Streaming DiLoCo v1 | OK-inference | 3.60, 3.64 (Table 6) vs DP 3.51 (Table 5, l.1694): 2.56%, 3.70%; see O1 |
| 310 | 1.1B, 4 workers, H 125/500, 4× batch DP, Nesterov 0.7 | OpenDiLoCo 2407.07852 v1 | OK-raw | Table 2 l.368-375; §3 l.293-296 |
| 310 | +0.96% / +2.4% | OpenDiLoCo v1 | OK-inference | 10.76, 11.14 vs 10.52: 0.96%, 2.43% |
| 311-312 | 135M, 4 workers, Kx 16/256 | DES-LOC 2505.22549 v1 | OK-raw | §4.1 l.373-381; Fig. 5 panel labels l.553 |
| 311 | +9.7% / +24% | DES-LOC v1 | OK-inference | 12.77 vs 10.20 and 17.79 vs 10.19 (Fig. 5 legend l.540-544): 9.68%, 24.00% |
| 312 | +41.6% / +23.8% | DES-LOC v1 | OK-inference | 26.77 vs 10.20 and 17.72 vs 10.19: 41.55%, 23.83% |
| 314 | 3.56B tokens, 524k per step, 30 | Horoi v1 | OK-inference | inputs at l.341-342 (20× params; 524k global batch) |
| 318 | 1.44% in loss | DiLoCo v3 | OK-inference | ln15.30/ln14.72 − 1 = 1.44% |
| 318 | (S/S_min − 1)(E/E_min − 1) = 1; B_crit = E_min/S_min; twice the steps and examples | McCandlish 1812.06162 v1 | OK-raw | §2.3, Eqs. 2.11-2.12 l.337, 346; "twice" l.356-357 |
| 318 | data size rather than model size | CBS 2410.21676 v4 | OK-raw | abstract l.22-23 |
| 318 | R steps of batch KM; MKR sequential | Woodworth 2002.07839 v2 | OK-raw | §1 l.64, §2 Eq. 3; "M KR … sequentially" §5 l.556 (see O6) |
| 318 | 4× more steps; batch 128 vs 32 | ours | OK-ours | stage0-report l.83 |
| 319 | 150M, 4 workers, H = 50; 17.75 vs 16.38 | Khaled v2 | OK-raw | Table 3 HTML l.953, 965 |
| 319 | about 2.9% in loss | Khaled v2 | OK-inference | ln17.75/ln16.38 − 1 = 2.87% |
| 319 | 178M, 4 workers, H = 30; 2.937, 2.911, 2.881 | Horoi v1 | OK-raw | Table 2 l.500-506 |
| 319 | 20M, pretrained start | Async Local-SGD 2401.09135 v2 | OK-raw | §4 l.319-344 |
| 319 | 2.179 → 2.137; 2.108 | SlowMo 1910.00643 v2 | OK-raw | Table B.1 l.830-838 (garbled; row order Local Adam, SGP, AR-Adam) |
| 319 | 1.6 at 8 workers | Horoi v1 | OK-raw | Table 5 (App. A) l.925-929 "DiLoCo SGD 0.00138 1.6" |
| 319 | values greater than 1 | Khaled v2 | OK-raw | abstract l.23 |
| 319 | server lr 1 (FedOpt) | FedOpt 2003.00295 v5 | OK-raw | Remark 1, l.388 |
| 319 | 1/√M | DiLoCo v3; Decoupled DiLoCo 2604.21428 v1 | OK-raw | DiLoCo §6.2 l.841-842; Decoupled App. D.2 l.1763-1770 |
| 319 | 30% at 2 workers to 10% at 16 | Khaled v2 | OK-raw | App. A.1.3 l.1167 |
| 319 | up to 6.32% | Defazio 2512.17131 v3 | OK-raw | §1 l.44 |
| 320 | 12.77 → 26.77 (Kx 16); 17.79 vs 17.72 (Kx 256) | DES-LOC v1 | OK-raw | Fig. 5 legend l.540-544 |
| 320 | 4.732 vs 2.106 | SlowMo v2 | OK-raw | Table B.3, App. B.4 l.953-959 (row order avg/reset/maintain) |
| 320 | about 20 steps | ours, from β2 = 0.95 | OK-inference | 1/(1 − 0.95) = 20; labelled "Inference (01)" |
| 320 | β2 = 0.95; H = 125; 1e-3 for 80% | ours | OK-ours | stage0-report l.67, 83 |
| 321 | +2.0% (35M), +1.5% (90M), +0.3% (2.4B) | Scaling laws v1 | OK-raw | Table 4 printed percentages l.392, 393, 398 |
| 321 | 75M; 1.3B | Sani et al. 2405.10853 v3 | OK-raw | Fig. 3 caption l.1117-1122 |
| 321 | 86M smallest body | DEPT 2410.05021 v5 | OK-raw | 86.4M, App. A l.1231, 1246; Table 13 l.1654; App. B.7 l.1676-1690 |
| 321 | 35M | Scaling laws v1 | OK-raw | Table 4 |
| 322 | 178M, 8 workers; 2.950, 2.957, 2.976, 3.008 at H 30/60/120/240 | Horoi v1 | OK-raw | Table 4 l.556-567 |
| 322 | +2.4% to +4.4% | Horoi v1 | OK-inference | vs 2.881: 2.40%, 4.41% |
| 322 | 35M, 4 workers, +2.6% / +3.7% | Streaming DiLoCo v1 | OK-inference | as line 309 (see O1) |
| 322 | 1.1B, 4 workers; 10.76 / 11.14 / 10.52 | OpenDiLoCo v1 | OK-raw | Table 2 l.368-370 |
| 322 | 1.5B, 8 workers; 18.65, 22.67, 28.17 at H 100/500/1,000; 17.53 | Factored Gossip 2606.22768 v1 | OK-raw | §5.1 setup l.464-467; §5 text l.543-545; §6 text l.754 |
| 322 | +2.2%, +9.0%, +16.6% | Factored Gossip v1 | OK-inference | 2.16%, 8.98%, 16.56% |
| 322 | about 190, 38, 19 rounds | Factored Gossip v1 | OK-inference | 10B ÷ (512 × 1024) ≈ 19,073 steps ÷ H |
| 322 | 1B (Fig. A2) | SPES v3 | OK-raw | Fig. A2 caption l.1150; App. B, 1B H ablation at 100B, l.947-949 |
| 322 | H = 250 to 2,000 | Khaled v2 | OK-raw | App. A.1.2 l.1126 |
| 322 | a quarter of the compute | Khaled v2 | OK-raw | DP 1× batch 18.07, Table 3 l.1277 |
| 323 | H ∝ 1/η² | QSR 2310.14423 v2 | OK-raw | abstract l.35; §1 l.169 |
| 323 | final 20% cool-down; 10B | INTELLECT-1 2412.01152 v1 | OK-raw | §3.1 l.466-474 (see O2) |
| 323 | 1e-3 for 80%; 1e-4 | ours | OK-ours | stage0-report l.67 |
| 324 | 6%; 46M | ours | OK-ours | stage0-report l.82, 161 |
| 325 | 2.8B and 3.8B active | Decoupled DiLoCo v1 | OK-raw | §5.5 l.770, 834-849 |
| 325 | 54M MoE | FoMoE v2 | OK-raw | Table 1 "∼54M", tables_v2.txt l.28; App. F l.114 |
| 329 | 125M, 4 clients, local batch 32, global batch 128 | Photon 2411.02908 v2 | OK-raw | Fig. 6 caption l.574-579; Table 4 caption l.582-585 |
| 329 | about half of DiLoCo's wall time | Photon v2 | OK-raw | Table 4, N = 4: 0.49× and 0.5×, l.598-599 |
| 329 | outer lr above 0.1 | Photon v2 | OK-raw | Fig. 6 caption l.574-579 |
| 329 | K = 128 (Nesterov degrades) | FoMoE v2 | OK-raw | Table 5 (DiLoCo): M = 4, 420.49 at K = 128 against 124.17 at K = 64 |
| 329 | H = 1,000 and 2,000 (Nesterov lr 1.0 worse than plain) | Khaled v2 | OK-raw | Table 3 HTML: 18.75 vs 18.18; 18.36 vs 18.11 |
| 330 | H = 1,000; 160M to 1.5B | Factored Gossip v1 | OK-raw | §6 text l.749-751 |
| 334 | 2.8B active | Decoupled DiLoCo v1 | OK-raw | §5.5 |
| 334 | H 100-150, β2 = 0.95, 4 workers, 6.1 points | ours | OK-ours | stage0-report l.67, 83, 161 |

PROBLEM rows (not in the table above): l.298 "about 10M"; l.302 "~10M"; l.321 "~10M"; l.287 FoMoE percentages; l.305 "≈160 / ≈48"; l.306 "≈480"; l.310 "352 / 88"; l.311 "≈200 / ≈12.5"; l.312 "≈200 / ≈12.5".

Manifest: 7 missing papers appended to audit3-parts/manifest.md (1812.06162, 2410.21676, 2002.07839, 2512.17131, 2405.10853, 2412.01152, 1910.06378).

Status: COMPLETE.
