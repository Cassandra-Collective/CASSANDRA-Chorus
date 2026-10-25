# 2026-10-25 · True division in the merge on every device (#60)

| | |
|---|---|
| PLAN step | None; Phase 3, issue #60, preserving the Stage 0 merge |
| Branch | `fix/60-gpu-merge-true-division`, based on `main` at `e05b024` |
| SRS requirements | S0-F-08 to S0-F-10, S0-N-05, S0-N-06; D11; architecture section 7.1 steps 4 and 5 |
| Status | Verified on the CPU and an RTX 4070 Laptop CUDA GPU, 2026-10-25; plan committed before code as `6627057` |

## Problem / Motivation

`_weighted_mean` ends with `acc / total`, where `total` is a Python number. On CUDA, PyTorch implements this division by multiplying by a rounded reciprocal. That can change the last bit compared with IEEE division on the CPU.

P6 used a 46,050,432-parameter model on one RTX 4070 Laptop GPU. Its sliced plain merge differed from the CPU in 472 elements; a second Nesterov round differed in 526 elements, with a largest difference of 5.96e-08. The device-tensor division matched the CPU in both member and shuffled order. These are the recorded P6 findings, not new measurements in this change.

Architecture section 7.2 requires peers to compare hashes of the merged tensor bytes. A small numerical error still changes a hash. The fix must therefore preserve every CPU result bit and request float64 IEEE division on every device. P6 also found that float32 velocity storage changed round 2's sliced model in 204,432 elements, so the existing float64 velocity is part of the storage and publication contract.

## What Changed

| File | Description |
|---|---|
| `docs/implementations/2026-10-25-gpu-merge-true-division.md` | Record the plan, contracts, decisions, checks and limits of this fix. |
| `cassandra_chorus/coordinator/merge.py` | Change only the final weighted-mean division and document the float64 Nesterov velocity storage and publication contract. |
| `tests/test_coordinator.py` | Pin CPU compatibility, guard velocity dtype, strengthen the existing CUDA comparison and add a seeded random CUDA regression. |

## Implementation Approach

`_weighted_mean(tensors, weights)` receives a nonempty list of same-shaped tensors on one device and a matching list of positive example weights supplied by `merge`. It returns their weighted mean as a float64 tensor on the first tensor's device, without changing the inputs. It accumulates in float64 in the given order. The final operation must be IEEE float64 division on every device:

```python
return acc / torch.tensor(total, dtype=torch.float64, device=acc.device)
```

Keep the accumulation, weights, order and casts exactly as they are. Add a short comment explaining why the divisor is a device tensor. `merge` keeps its existing public interface, contributor rules and cast back to each parameter's dtype.

`NesterovOuter` receives current and averaged parameters plus an optional contributor mask. A step returns parameters in the current dtype and updates its per-parameter velocity only for contributing entries. Velocity tensors are float64 and must stay float64 when stored or published. Only its docstring changes: the existing `.double()` delta and checkpoint `.cpu()` storage already preserve this dtype.

Tests use a CPU `torch.Generator` seeded with 60 to construct float32 model and worker states with 164,800 global elements. The model has two layers, four experts, width 64, expert width 64 and vocabulary size 257. The three example counts are 11, 17 and 21, whose sum is 49. Reuse the existing slice and worker-state helpers, and keep unheld router rows at their global values. Cover sliced and full workers, `holders` and `all`, and both `PlainAverage` and `NesterovOuter`.

The unmarked CPU compatibility test runs the real `merge` twice on the same inputs with separate outer optimizers. For the reference only, monkeypatch the merge module's `_weighted_mean` to its exact pre-fix body ending in `acc / total`. Restore the function before running the fixed merge and require `torch.equal` for every output tensor. Do not reimplement the merge. A separate CPU test requires every velocity tensor after a float32-parameter step to be float64.

The existing GPU comparison changes from `allclose` to `torch.equal`. The new random comparison also uses `torch.equal`, is marked `gpu`, and has the same CUDA availability skip condition. Copy the CPU inputs to CUDA so both devices receive identical bits. On the available GPU, also temporarily revert only the final division and require the new regression to fail, then restore the fix before further checks or commits.

## Mathematical / Statistical Details

For contributors i with example count n_i and parameters W_i, the average is

```text
A = (sum_i n_i W_i) / (sum_i n_i).
```

The sum is accumulated in float64 over the supplied contributor order. With s = sum_i n_i, IEEE division rounds x / s once. Multiplication by a reciprocal first rounds 1 / s and then rounds x times that rounded value. Those two roundings can produce a different last bit from the single division rounding. Casting to float32 can preserve that difference when the values fall on opposite sides of a rounding boundary.

The Nesterov formulas stay unchanged: delta = average - current; v = momentum * v + delta; new = current + lr * (delta + momentum * v). The existing float64 velocity must survive between rounds without a float32 storage cast.

## Design Decisions

