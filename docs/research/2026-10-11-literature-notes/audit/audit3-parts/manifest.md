# Audit 3 manifest: papers cited in report lines 457-588 (sections 3.4, 3.5, 3.6, 4, 5)

PAPERS = /c/Users/senso/AppData/Local/Temp/claude/C--Users-senso-OneDrive-Masa-st--CASSANDRA-Chorus/7495f590-a728-4f3b-bb8e-04b29778f8a0/scratchpad/papers
Raw-file versions confirmed from the arXiv stamp in each paper.txt (all match the version the notes say was read).

| Name in report | arXiv ID | Raw dir(s) under PAPERS | Version read | Read status (from notes) |
|---|---|---|---|---|
| SPES | 2602.11543 | q4a/2602.11543v3 (paper.txt, paper_html.txt); v1, v2 dirs; q4a/diff_v1_v3.txt; spes_v2v3_wdiff.txt | v3 (+v1,v2 diff) | 04a: v3 full text; v1/v2 diffed; v1 §3.2-§4.2, T1, T4, App B, E; code files listed in 04a |
| FoMoE | 2606.19025 | q4a/2606.19025 (paper.txt, paper_html.txt); r2/2606.19025 (tables_v2.txt, html_v2.txt, paper_v1.txt) | v2 | 04a/04b/06: full text v2; tables re-read from v2 HTML |
| MoE-DisCo | 2601.06857 | q4b/2601.06857 | v1 | 04b: full text incl. App A-E |
| BTX | 2403.07816 | q4b/2403.07816 | v1 | 04b: full text incl. App A-C (Table 2 garbled, mapped) |
| BTM | 2208.03306 | q4b/2208.03306 | v1 | 04b: §1-§9 + App Tables 9, 13, Fig 10 |
| DiPaCo | 2403.10616 | q4b/2403.10616 | v1 | 04b: full text incl. §7.1-7.3 |
| SMALLTALK LM | 2410.03529 | q4b/2410.03529 | v2 | 04b: full text incl. App A-C |
| DEPT | 2410.05021 | q4b/2410.05021 | v5 | 04b: full text incl. App A-F |
| Learning@home | 2002.04013 | q4b/2002.04013 | v3 | 04b: full text incl. App A-E |
| KALAVAI | 2603.22755 | q4b/2603.22755 | v2 | 04b: §1-§7 only; appendices not read |
| System-level FedMoE sketch | 2507.05685 | q4a/2507.05685 | v1 | 04a: §I-§III, start of §IV |
| Router KD | 2603.02217 | q2b/2603.02217 | v1 | 02b: Abstract, 1, 3.4, 4 prose, 5; App G not read |
| Khaled et al. (outer optimizers) | 2509.10439 | q1/2509.10439, q1/2509.10439-html | v2 | 01: abstract, §1, §4.2, App A.1.1-A.1.6, Tables 1-5 |
| Horoi et al. (model merging in DiLoCo) | 2607.03011 | q1/2607.03011 | v1 | 01: main body §1-§4.4, App A |
| DiLoCo | 2311.08105 | q1/2311.08105 | v3 | 01: full text |
| Asynchronous Local-SGD | 2401.09135 | q1/2401.09135 | v2 | 01: §4, §7 (Tables 1-4), App 10.1 |
| SlowMo | 1910.00643 | q1/1910.00643 | v2 | 01: §4 setup, Table 1, App B.1, B.3, B.4 (Tables B.1-B.3) |
| Photon | 2411.02908 | q1/2411.02908 | v2 | 01: abstract, §3, §5.1-§5.3, Tables 2-4, App A T6, B.1, C.1, C.2 |
| Streaming DiLoCo | 2501.18512 | q1/2501.18512 | v1 | 01: §3.1 partial, §3.2, Supp. Tables 2, 5, 6, 7 |
| OpenDiLoCo | 2407.07852 | q1/2407.07852 | v1 | 01: main body §1-§4 |
| Factored Gossip DiLoCo | 2606.22768 | q1/2606.22768 | v1 | 01: §4.1, §5 text, §6 (scaling, H), App optimizers; Table 1 garbled, numbers from text |
| DiLoCo scaling laws | 2503.09799 | q1/2503.09799, q6/2503.09799 | v1 | 01: abstract, §1-§4 (Tables 3-5), §5.1, §5.2, §6.1-6.4; 05: §2.2, §3, §4 Finding 1 (Tables 4-5) |
| Filippova et al. (partial updates) | 2509.22418 | q3/2509.22418, q3/2509.22418-html | v1 | 03: full text |
| Ro et al. (cross-device FL LM) | 2204.09715 | q3/2204.09715 | v2 | 03: abstract, §3, §4 partial model training, App A (Tables 2-3), Table 4, App B opening |
| SDP | 2507.09029 | q3/2507.09029 | v5 | 03: full text incl. App A-J |
| Decoupled DiLoCo | 2604.21428 | q1/2604.21428 | v1 | 01: abstract, §1, §2-§3.2, §5.1, §5.4-§6, App D.2, Table 14 |
| DES-LOC | 2505.22549 | q1/2505.22549 | v1 | 01: abstract, §1, Fig 2 caption, §4.1, §5.3, Fig 5 legend values, §5.4 opening |
| StableMoE | 2204.08396 | q2a/2204.08396 | v1 | 02a: abstract, 1, 3, 4.1-4.4 (Tables 2-6, Fig 7) |
| Fan et al. (MoE design choices) | 2402.13089 | q2a/2402.13089 | v1 | 02a: full text |
| MaskMoE | 2407.09816 | q2a/2407.09816 | v4 | 02a: abstract, 1, 3.3-3.4, 4 (Tables 1-2), 5.1-5.4 |
| MoEC | 2207.09094 | r2/2207.09094 | v1 | 06: abstract, intro, method, experiments (Tables 1-4); appendices not read |
| Demons in the Detail | 2501.11873 | q2a/2501.11873 | v2 | 02a: abstract, 1, 2, 4.1-4.2 (Table 1), 5 (Tables 2-4) |
| Aux-loss-free | 2408.15664 | q2a/2408.15664 | v1 | 02a: abstract, 1, 2.2, 3, 4.1-4.2 (Table 2), 4.3 (Tables 3-4), App C |
| Gopinath et al. (declarative-procedural) | 2608.15102 | q2a/2608.15102 | v2 | 02a: abstract, 3, 4.4, 5.1-5.2, App G (Table 9) |
| EMO | 2605.06663 | q4a/2605.06663 | v2 | 04a: §3, §4, §5.1, §5.2, start §5.3 |
| Slicing and Dicing | 2605.11689 | q2a/2605.11689 | v1 | 02a: abstract, 1, 3.1 para, 3.2 generalists para, 3.3 ablations, App A, App C.3 |
| FedRolex | 2212.01548 | q3/2212.01548 | v2 | 03: §4 setup, §4.1-4.5, App A.3-A.5, A.7 Table 8 |
| PVT | 2110.05607 | q3/2110.05607 | v1 | 03: full text |
| IST | 1910.02120 | q3/1910.02120 | v7 | 03: 2.2, 2.3, 3.1, 3.2 (Tables 1-3) |
| FLEX-MoE | 2512.23070 | q2b/2512.23070 | v2 | 02b: full text |
| FedOpt | 2003.00295 | q1/2003.00295 | v5 | 01: §3 Remark 1, discussion (i)-(ii), App D.2 (Tables 8-10) |
| FlexOlmo | 2507.07024 | q2b/2507.07024 | v4 | 02b: Abstract, 1, 2.2, 3, 4, 5, App A.1-A.2, App D |
| HARC | 2606.03391 | q2b/2606.03391 | v1 | 02b: full text incl. App A-D |
| Routing Drift | 2609.32821 | r2/2609.32821 | v1 | 06: abstract, §1, §2, §3.1-3.3, §6.1, §6.2; Table 2 from prose |
| DDOME | 2306.08586 | q2b/2306.08586 | v3 | 02b: Abstract, 1-4, 5 setup+prose, 6, App D-E |
| BAR | 2604.18473 | q2b/2604.18473 | v1 | 02b: Abstract, 1-4, 5.1-5.3, 6 |
| Symphony-MoE | 2509.18542 | q2b/2509.18542 | v2 | 02b: Abstract, 4.6, 4.7, 5 |
| FedAlign-MoE | 2603.21276 | q2b/2603.21276 (v2), q2b/2603.21276v1 | v2 | 02b: full text v2; v1 Table I and setup |
| MedMix | 2608.13911 | q2b/2608.13911 | v1 | 02b: Abstract, 1, 2, experiments prose (setup, cross-client analysis, ablation) |
| ST-MoE | 2202.08906 | q2a/2202.08906, q6/2202.08906 | v2 | 02a: §3 (3.1-3.3 incl. Table 4), 4.1, 7; 05: §3 z-loss para, Table 11, §7 para, App A/B |
| OLMoE | 2409.02060 | q2a/2409.02060 | v2 | 02a: 4.1.1-4.1.7, 5.1-5.3 |
| σ-MoE | 2310.10837 | q2a/2310.10837, q6/2310.10837 | v3 | 02a: 4, 5, 6.1-6.3 (Tables 1,3,4,5), App 8-9; 05: §6 setup, 6.1-6.3 (Tables 1-4), Table 10, App B |
| DeepSeekMoE | 2401.06066 | q2a/2401.06066 | v1 | 02a: 1, 3.2, 3.3, 4.4, 4.5 |
| FjORD | 2102.13451 | q3/2102.13451 | v5 | 03: 3.5, 5 (setup, Table 1), 5.2, 5.3 |
| InclusiveFL | 2202.08036 | q3/2202.08036 | v2 | 03: §4, Tables 2 and 3 |
| QSR | 2310.14423 | q1/2310.14423 | v2 | 01: abstract and §1 only |
| Post-local SGD | 1808.07217 | q1/1808.07217 | v6 | 01: abstract, §1 partial, §3, §4 opening |
| MuLoCo | 2505.23725 | q1/2505.23725 | v3 | 01: abstract, §1 partial, §5 setup, §6.1-6.2 |
| Gating Dropout | 2205.14336 | q2a/2205.14336, r2/2205.14336 | v2 | 02a: full main text 1-6 |
| DeepSeek-V2 | 2405.04434 | r2/2405.04434 | v5 | 06: §2.2.2 and training-hyperparameter para only |
| Switch | 2101.03961 | q2a/2101.03961, q6/2101.03961 | v3 | 02a: 2.2, 2.4 (Tables 3-4); 05: §1, §2.2, §3.1 Fig 4, App D |
| Al-Rfou et al. (T12/T64) | 1808.04444 | q6/1808.04444 | v2 | 05: full text |
| Transformer-XL | 1901.02860 | q6/1901.02860 | v3 | 05: §3.1, §4.1 (Tables 1-3), §4.2, §4.3, §4.5 |
| Adaptive span | 1905.07799 | q6/1905.07799 | v2 | 05: abstract, §1, §2.1, §3 (Tables 1-3), §4 |
| Cooijmans et al. (BN-LSTM) | 1603.09025 | q6/1603.09025 | v5 | 05: §5.3 (Table 3), PTB setup |
| mLSTM | 1609.07959 | q6/1609.07959 | v3 | 05: abstract, §4.1-§4.3 (Tables 1-2) |
| D3PM | 2107.03006 | q6/2107.03006 | v3 | 05: §5.1 (Table 1), App B.2 (Tables 5-6) |
| Shortformer | 2012.15832 | q6/2012.15832 | v2 | 05: §1, §2, §3 (Table 1) |
| Clark et al. (unified scaling laws) | 2202.01169 | q6/2202.01169, q2a/2202.01169 | v2 | 05: §1, §2, §4 para, §5.2, App A, App F.1 + 15M para; 02a: 2-3, 4.2, 4.3, 5.3, App A, B.4 |
| SMoE-Dropout | 2303.01610 | q6/2303.01610, q2a/2303.01610 | v1 | 05: §4.1, §4.2 (Table 1), Fig 5 text; 02a: 1, 3.1-3.2, 4.1-4.4 |

