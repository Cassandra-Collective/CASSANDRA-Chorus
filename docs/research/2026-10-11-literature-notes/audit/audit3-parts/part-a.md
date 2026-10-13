# Part A: sections 3.4, 3.5 (lines 457-488) and section 5 table (lines 566-587)

Raw paths are relative to PAPERS (see manifest.md). Arithmetic: scratchpad/audit3scripts/arith_a.py.
Percent gaps in cross-entropy use rel(a,b) = ln(a)/ln(b) - 1 on perplexities.

## Counts (part A)

Counted by individual number (a cell "+1.6%, +2.9%, +2.1%" is 3 numbers); PROBLEMs counted by entry.

| Class | Count |
|---|---|
| OK-raw | 126 |
| OK-inference | 21 |
| OK-ours | 16 |
| NOTES-ONLY (search/citation counts, code facts via 04a) | 16 |
| PROBLEM | 3 entries (7 numbers: +0.93, −0.23; 20, 10, 5; −0.6%, −0.7%) |

## PROBLEM list

1. **Line 572 (section 5, SPES row, quality column).** Text: "8-task average +0.93 points above centralized, DiLoCo −0.23 (1B, token-matched 50B, single runs; Table 1, v3)". The paper prints only the averages 50.95, 50.02, 49.79 (q4a/2602.11543v3/paper_html.txt, Table 1); +0.93 = 50.95 − 50.02 and −0.23 = 49.79 − 50.02 are differences computed by the writer. The table's stated note says only gaps marked "(inference)" were computed by a researcher, so these read as paper numbers. Derived but unlabelled. **Fix:** write "50.95 against 50.02 centralized and 49.79 DiLoCo (Table 1, v3)", or keep the differences and add "(inference)".

2. **Line 573 (section 5, FoMoE row, synchronization column).** Text: "K = 32, 64, 128 (20, 10, 5 rounds)". FoMoE never states round counts; it states 640 optimizer batches (Table 7 reproducibility summary, v2) and total rounds = N_tok/(K·B_g) (§5, Eq. 12). 640/32 = 20, 640/64 = 10, 640/128 = 5 is the researcher's arithmetic (note 06 §8: "K = 128 means 640/128 = 5 rounds"). Derived but unlabelled. **Fix:** "K = 32, 64, 128 (20, 10, 5 rounds; inference from 640 optimizer batches, Table 7)".

3. **Line 585 (section 5, SDP row, quality column).** Text: "−0.6% to −0.7% in loss against data parallel at 1B, FLOP-matched (Table 1, v5)". SDP Table 1 prints validation losses only (DDP 2.452; B-SDP and Bb-SDP 2.437; N-SDP 2.434; q3/2507.09029/paper.txt lines 391-398). The percentages are note 03's arithmetic: 2.437/2.452 − 1 = −0.61%, 2.434/2.452 − 1 = −0.73%. Derived but unlabelled under the table's own note. **Fix:** add "(inference)": "−0.6% to −0.7% in loss (inference; 2.437 and 2.434 against 2.452) ...".

## Minor remarks (not PROBLEMs; locators that could be tightened)

- Line 469 (BTM row of the 3.4 table): "+3.0% to +5.3% worse (inference from Table 4)". The random-split perplexities are in Table 4, but the compute-matched dense comparator (22.5, 18.5, 17.0, 16.3) is in Table 1. Line 576 correctly says "Tables 1 and 4". Suggest "inference from Tables 1 and 4".
- Line 474 (KALAVAI): "with 3× parameters and inference (Table 4)". The +0.47% and +0.34% are in Table 4 and §4.3; the "3×" comes from §1 (inference compute × N) and §4.6 ("3× the unfrozen parameters"), both inside the read §1-§7. Suggest "(Table 4; 3× from §4.6)".
- Line 575 (BTX): "averaged uniformly over 4 branches": three trained branches plus the seed model as fourth expert (BTX §1, §3.2). Correct as a count; "3 branches plus the seed" would be more exact.
- Line 572 (SPES): "H = 50 (1B) or 100 (2B, 7B, 9B)" omits the App. B switch to H = 50 after 70% of tokens for 2B and 7B; line 459 states it. Not a number error.

## OK checks

