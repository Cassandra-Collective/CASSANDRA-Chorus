# 2026-10-25 · Canonical part and model hashes in the package

| | |
|---|---|
| PLAN step | none; Phase 3, issue #62, architecture section 7.2 |
| Branch | `feat/62-canonical-hashes`, from `origin/main` at `e05b024` |
| SRS requirements | S0-N-05 (coordinator independence); D11 (expert router rows), D44 (working architecture) |
| Status | Planned; CPU-only baseline passed on 2026-10-25 |

## Problem / Motivation

Every peer computes its own merge and compares hashes to agree on the model.
The tensor hash is currently a prototype helper, so package code cannot reuse
it without importing scripts. Architecture section 7.2 also requires hashes
for each part and a model hash over those hashes. A slice holder must be able
to check its complete parts without loading experts it does not hold.

Issue [#62](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/62)
moves the existing definition without changing any bytes and adds those two
levels of identity. This change does not settle the owner's protocol choices.

## What Changed

| File | Description |
|---|---|
| `cassandra_chorus/coordinator/hashing.py` | Own the tensor byte and hash definitions, split complete parts, hash each part, and combine part hashes. |
| `cassandra_chorus/coordinator/__init__.py` | Export the five public functions; keep `__all__` sorted. |
| `scripts/proto/common.py` | Re-export `tensor_bytes` and `canonical_hash` from the package; preserve the remaining helpers. |
| `tests/test_hashing.py` | Pin the pre-move digests and check tensor identity, locality, partial states, model encoding, and a skipped GPU device copy. |
| `docs/implementations/2026-10-25-canonical-hashes.md` | Record the contracts, proposed protocol encoding, and verification. |

## Implementation Approach

### Tensor identity

Move the existing `tensor_bytes` and `canonical_hash` implementations and
their private dtype helpers to the coordinator package. The prototype imports
the public functions back from the package, so its existing imports and tests
continue to work. The prototype's integer-view table stays for `bit_diff`.
There is no package import from scripts or the simulation, and no dependency
is added. Neither `merge.py` nor `tests/test_coordinator.py` is edited.

### Parts and completeness

The proposed part IDs are `shared` and `L<layer>.E<expert>`. Indices are
nonnegative integers in decimal with no leading zeros. All ordering uses
Python string order by Unicode code points, including `L0.E10` before
`L0.E2`. Classification reuses `expert_param_owner` and `router_param_layer`.

The shared part contains every parameter that is neither an expert parameter
nor a router weight. Expert `(l, e)` contains every parameter under
`blocks.<l>.moe.experts.<e>.`, plus row `e` of
`blocks.<l>.moe.router.weight`. The row enters as a one-dimensional tensor
of shape `[d_model]`, named `blocks.<l>.moe.router.weight[<e>]`.
The full router never enters the shared part.

Both splitting and per-part hashing require `parameter_names`, the complete
parameter-name inventory from a full model or trusted manifest. Iterating
this inventory reads no tensor values. The inventory must not be inferred
from the supplied partial state: missing tensors cannot otherwise be detected
reliably. It must contain the router for each expert layer and the expert
parameter names for every router row, with contiguous indices from zero.

A part whose parameter names are wholly absent is omitted. Any present
expert parameter declares that expert present; all of its expected parameters
and its router must then be available or `ValueError` is raised. A whole
router in a slice does not declare its unheld experts present. Its unused
rows are ignored. A shared part with some but not all expected tensors also
raises `ValueError`; an empty shared inventory produces an empty shared part.
Unknown state names, an inconsistent inventory, and a router with a shape
other than `[n_experts, d_model]` (positive width) raise `ValueError`.
Other tensor shapes and dtypes enter the hash as supplied; this API is not
the update validator.

### Public function contracts

- `tensor_bytes(t: torch.Tensor) -> bytes`: return detached, CPU-read,
  C-contiguous little-endian data bytes. Floating dtypes use integer views of
  their bits, including bfloat16. The input is not changed. Copies and device
  transfers may occur; the supported dtypes stay those of the prototype.
- `canonical_hash(state: Mapping[str, torch.Tensor]) -> str`: read tensors
  once each in ascending name order and return 64 lowercase hexadecimal
  SHA-256 characters. Names, dtypes, shapes, lengths, and raw bits all enter
  the hash. The mapping may generate tensors on access. No inputs are changed
  and no random state is consumed. The prototype byte definition is invariant.
- `split_state(state: Mapping[str, torch.Tensor], parameter_names:
  Iterable[str]) -> dict[str, dict[str, torch.Tensor]]`: validate against the
  authoritative full inventory, then return all complete present parts in
  ascending part-ID order, using the proposed names above. Tensor values are
  references to inputs, and router rows are views, not copies. It reads the
  state but does not mutate it. Callers must keep inputs stable and must not
  mutate the returned tensors while hashing. Invalid or incomplete parts
  raise `ValueError` as described above.
- `part_hashes(state: Mapping[str, torch.Tensor], parameter_names:
  Iterable[str]) -> dict[str, str]`: split and hash each returned part with
  `canonical_hash`; return part IDs mapped to lowercase hex digests in
  ascending ID order. It has the same validation and side effects as
  splitting, plus CPU copies needed for hashing. It never hashes a partial
  expert or a router row without its expert parameters.
- `model_hash(hashes: Mapping[str, str]) -> str`: return SHA-256 over the
  sorted supplied `(part ID, part hash)` pairs. For each pair, append the ID
  as UTF-8, `0x00`, the digest as 64 lowercase hex ASCII characters, `0x00`.
  Empty or NUL-containing IDs and malformed digests raise `ValueError`.
  Inputs are not changed. The caller supplies the complete part inventory
  when claiming a full model hash; this function cannot infer omitted parts.
  An empty mapping hashes the empty byte string.

## Mathematical / Statistical Details

Let `||` denote byte concatenation, `Z` one zero byte, `UTF8` UTF-8 encoding,
`ASCII` ASCII encoding, and `LE64(n)` the unsigned 8-byte little-endian
encoding of `n`. For a tensor `t`, let `B(t)` be its C-contiguous little-endian
data bytes, using integer views of floating bits. Let `dtype(t)` be the dtype
name without `torch.`, and `shape(t)` comma-join the decimal dimensions (the
empty string for a scalar).

For each name `n`, define
`T(n, t) = UTF8(n) || Z || ASCII(dtype(t)) || Z || ASCII(shape(t)) || Z || LE64(len(B(t))) || B(t)`.
Then `C(S) = hex(SHA256(concat(T(n, S[n]) for n in sorted(S))))`.

For part `p`, `H[p] = C(S_p)` with `S_p` defined above. The proposed model
definition is
`M(H) = hex(SHA256(concat(UTF8(p) || Z || ASCII(H[p]) || Z for p in sorted(H))))`.
No numerical tolerance, arithmetic on tensor values, or statistical estimate
enters these hashes. SHA-256 collisions remain theoretically possible.

## Design Decisions

- **Open for the owner: part IDs and ordering.** Propose `shared` and
  `L<layer>.E<expert>`, sorted by Python string order by code points. This
  makes the global indices explicit without a second numeric ordering rule.
- **Open for the owner: router row name and shape.** Propose the original
  router parameter name followed by `[<expert>]`, with shape `[d_model]`.
  This retains its origin and cannot be confused with the full matrix.
- **Open for the owner: model hash byte encoding.** Propose UTF-8 ID, NUL,
  lowercase hex ASCII digest, NUL per pair. Reject invalid delimiters and
  digests to keep the encoding unambiguous. Binary digests are an alternative.
- **Open for the owner: partial-state rule.** Hash complete present parts,
  omit wholly absent parts, and reject incomplete present parts. Require a
  trusted full name inventory rather than guessing expected names from a
  slice or hard-coding today's expert implementation. Ignore unheld rows in
  a slice's full router. A permissive subset hash could hide a missing tensor.

These are engineering proposals for draft review, not new SRS decisions.
The owner should add the agreed choices to architecture section 7.2. Until
then, the plan and draft PR explicitly carry the unsettled choices.

## Verification

Before changing any tracked file, `python -m pytest` at `e05b024` completed
with **310 passed, 12 skipped, 0 failed**, and 2 expected warning-capture
warnings, in 167.94 seconds. The initial invocation on the issue #60 checkout
was interrupted before GPU tests after discovering CUDA was visible; it was
not used as the baseline. All authoritative checks run in the isolated issue
#62 checkout, outside OneDrive, with this process-local environment:

```powershell
$env:CUDA_VISIBLE_DEVICES = '-1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
python -m pytest
```

Environment: Windows 11 x64 (build 26300), Intel64 family 6 model 183 CPU,
Python 3.13.14, PyTorch 2.12.1+cu126, pytest 9.0.2. Verification is CPU only,
with one torch thread. This host has CUDA, unlike the objective's assumed
cloud container, so CUDA is explicitly hidden. No GPU test is run.

Before the move, the original `scripts.proto.common.canonical_hash` gave
these literal digests for the following retained reconstruction script:

1. `e082cbae4f221a95d74bcfc55a915e8f874a2cd03ffb8cd01379d909055e1c94`
2. `fc61228b9a6472cd64e433355a1a8763ef0d1479312369577861a8e374d01ec0`
3. `3339744837d70f472657890d07ca30bdccc6a92d511c174148e1534d18fc1aa0`

```python
import torch
from scripts.proto.common import canonical_hash

def golden_states():
    g = torch.Generator().manual_seed(62)
    return [
        {
            "b.weight": torch.randn(2, 3, generator=g, dtype=torch.float32),
            "a.bias": torch.randn(3, generator=g, dtype=torch.float64),
        },
        {
            "expert.weight": torch.randn(2, 4, generator=g, dtype=torch.bfloat16),
            "tokens": torch.randint(-100, 100, (3,), generator=g, dtype=torch.int64),
        },
        {
            "scalar": torch.randn((), generator=g, dtype=torch.float64),
            "signed_zero": torch.tensor([-0.0], dtype=torch.float32),
            "offset": torch.randint(-10, 10, (), generator=g, dtype=torch.int64),
        },
    ]

for state in golden_states():
    print(canonical_hash(state))
```

The tests will retain the same `golden_states` constructor and literals.
Part tests will use the real model's names on a 5,680-parameter transformer:
2 layers, 4 experts per layer, width 16, expert hidden width 8, vocabulary 11,
context 8, 2 heads. Seed 0 builds that fixture; seed 62 builds the three
golden states. No training or dataset is involved in the new hash tests.

Planned checks: golden compatibility; reordered and lazy inputs; bit, dtype,
shape, name, and signed-zero sensitivity; exact part membership; locality of
expert, router-row, and shared changes; sorted model encoding; slice equality;
incomplete parts; invalid inputs; no input mutation; prototype import identity;
and the unchanged prototype and layering tests. Final counts will be filled
in after implementation. Check whitespace and forbidden dash characters in
every touched file before the second commit.

**Not tested:** GPU device-copy equality (the marked test is skipped),
cross-machine equality (#75), posting hashes in the round log (#64), and
the bitwise-or-tolerance decision AD-8 (#39). This is local hash verification,
not a training or performance experiment; no `RESULTS.md` entry is needed.

## Related Docs

- [Architecture sections 7.1 and 7.2](../ARCHITECTURE.md#7-the-merge-rule).
- [SRS](../SRS.md), S0-N-05 and decisions D11, D44.
- [Contribution rules](../../CONTRIBUTING.md), sections 3, 5, 7, 8.
- [Coordinator implementation](2026-10-08-coordinator.md).
- [Prototype implementation](2026-10-14-solo-prototypes.md).
- [Issue #62](https://github.com/Cassandra-Collective/CASSANDRA-Chorus/issues/62).