Part files: part-a (§3.4, §3.5, §5 lines 457-488, 566-587), part-b (§3.6 lines 490-530), part-c (§4 rows A1-B4, lines 540-546), part-d (§4 rows B5-D1, lines 547-562).
Each part file: a PROBLEM list (line, exact text, what is wrong, fix) and an OK table (line | number | paper | class | where found).
Classes: OK-raw, OK-inference, OK-ours, PROBLEM, plus NOTES-ONLY for search/citation counts that are not paper numbers.

Rows added by audit 2a (report lines 271-335); arXiv stamps confirmed in each paper.txt:

| Name in report | arXiv ID | Raw dir(s) under PAPERS | Version read | Read status (from notes) |
|---|---|---|---|---|
| McCandlish et al. (large-batch model) | 1812.06162 | q1/1812.06162 | v1 | 01 (D1): abstract, §2.3 (Eqs. 2.11-2.12) |
| Critical batch size scaling | 2410.21676 | q1/2410.21676 | v4 | 01 (D2): abstract and §1 opening |
| Woodworth et al. (local vs minibatch SGD) | 2002.07839 | q1/2002.07839 | v2 | 01 (C2): abstract, §1, §2, §3 opening, §5 lower-bound discussion (fragments) |
| Defazio et al. (primal averaging) | 2512.17131 | q1/2512.17131 | v3 | 01 (B7): abstract, §1; Table 2 not used |
| Sani et al. (Future of LLM pre-training is federated) | 2405.10853 | q1/2405.10853 | v3 | 01 (A7): §6.5, §7.1 partial, Table 3, Fig. 3 caption |
| INTELLECT-1 | 2412.01152 | q1/2412.01152 | v1 | 01 (A5): abstract, §2, §3.1, §3.4, App. A table (garbled) |
| SCAFFOLD | 1910.06378 | q1/1910.06378 | v4 | 01 (C1): abstract, §1, §3.1, §4 partial, §6 partial, §7 intro |
