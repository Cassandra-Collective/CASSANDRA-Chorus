"""Shared helpers for the prototypes (docs/implementations/2026-10-14-solo-prototypes.md).

* :func:`canonical_hash`: the model identity a peer would post in the round
  log, defined over tensors rather than file bytes;
* :class:`LazyState`: a read-only name-to-tensor mapping that produces each
  tensor on access, so a 46M-parameter merge can stream from files or seeds
  without holding every worker's state in memory;
* :func:`bit_diff`: how two states differ, bit for bit;
* the Hub token guard (:func:`scope_problems`, :func:`guarded_token`).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = REPO_ROOT / "results" / "prototypes"

_INT_VIEW = {torch.float32: torch.int32, torch.float64: torch.int64, torch.float16: torch.int16,
             torch.bfloat16: torch.int16}


def _dtype_name(dtype: torch.dtype) -> str:
    return str(dtype).removeprefix("torch.")


def tensor_bytes(t: torch.Tensor) -> bytes:
    """The tensor's data as C-contiguous little-endian bytes, read on the CPU."""
    t = t.detach().to("cpu").contiguous()
    view = _INT_VIEW.get(t.dtype)
    if view is not None:
        t = t.view(view)  # numpy has no bfloat16; the bit pattern is what is hashed
    arr = t.numpy()
    if arr.dtype.byteorder == ">":
        arr = arr.byteswap().view(arr.dtype.newbyteorder("<"))
    return arr.tobytes(order="C")


def canonical_hash(state: Mapping[str, torch.Tensor]) -> str:
    """SHA-256 (hexadecimal) of the state's names, dtypes, shapes and bit patterns.

    Tensors in ascending name order; for each: name (UTF-8), 0x00, dtype name,
    0x00, shape as comma-joined integers, 0x00, data length as an 8-byte
    little-endian integer, then the data. Equal hashes mean equal names,
    dtypes, shapes and bits; file serialization does not enter.
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


class LazyState(Mapping[str, torch.Tensor]):
    """A fixed set of names whose tensors come from ``fetch(name)`` on every access.

    Nothing is cached, so memory holds at most the tensors the caller keeps.
    Iteration order is the order of ``names``.
    """

    def __init__(self, names: Iterable[str], fetch: Callable[[str], torch.Tensor]) -> None:
        self._names = list(names)
        self._set = set(self._names)
        self._fetch = fetch

    def __getitem__(self, name: str) -> torch.Tensor:
        if name not in self._set:
            raise KeyError(name)
        return self._fetch(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self._names)

    def __len__(self) -> int:
        return len(self._names)


def bit_diff(a: Mapping[str, torch.Tensor], b: Mapping[str, torch.Tensor]) -> dict[str, Any]:
    """How ``b`` differs from ``a``: per tensor and overall.

    Elements are compared by bit pattern. For differing tensors: the count of
    differing elements, max |a - b| and max |a - b| / max(|a|, 1e-30).
    Raises ``ValueError`` if names, dtypes or shapes differ.
    """
    if set(a) != set(b):
        raise ValueError(f"name sets differ: {sorted(set(a) ^ set(b))[:5]}")
    per_tensor: dict[str, dict[str, Any]] = {}
    elements = 0
    for name in sorted(a):
        x, y = a[name].detach().to("cpu"), b[name].detach().to("cpu")
        if x.dtype != y.dtype or x.shape != y.shape:
            raise ValueError(f"{name}: {x.dtype}{tuple(x.shape)} against {y.dtype}{tuple(y.shape)}")
        view = _INT_VIEW.get(x.dtype)
        differ = (x.view(view) != y.view(view)) if view is not None else (x != y)
        count = int(differ.sum())
        elements += x.numel()
        if count:
            dx, dy = x.double(), y.double()
            absd = (dx - dy).abs()
            rel = absd / dx.abs().clamp_min(1e-30)
            per_tensor[name] = {"elements_differing": count, "max_abs": float(absd.max()),
                                "max_rel": float(rel.max())}
    return {
        "bitwise_equal": not per_tensor,
        "tensors_differing": len(per_tensor),
        "elements_differing": sum(d["elements_differing"] for d in per_tensor.values()),
        "elements_total": elements,
        "max_abs": max((d["max_abs"] for d in per_tensor.values()), default=0.0),
        "max_rel": max((d["max_rel"] for d in per_tensor.values()), default=0.0),
        "worst_tensors": dict(sorted(per_tensor.items(), key=lambda kv: -kv[1]["max_abs"])[:5]),
    }


def write_json(path: Path, payload: Any) -> None:
    """Write ``payload`` as indented UTF-8 JSON, creating the folder."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Hub token guard (P0, P3, P4, P5)

