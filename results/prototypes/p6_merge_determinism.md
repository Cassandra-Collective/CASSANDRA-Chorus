# P6 merge determinism

Plan: `docs/implementations/2026-10-14-solo-prototypes.md`. Model: Task B, 46,050,432 parameters, seed 7. Hardware: NVIDIA GeForce RTX 4070 Laptop GPU; Windows-11-10.0.26300-SP0; PyTorch 2.12.1+cu126 (CUDA 12.6); default CPU threads 14; deterministic algorithms off. One machine.

Each cell compares the variant's output with its reference variant: **equal** (bitwise), or the number of differing elements and the largest absolute difference.

## sliced

| Variant | Reference | plain-1 | nesterov-1 | nesterov-2 | velocity-1 | velocity-2 |
|---|---|---|---|---|---|---|
| baseline | none | `6878ae9c5352` | `6b81ffbb6ed0` | `cf92df7319a7` | `94e546c134d4` | `86bf073efcda` |
| baseline-repeat | baseline | equal | equal | equal | equal | equal |
| cpu-1-thread | baseline | equal | equal | equal | equal | equal |
| cpu-reversed | baseline | equal | equal | equal | equal | equal |
| cpu-shuffled | baseline | equal | equal | equal | equal | equal |
| in-memory | baseline | equal | equal | equal | equal | equal |
| velocity-float32 | baseline | equal | equal | 204,432 differ, max 9.31e-10 | equal | 862,691 differ, max 1.05e-10 |
| delta-rebuild-cpu | baseline | equal | equal | equal | equal | equal |
| delta-direct-cpu | baseline | 355,790 differ, max 4.66e-10 | n/a | n/a | n/a | n/a |
| cuda | baseline | 472 differ, max 3.73e-09 | 463 differ, max 7.45e-09 | 526 differ, max 5.96e-08 | 472 differ, max 3.73e-09 | 927 differ, max 5.96e-08 |
| cuda-repeat | baseline | 472 differ, max 3.73e-09 | 463 differ, max 7.45e-09 | 526 differ, max 5.96e-08 | 472 differ, max 3.73e-09 | 927 differ, max 5.96e-08 |
| cuda-shuffled | baseline | 472 differ, max 3.73e-09 | 463 differ, max 7.45e-09 | 526 differ, max 5.96e-08 | 472 differ, max 3.73e-09 | 927 differ, max 5.96e-08 |
| cuda-true-division | baseline | equal | equal | equal | equal | equal |
| cuda-shuffled-true-division | baseline | equal | equal | equal | equal | equal |
| delta-rebuild-cuda | delta-rebuild-cpu | 472 differ, max 3.73e-09 | 463 differ, max 7.45e-09 | 895 differ, max 5.96e-08 | 472 differ, max 3.73e-09 | 927 differ, max 5.96e-08 |
| delta-direct-cuda | delta-direct-cpu | 44 differ, max 1.16e-10 | n/a | n/a | n/a | n/a |

## full

| Variant | Reference | plain-1 | nesterov-1 | nesterov-2 | velocity-1 | velocity-2 |
|---|---|---|---|---|---|---|
| baseline | none | `d861eea2623f` | `819194c056f4` | `e1e84ce79f32` | `17bb6a02d142` | `5a84a3874985` |
| baseline-repeat | baseline | equal | equal | equal | equal | equal |
| cpu-1-thread | baseline | equal | equal | equal | equal | equal |
| cpu-reversed | baseline | equal | equal | equal | equal | equal |
| cpu-shuffled | baseline | equal | equal | equal | equal | equal |
| in-memory | baseline | equal | equal | equal | equal | equal |
| velocity-float32 | baseline | equal | equal | 132,276 differ, max 4.66e-10 | equal | 557,468 differ, max 1.05e-10 |
| delta-rebuild-cpu | baseline | equal | equal | equal | equal | equal |
| delta-direct-cpu | baseline | 499,977 differ, max 4.66e-10 | n/a | n/a | n/a | n/a |
| cuda | baseline | equal | equal | equal | equal | equal |
| cuda-repeat | baseline | equal | equal | equal | equal | equal |
| cuda-shuffled | baseline | equal | equal | equal | equal | equal |
| cuda-true-division | baseline | equal | equal | equal | equal | equal |
| cuda-shuffled-true-division | baseline | equal | equal | equal | equal | equal |
| delta-rebuild-cuda | delta-rebuild-cpu | equal | equal | equal | equal | equal |
| delta-direct-cuda | delta-direct-cpu | equal | n/a | n/a | n/a | n/a |

## Merge time on the CPU

Measured separately after the main run, on the same machine: merge() alone, inputs read from safetensors files that were just written (so in the operating system's cache), 3 repeats, seconds.

| Kind | Plain | Nesterov |
|---|---|---|
| full (5 workers) | 0.70, 0.68, 0.71 | 0.89, 0.97, 1.11 |
| sliced (4 workers) | 0.32, 0.32, 0.33 | 0.50, 0.51, 0.50 |

The per-variant times in the run log (11 to 119 s) also include file writing, hashing and comparisons.
