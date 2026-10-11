# Task B · Timing pilot

Generated 2026-10-09 05:01 UTC by `python -m scripts.pilot_task_b_timing` (code `51b8a91`, config `configs/task_b/pilot.toml`, run `20261009T044556Z_taskB-timing-pilot_s7`). Untrained models: times and memory only. Median of the timed steps after warm-up; fp32, explicit attention, sparse dispatch (owner decisions). Peak memory is each model's own: model, optimizer state and activations, with nothing else on the GPU.

## Milliseconds per optimizer step (peak GPU memory, MiB)

| Parameters | Width | Batch × 256 | Centralized | Sliced worker | Partial-update worker | Full-averaging worker |
|---|---|---|---|---|---|---|
| 20,476,672 | 256 | 32 | 149 (2109) | 116 (1966) | 145 (1966) | 147 (2112) |
| 20,476,672 | 256 | 64 | 249 (3826) | 219 (3669) | 266 (3646) | 271 (3824) |
| 31,985,600 | 320 | 32 | 191 (2717) | 152 (2485) | 192 (2493) | 234 (2718) |
| 31,985,600 | 320 | 64 | 334 (4853) | 324 (4617) | 404 (4624) | 433 (4853) |
| 46,050,432 | 384 | 32 | 405 (3423) | 215 (3061) | 247 (3059) | 310 (3422) |
| 46,050,432 | 384 | 64 | 570 (5945) | 475 (5609) | 673 (5552) | 587 (5969) |

## Merge and evaluation

| Parameters | Merge of 4 results (ms) | Whole test split (s) | Validation curve, first 1M characters (s) |
|---|---|---|---|
| 20,476,672 | 70 | 54 | 6.8 |
| 31,985,600 | 130 | 64 | 15.6 |
| 46,050,432 | 78 | 109 | 18.4 |