| Decision | Reason and authority |
|---|---|
| Use the prototype's exact divisor form | Required by issue #60 and the objective; it is the form tested in `scripts/proto/p6_merge_determinism.py`. |
| Put the divisor on `acc.device` | A zero-dimensional CPU tensor next to a CUDA tensor can be treated as a scalar and select the reciprocal path again. |
| Keep the merge on the caller's device | Moving it to the CPU is a separate architecture proposal in section 7.1 step 7, outside this bug fix. |
| Preserve all other arithmetic and interfaces | The CPU merge is the reference; changing ordering, dtype or casts would weaken the compatibility claim. |
| Document and guard velocity without changing storage | Current Nesterov computation and checkpoint storage already retain float64; section 7.1 step 5 supplies the rule. |
| Use example counts 11, 17 and 21 | During regression validation, the initial counts 3, 5 and 7 did not expose the old division on this GPU. The total 49 also is not a power of two and was chosen to expose reciprocal rounding in float32 output. The negative check below confirms that the final fixture detects the bug. |
| Use the actual available GPU for verification | The objective describes a CPU-only container, but this checkout is on Windows with CUDA available; record observed runs instead of claiming GPU tests were skipped. This is an engineering default for review. |
| Keep scope to the three files listed above | No dependencies, protocol decisions, prototype changes or cross-machine determinism work are needed. |

**Open for the owner:** None. No new architecture decision was needed.

## Verification

Baseline: `python -m pytest` on the untouched checkout at `f24df06`: **322 passed, 0 skipped, 0 failed**, 2 expected warning-capture warnings, in 320.56 s. The baseline checkout was `process/approvals-and-backlog`. The fix branch starts at current `origin/main`, `e05b024`; `git diff --name-only f24df06 e05b024 -- '*.py' pyproject.toml` is empty, so all baseline Python code and test configuration match the branch base.

Environment observed before changes: Windows 11 (`Windows-11-10.0.26300-SP0`), NVIDIA GeForce RTX 4070 Laptop GPU, Python 3.13.14 (MSC v.1944 64 bit), PyTorch 2.12.1+cu126, CUDA available. Version command: `python -c "import sys, torch; print(sys.version, torch.__version__)"`. Baseline tests use their existing synthetic fixtures and seeds; no training dataset or full-scale prototype run was added.

Observed checks on the hardware above, using the final 164,800-parameter fixture, one generator seed (60), synthetic float32 inputs and no training dataset:

| Command or check | Observed result |
|---|---|
| `python -m pytest tests/test_coordinator.py -k cpu_merge_is_unchanged` | 8 passed, 40 deselected, 0 skipped, 0 failed, in 1.73 s; exact old/new CPU equality for both outer optimizers, router rules and slice modes. |
| `python -m pytest -m gpu tests/test_coordinator.py -k random --tb=short`, with only the final division temporarily reverted | 8 failed, 40 deselected, 0 skipped, in 3.94 s (expected exit code 1); every new case detected CPU/CUDA inequality in `embed.weight`. |
| `python -m pytest -m gpu tests/test_coordinator.py`, after restoring the fix | 10 passed, 38 deselected, 0 skipped, 0 failed, in 1.72 s; both existing and new comparisons require `torch.equal`. |
| `python -m pytest`, after restoring the fix | **339 passed, 0 skipped, 0 failed**, 2 expected warning-capture warnings, in 387.37 s; includes the velocity dtype guard and layering checks. |
| `git diff --check` | No output; no whitespace errors. |

An earlier `python -m pytest tests/test_coordinator.py` run passed all 48 cases in 5.78 s with the initial counts 3, 5 and 7. However, the new GPU cases also passed with the old division, so that candidate fixture was rejected. All final checks in the table use counts 11, 17 and 21 (total 49). The negative check changed only the final division; the device-tensor fix was restored before the positive GPU check and final suite.

Prohibited-dash check, equivalent to the requested `grep -nP` check:

```text
rg -nP '[\x{2013}\x{2014}]' cassandra_chorus/coordinator/merge.py tests/test_coordinator.py docs/implementations/2026-10-25-gpu-merge-true-division.md
```

It printed nothing (exit code 1 for no matches). The diff contains only the three files listed above.

The objective described a CPU-only container, but GPU tests were run here because CUDA is available. They show exact CPU/CUDA equality for these test inputs on this machine and PyTorch build. Before merging, the owner must confirm both CUDA acceptance checks on the target machine: (i) `python -m pytest -m gpu tests/test_coordinator.py` passes; (ii) with only the final division temporarily reverted, `python -m pytest -m gpu tests/test_coordinator.py -k random` fails. Both checks were observed here.

**Not tested:** The 46,050,432-parameter P6 prototype was not rerun. Performance, network publication and cross-machine or cross-build determinism (#75) were not tested. `scripts/proto/` and `results/` remain unchanged.

## Related Docs

- [Issue #60](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/60).
- [CONTRIBUTING.md](../../CONTRIBUTING.md), sections 3, 5, 7 and 8.
- [Architecture](../ARCHITECTURE.md), section 7.1 steps 4, 5 and 7, and section 7.2.
- [Coordinator implementation](2026-10-08-coordinator.md), weighted means and Nesterov formulas.
- [SRS](../SRS.md), S0-F-08 to S0-F-10, S0-N-05, S0-N-06 and D11.
- [PLAN](../PLAN.md), Stage 0 coordinator step 5.
- [P6 findings](../../results/prototypes/p6_merge_determinism.md) and [prototype divisor](../../scripts/proto/p6_merge_determinism.py).
- [RESULTS.md](../../RESULTS.md), existing prototype results; this fix adds regression tests rather than a new experiment.