| Line | Number | Paper | Class | Where found |
|---|---|---|---|---|
| 459 | 1.1B (controlled), 2B, 7B, 9B upcycled | SPES 2602.11543 v3 | OK-raw | paper_html.txt Table 2 (0.3B/1.1B, 0.8B/2.1B, 1.6B/7.3B, 3.1B/9.4B); §4.1 |
| 459 | H = 50 (1B), 100 (larger) | SPES v3 | OK-raw | Table A1 "Synchronization Steps H 100 100 100 50" |
| 459 | per-node batch halved, H = 50 after 70% of tokens (2B, 7B) | SPES v3 | OK-raw | App. B, paper.txt l.946-947 |
| 459 | 50.95, 50.02, 49.79 (8-task avg, 1B) | SPES v3 | OK-raw | Table 1 (HTML) |
| 459 | 8 tasks | SPES v3 | OK-raw | Table 1 columns ARC(e), ARC(c), PIQA, SciQ, OBQA, BoolQ, SIQA, WinoGrande |
| 459 | BoolQ +5.45, ARC-e +1.93; trails on PIQA, SciQ, WinoGrande | SPES v3 | OK-inference | 60.95−55.50 = 5.45; 52.11−50.18 = 1.93; 66.27<67.08, 76.50<77.50, 50.83<50.91 (Table 1); labelled "(inference, 04a)" |
| 459 | 48.99 without warm-up | SPES v3 | OK-raw | Table 4 (HTML) and §4.3 prose "from 48.99 to 50.95" |
| 459 | paper: strength 0.1, interval 300, warm-up 12,500 | SPES v3 | OK-raw | §4.1 paper.txt l.359-361 ("Tw ... 12,500 ... Ti ... 300 ... 0.1 and 4") |
| 459 | code: interval 500, start 0.01, decay 10,000 | SPES code | NOTES-ONLY (code, via 04a) | 04a l.113: `run_parameter_server.sh` launcher defaults, file read in full per 04a read status |
| 461 | 54M MoE | FoMoE 2606.19025 v2 | OK-raw | Table 1 "Small Proxy ... ∼54M" (r2/2606.19025/tables_v2.txt) |
| 461 | 4 workers, 2 holders | FoMoE v2 | OK-raw | Table 6 M = 4, O_e = 2 |
| 461 | +1.6%, +2.9%, +2.1% at K = 32, 64, 128 | FoMoE v2 | OK-inference | Table 6 LocalAdamW fixed M=4: 112.00/103.91, 119.53/104.47, 123.50/111.89 → 1.61, 2.90, 2.09; labelled "(inference)" |
| 461 | skip-token in a figure only | FoMoE v2 | OK-raw | Fig. 7, §6.3 |
| 461 | full replica degrades with K and M | FoMoE v2 | OK-raw | Table 4: M=8 106.30, 112.99, 159.71 |
| 461 | 138.88 against 159.71 (8 workers, K = 128) | FoMoE v2 | OK-raw | Table 6 M=8 K=128 fixed O_e=4 138.88, O_e=8 159.71 |
| 467 | 19% to 37% of steps | MoE-DisCo 2601.06857 v1 | OK-inference | Table 1: 4100/21150=19.4% ... 7800/21000=37.1%; labelled "(inference from Table 1)" |
| 467 | §4.5.1 random assignment, figure only | MoE-DisCo v1 | OK-raw | §4.5.1, Fig. 6 |
| 468 | 7B | BTX 2403.07816 v1 | OK-raw | §1 "Llama-2 7B ... seed model" |
| 468 | 47.9 against 47.3, about equal GPU-days | BTX v1 | OK-raw | Table 3 (926.1 vs 1007.1 GPU-days) |
| 468 | §4.3.1 "mainly trains" | BTX v1 | OK-raw | paper.txt l.554 |
| 469 | +3.0% to +5.3% | BTM 2208.03306 v1 | OK-inference | Table 4 random ensemble 24.7, 21.5, 19.2, 18.9 vs Table 1 T-LM 22.5, 18.5, 17.0, 16.3 → 3.00, 5.15, 4.30, 5.30; labelled (see minor remark on locator) |
| 470 | 2×4 paths +0.4% | DiPaCo 2403.10616 v1 | OK-inference | Table 1: 14.86 vs 14.72 → 0.35%; labelled |
| 470 | 150M, 8× longer | DiPaCo v1 | OK-raw | Table 1 "Baseline, 8× steps 8× 8× 150M 14.72" |
| 471 | 3.85% to 17.56% | SMALLTALK 2410.03529 v2 | OK-raw | App. Table 3 (printed percentages, paper.txt l.1357, 1363) |
| 472 | every 500 local steps | DEPT 2410.05021 v5 | OK-raw | App. l.1373 "500 steps, equal to DEPT's Nlocal"; Table 9 rows |
| 472 | 31.6 against 36.9 | DEPT v5 | OK-raw | Table 3 GLOB 31.6, STD (α=1) 36.9 |
| 472 | 86M; 32.4 against 31.2 | DEPT v5 | OK-raw | Table 13 (12-block, 86.4M body) GLOB 32.4, STD (α=0) 31.2 |
| 473 | Fig. 6 only; 10% failure rate; WikiText-2 | Learning@home 2002.04013 v3 | OK-raw | §4 l.580-586 |
| 474 | +0.47% (410M), +0.34% (1B) | KALAVAI 2603.22755 v2 | OK-raw | §4.3 l.403-404, Table 4 |
| 474 | 3× parameters and inference | KALAVAI v2 | OK-raw | §1 l.59-60 (×N inference), §4.6 l.564 (3× unfrozen params); see minor remark |
| 474 | §4.5 quote | KALAVAI v2 | OK-raw | §4.5 heading and §1 l.104 |
| 476 | SPES citers 0 (OpenAlex), 0 (S2) | search | NOTES-ONLY | 04a "Citing papers" |
| 476 | FlexOlmo 16 S2 citers; 25 OpenAlex search works | search | NOTES-ONLY | 04a "FlexOlmo citers" |
| 476 | Gating Dropout 34, MaskMoE 12, HARC 1, FedAlign-MoE 4, DDOME 6; FoMoE none | search | NOTES-ONLY | 06 "Citation counts by source" (S2 column) |
| 476 | four axes | method | NOTES-ONLY | 04a/06 four-axis code |
| 478 | CIFAR-10, §III, v1 | 2507.05685 v1 | OK-raw | Fig. 3 caption "non-IID ... CIFAR10" in §III (l.248) |
| 478 | 4 of 8 | ours | OK-ours | stage0-report l.66, l.122 |
| 478 | about 23 web discovery queries | search log | NOTES-ONLY | WebSearch rows: 02b 12, 04a 10, 04b 1 multi-query row; consistent with "about 23" |
| 478 | 20 arXiv API queries in round 2 | search log | NOTES-ONLY | 06 query log, two export.arxiv.org rows: 20 queries counted |
| 484 | between 35M and 1.5B | Streaming DiLoCo 2501.18512; Factored Gossip 2606.22768 | OK-raw | Streaming DiLoCo "35M" (Fig. 5, App. table); Factored Gossip "1.5B parameter Llama 3" (§4.1) |
| 486 | 1B to 1.3B; small federated LM | SDP 2507.09029 v5; Filippova 2509.22418 v1; Ro 2204.09715 | OK-raw | SDP §4 "134M, 500M, and 1B"; Filippova abstract "1.3B-parameter"; Ro 21M (row A3) |
| 487 | 128-expert MoE; "relatively marginal for Mixtral"; 8 experts | Router KD 2603.02217 v1 | OK-raw | §4 coarse-grained experts prose, paper.txt l.381-385 ("128 experts", "only 8 experts per layer") |
| 572 | H = 50 (1B) or 100 (2B, 7B, 9B) | SPES v3 | OK-raw | Table A1 |
| 572 | 1.1B to 9.4B | SPES v3 | OK-raw | Table 2 |
| 572 | 50B tokens, Table 1 | SPES v3 | OK-raw | Table 1 caption "50B training tokens" |
| 572 | uniform (one integer) | SPES code | NOTES-ONLY (code, via 04a) | 04a: `num_train_experts_per_node`, single integer |
| 573 | O_e/M of the experts | FoMoE v2 | OK-raw | Eq. 6, p_hit = O_e/M |
| 573 | 54M proxy; ~51M embeddings (inference) | FoMoE v2 | OK-inference | 200,019 × 256 = 51.2M (Table 1 d_model 256; Table 7 vocab 200,019); labelled |
| 573 | +1.6%, +2.9%, +2.1% | FoMoE v2 | OK-inference | as line 461; labelled "(inference, Table 6, v2)" |
| 573 | centralized only in Fig. 5 | FoMoE v2 | OK-raw | Fig. 5 caption ("Centralized" is the quality reference) |
| 573 | K = 32, 64, 128 | FoMoE v2 | OK-raw | Table 7 sweep grid |
| 574 | one expert per submodel (1 of 4); 4 experts | MoE-DisCo v1 | OK-raw | §4.1.1 "set the number of experts to 4" |
| 574 | Qwen1.5-MoE-2.7B, LLaMA-MoE-3.5B | MoE-DisCo v1 | OK-raw | abstract, §4.1 |
| 574 | 19% to 37% | MoE-DisCo v1 | OK-inference | as line 467; labelled |
| 575 | 7B; 4 branches; 80B tokens | BTX v1 | OK-raw | §1 (fourth expert), §4.1 "another 80B tokens" |
| 575 | 47.9 against 47.3 | BTX v1 | OK-raw | Table 3 |
| 576 | 125M to 1.3B per expert | BTM v1 | OK-raw | Table 1 caption (125M, 350M, 750M, 1.3B) |
| 576 | +3.0% to +5.3% | BTM v1 | OK-inference | Tables 1 and 4; labelled |
| 577 | √(paths) | DiPaCo v1 | OK-raw | §2.7 "rescaled the outer gradient norm by the square root of the number" (l.490-491) |
| 577 | 150 inner steps; 62 in Table 5 | DiPaCo v1 | OK-raw | §4 "τ = 150 steps" (l.743); Table 5 caption "62 inner optimization steps" |
| 577 | 150M paths, up to 256 paths | DiPaCo v1 | OK-raw | abstract l.22 |
| 577 | +0.4% | DiPaCo v1 | OK-inference | 14.86 vs 14.72; labelled |
| 578 | about 94 times | SMALLTALK v2 | OK-raw | App. A.4 "Ncomm ≈ 94" (l.1416) |
| 578 | 335M and 1.3B experts, 4 to 32 experts | SMALLTALK v2 | OK-raw | §3 l.379-380 |
| 578 | 3.85% to 17.56% | SMALLTALK v2 | OK-raw | App. Table 3 |
| 579 | every 500 local steps | DEPT v5 | OK-raw | as line 472 |
| 579 | 86M to 298M bodies; 1.2B multilingual | DEPT v5 | OK-raw | App. l.1231-1237 ("86.4M", "298M"), Table 9 "Multilingual 24 2048 1.2B" |
| 579 | 31.6 vs 36.9; 32.4 vs 31.2 | DEPT v5 | OK-raw | Tables 3 and 13 |
| 580 | 256 experts over 16 layers; WikiText-2; Fig. 6 | Learning@home v3 | OK-raw | §4 l.561, l.580 |
| 581 | 32 experts; 30 clients | FedMoE 2408.11304 v1 | OK-raw | §I l.37 ("32 experts per layer"); §V setup l.384 ("30 clients") |
| 582 | 7B base; 37B total, 20B active | FlexOlmo 2507.07024 v4 | OK-raw | §4.4 l.426, l.434-435 |
| 582 | 46.7, 47.8, 51.5 (2× FLOPs) | FlexOlmo v4 | OK-raw | Table 1 (§5.1) |
| 583 | capacity 2 to 6; 8 ResNet experts | FLEX-MoE 2512.23070 v2 | OK-raw | §IV "C = 20, E = 8, kc ∈ [2, 6]" (l.311, 378) |
| 583 | 100 rounds, 3 local training rounds | FLEX-MoE v2 | OK-raw | §IV l.359-360 |
| 584 | K/N | Filippova 2509.22418 v1 | OK-raw | §3 count vector m[i] = K/N (l.270-275) |
| 584 | lr 0.4; H = 100 | Filippova v1 | OK-raw | §4 l.344-345 ("learning rate 4 × 10^-1 ... H = 100") |
| 584 | 1.3B dense | Filippova v1 | OK-raw | abstract |
| 584 | −1.6% to +4.3% | Filippova v1 | OK-inference | Table 1: 12.24 and 14.21 vs Streaming DiLoCo 12.75 → −1.60, +4.26; labelled |
| 585 | 134M to 1B | SDP v5 | OK-raw | §4 l.376 |
| 586 | 12 to 32 GB; 4 clients | HFedMoE 2601.00583 v1 | OK-raw | §IV l.760, l.767 |
| 586 | Switch-base-64; DeepSeek-MoE-16B | HFedMoE v1 | OK-raw | §IV-A |
| 587 | 4 of 8, top-2, 1 to 4 holders, mean 2 | ours | OK-ours | report header (coordinator facts); stage0-report l.66 |
| 587 | H = 125, 40 rounds; fresh AdamW | ours | OK-ours | stage0-report l.83; report header |
| 587 | 46.05M (~10M active) | ours | OK-ours | stage0-report l.82; report header |
| 587 | +10.8%; 20,000 steps; batch 32; seeds 7, 11, 19; §3.3 | ours | OK-ours | stage0-report l.20, l.69, l.83, §3.3 table |
| 587 | S0-F-05 | ours | OK-ours | requirement id (not a paper number) |

Counting rule: each distinct value or tight value-group in a cell counts once (e.g. "+1.6%, +2.9%, +2.1%" = 3 numbers; "50.95, 50.02, 49.79" = 3). The table above groups some rows; counts in the header are by individual number.
