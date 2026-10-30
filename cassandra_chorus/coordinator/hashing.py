"""Canonical tensor, part, and model identity (architecture section 7.2).

Part IDs are ``shared`` and ``L<layer>.E<expert>`` with decimal global indices.
An expert part includes its router row as ``blocks.<l>.moe.router.weight[<e>]``.
Part IDs and tensor names use Python string order by code points. Protocol
choices and contracts: ``docs/implementations/2026-10-25-canonical-hashes.md``.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping

import torch

from cassandra_chorus.model import expert_param_owner, router_param_layer

_INT_VIEW = {torch.float32: torch.int32, torch.float64: torch.int64, torch.float16: torch.int16,
             torch.bfloat16: torch.int16}


def _dtype_name(dtype: torch.dtype) -> str:
    return str(dtype).removeprefix("torch.")


def tensor_bytes(t: torch.Tensor) -> bytes:
    """Return C-contiguous little-endian data bytes, read on the CPU.

    Detaches and may copy or transfer the tensor; the input is not modified.
    Floating dtypes are read through integer views to preserve their bits.
    """
    t = t.detach().to("cpu").contiguous()
    view = _INT_VIEW.get(t.dtype)
    if view is not None:
        t = t.view(view)  # numpy has no bfloat16; the bit pattern is what is hashed
    arr = t.numpy()
    if arr.dtype.byteorder == ">":
        arr = arr.byteswap().view(arr.dtype.newbyteorder("<"))
    return arr.tobytes(order="C")


def canonical_hash(state: Mapping[str, torch.Tensor]) -> str:
    """Return the state's SHA-256 hex digest, reading each tensor once.

    Tensors in ascending name order; for each: name (UTF-8), 0x00, dtype name,
    0x00, shape as comma-joined integers, 0x00, data length as an 8-byte
    little-endian integer, then the C-contiguous little-endian data.
    Dtypes and floating bit patterns follow the prototype definition.
    Lazy mappings are supported. No inputs or random state are modified;
    tensor reads may copy or transfer data to the CPU.
    """
    h = hashlib.sha256()
    for name in sorted(state):
        t = state[name]
        data = tensor_bytes(t)
        h.update(name.encode("utf-8") + b"\x00")
        h.update(_dtype_name(t.dtype).encode("ascii") + b"\x00")
        h.update(",".join(str(d) for d in t.shape).encode("ascii") + b"\x00")
        h.update(len(data).to_bytes(8, "little"))
        h.update(data)
    return h.hexdigest()


def split_state(
    state: Mapping[str, torch.Tensor], parameter_names: Iterable[str]
) -> dict[str, dict[str, torch.Tensor]]:
    """Return complete present parts, sorted by ID, without changing inputs.

    ``parameter_names`` is the authoritative full model's name inventory,
    never the partial state's names. Every expert layer must have a router
    and contiguous expert indices from zero. Unknown state names, incomplete
    present parts, inconsistent inventories, or invalid router shapes raise
    ``ValueError``. Wholly absent parts and unheld router rows are omitted.
    A router alone does not declare an expert present. Empty shared parts
    are retained. Output tensors alias inputs; router rows are 1-D views.
    Reads may materialize tensors from a lazy mapping; no values are changed.
    """
    expected = set(parameter_names)
    present = set(state)
    if extra := present - expected:
        raise ValueError(f"unexpected parameter names: {sorted(extra)}")

    names_by_part: dict[str, set[str]] = {"shared": set()}
    experts: dict[tuple[int, int], str] = {}
    routers: dict[int, str] = {}
    for name in expected:
        owner = expert_param_owner(name)
        layer = router_param_layer(name)
        if owner is not None:
            part_id = f"L{owner[0]}.E{owner[1]}"
            experts[owner] = part_id
            names_by_part.setdefault(part_id, set()).add(name)
        elif layer is not None:
            if layer in routers:
                raise ValueError(f"multiple router names for layer {layer}")
            routers[layer] = name
        else:
            names_by_part["shared"].add(name)

    if set(routers) != {layer for layer, _ in experts}:
        raise ValueError("parameter inventory must pair expert layers with routers")
    router_tensors = {}
    for layer, name in routers.items():
        indices = {expert for expert_layer, expert in experts if expert_layer == layer}
        if indices != set(range(len(indices))):
            raise ValueError(f"layer {layer}: expert inventory must be contiguous from zero")
        if name in present:
            router = state[name]
            if router.ndim != 2 or router.shape[0] != len(indices) or router.shape[1] < 1:
                raise ValueError(f"{name}: expected router shape [{len(indices)}, d_model] with positive width")
            router_tensors[layer] = router

    parts = {}
    for part_id, names in names_by_part.items():
        found = names & present
        if not found and names:
            continue
        if missing := names - present:
            raise ValueError(f"incomplete part {part_id}: missing {sorted(missing)}")
        parts[part_id] = {name: state[name] for name in sorted(names)}

    for (layer, expert), part_id in experts.items():
        if part_id not in parts:
            continue
        if layer not in router_tensors:
            raise ValueError(f"incomplete part {part_id}: missing {routers[layer]}")
        parts[part_id][f"{routers[layer]}[{expert}]"] = router_tensors[layer][expert]
    return {part_id: parts[part_id] for part_id in sorted(parts)}


def part_hashes(state: Mapping[str, torch.Tensor], parameter_names: Iterable[str]) -> dict[str, str]:
    """Return complete present part IDs mapped to canonical hex digests.

    Inputs and validation follow ``split_state``: a trusted full name inventory
    is required and incomplete present parts raise ``ValueError``. Inputs are
    not changed; hashing may copy tensors to the CPU. Keys use string order.
    """
    return {part_id: canonical_hash(part) for part_id, part in split_state(state, parameter_names).items()}


def model_hash(hashes: Mapping[str, str]) -> str:
    """Return SHA-256 of sorted supplied (part ID, hex digest) pairs.

    Each pair encodes as UTF-8 ID, NUL, 64 lowercase hex ASCII characters,
    NUL. Empty or NUL-containing IDs and invalid digests raise ``ValueError``.
    No inputs are changed. The caller supplies all parts for a full model
    hash; completeness cannot be inferred here. Empty input hashes no bytes.
    """
    h = hashlib.sha256()
    for part_id in sorted(hashes):
        digest = hashes[part_id]
        if not part_id or "\x00" in part_id:
            raise ValueError("part IDs must be nonempty and contain no NUL")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"{part_id}: part hash must be 64 lowercase hex characters")
        h.update(part_id.encode("utf-8") + b"\x00")
        h.update(digest.encode("ascii") + b"\x00")
    return h.hexdigest()