PROTO_TOKEN_NAME = "chorus-prototypes"
PROTO_PREFIX = "proto-"


def scope_problems(token_info: Mapping[str, Any], org: str) -> list[str]:
    """Reasons a token must not be used for the prototypes; empty if it may.

    ``token_info`` is a ``whoami`` response. Refused: a non-fine-grained token;
    any permission containing "write" on a ``user`` entity or among the global
    permissions; a token not scoped to ``org``.
    """
    access = (token_info.get("auth") or {}).get("accessToken") or {}
    if access.get("role") != "fineGrained":
        return [f"token role is {access.get('role')!r}, not 'fineGrained'"]
    fine = access.get("fineGrained") or {}
    problems = []
    orgs_scoped = set()
    for scoped in fine.get("scoped", []):
        entity = scoped.get("entity") or {}
        perms = scoped.get("permissions") or []
        if entity.get("type") == "user" and any("write" in p for p in perms):
            problems.append(f"token can write as user {entity.get('name')!r}: {sorted(perms)}")
        if entity.get("type") == "org":
            orgs_scoped.add(entity.get("name"))
    global_writes = [p for p in fine.get("global") or [] if "write" in p]
    if global_writes:
        problems.append(f"token has global write permissions: {global_writes}")
    if org not in orgs_scoped:
        problems.append(f"token is not scoped to organisation {org!r} (scoped: {sorted(orgs_scoped)})")
    return problems


def load_named_token(name: str = PROTO_TOKEN_NAME) -> str:
    """The stored Hub token called ``name``. Never print or log the result.

    Uses ``huggingface_hub._login.get_stored_tokens``, a private function of
    version 1.24.0: acceptable for prototypes, not for the client.
    """
    from huggingface_hub._login import get_stored_tokens

    token = get_stored_tokens().get(name)
    if not token:
        raise SystemExit(f"no stored Hub token named {name!r}; log in with it first (see the plan doc)")
    return token


def hub_manifest_path() -> Path:
    """The local record of every Hub resource the prototypes create (outside version control)."""
    from cassandra_chorus.paths import runs_root

    return runs_root() / "proto-hub-manifest.json"


def record_hub_resource(kind: str, resource_id: str, prototype: str) -> None:
    """Append a resource to the manifest. Called *before* creating it, so a crash cannot orphan it.

    Raises ``ValueError`` for a name outside the ``proto-`` prefix: the clean-up
    deletes only what this manifest lists, and only ``proto-`` names.
    """
    if kind not in ("repo", "bucket"):
        raise ValueError(f"unknown resource kind {kind!r}")
    if not resource_id.partition("/")[2].startswith(PROTO_PREFIX):
        raise ValueError(f"prototype resources must be named {PROTO_PREFIX}*, got {resource_id!r}")
    path = hub_manifest_path()
    entries = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    if not any(e["kind"] == kind and e["id"] == resource_id for e in entries):
        entries.append({"kind": kind, "id": resource_id, "prototype": prototype})
        write_json(path, entries)


def guarded_token(org: str, name: str = PROTO_TOKEN_NAME) -> str:
    """Load the token ``name`` and check its scope with ``whoami``; exit if it is too broad."""
    from huggingface_hub import whoami

    token = load_named_token(name)
    problems = scope_problems(whoami(token=token), org)
    if problems:
        raise SystemExit("refusing to use token " + repr(name) + ":\n  " + "\n  ".join(problems))
    return token
