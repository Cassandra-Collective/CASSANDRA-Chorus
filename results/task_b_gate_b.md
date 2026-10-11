# Task B · Gate B report

Generated 2026-10-11 06:43 UTC by `python -m scripts.analyze_task_b` (code `ee2a7dd`) from the run logs in `C:\Users\senso\chorus-runs`, 12 completed matrix runs. Test bits per character on the whole text8 test split (4,999,936 characters); lower is better.

## S0-A-04 for the sliced arm: FAIL

| Seed | Verdict | Detail |
|---|---|---|
| 7 | fail | sliced +11.3% (limit +5%) |
| 11 | fail | sliced +10.3% (limit +5%) |
| 19 | fail | sliced +10.7% (limit +5%) |

S0-A-06 requires the criterion on every seed. The other arms are reported for diagnosis.

## Test bits per character by arm and seed

| Arm | Seed 7 | Seed 11 | Seed 19 | Gap to centralized: mean (range) |
|---|---|---|---|---|
| Centralized | 1.4388 | 1.4386 | 1.4353 | reference |
| Full-model averaging | 1.5300 (+6.3%) | 1.5242 (+5.9%) | 1.5219 (+6.0%) | +6.1% (+5.9% to +6.3%) |
| Partial update | 1.5504 (+7.8%) | 1.5474 (+7.6%) | 1.5408 (+7.3%) | +7.6% (+7.3% to +7.8%) |
| Sliced | 1.6020 (+11.3%) | 1.5867 (+10.3%) | 1.5887 (+10.7%) | +10.8% (+10.3% to +11.3%) |

## Where the sliced arm's gap comes from

Each step adds one restriction, measured by two arms that differ only in it (percent of centralized bits per character, same seed). The steps sum to the sliced arm's gap.

| Step | Arms compared | Seed 7 | Seed 11 | Seed 19 | Mean (range) |
|---|---|---|---|---|---|
| local averaging | full-model averaging vs centralized | +6.3% | +5.9% | +6.0% | +6.1% (+5.9% to +6.3%) |
| partial updates | partial update vs full-model averaging | +1.4% | +1.6% | +1.3% | +1.4% (+1.3% to +1.6%) |
| masked routing | sliced vs partial update | +3.6% | +2.7% | +3.3% | +3.2% (+2.7% to +3.6%) |

## Runs

| Arm | Seed | Run ID | Commit | Final validation bpc | Least-used expert share | Negligible experts | Resumed |
|---|---|---|---|---|---|---|---|
| Centralized | 7 | `20261009T060425Z_taskB-central_s7` | `e0851aa` | 1.3378 | 0.199 | 0 | 0 |
| Centralized | 11 | `20261010T093641Z_taskB-central_s11` | `df3a7ac` | 1.3399 | 0.194 | 0 | 0 |
| Centralized | 19 | `20261010T163249Z_taskB-central_s19` | `df3a7ac` | 1.3349 | 0.168 | 0 | 0 |
| Full-model averaging | 7 | `20261010T002852Z_taskB-fullavg_s7` | `1aba651` | 1.4486 | 0.189 | 0 | 1 |
| Full-model averaging | 11 | `20261010T143649Z_taskB-fullavg_s11` | `df3a7ac` | 1.4457 | 0.214 | 0 | 0 |
| Full-model averaging | 19 | `20261010T215606Z_taskB-fullavg_s19` | `a871210` | 1.4427 | 0.217 | 0 | 0 |
| Partial update | 7 | `20261009T220408Z_taskB-partial_s7` | `bb20b0e` | 1.4750 | 0.179 | 0 | 0 |
| Partial update | 11 | `20261010T125827Z_taskB-partial_s11` | `df3a7ac` | 1.4698 | 0.174 | 0 | 0 |
| Partial update | 19 | `20261010T201620Z_taskB-partial_s19` | `408a317` | 1.4648 | 0.157 | 0 | 0 |
| Sliced | 7 | `20261009T194909Z_taskB-sliced-coverage_s7` | `bb20b0e` | 1.5336 | 0.104 | 0 | 0 |
| Sliced | 11 | `20261010T111737Z_taskB-sliced-coverage_s11` | `df3a7ac` | 1.5176 | 0.011 | 1 | 0 |
| Sliced | 19 | `20261010T183601Z_taskB-sliced-coverage_s19` | `dc23a78` | 1.5219 | 0.078 | 0 | 0 |

## Decision gate B (PLAN section 5)

- Gap within the criterion: proceed to Stage 1.
- Moderate gap: report it, and decide whether the flagship is still worth building at that cost.
- Large gap: treat as a negative result, publish it, and reconsider the architecture.

PLAN leaves "moderate" and "large" undefined; which applies, and what follows, is the owner's decision.
