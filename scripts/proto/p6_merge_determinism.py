"""P6: merge determinism (docs/implementations/2026-10-14-solo-prototypes.md).

Computes the same merges under several variants and compares each result's
canonical hash with a reference. The baseline: CPU with default threads,
results in member order, full worker states read from safetensors files,
merged states written and read back, Nesterov velocity stored as float64.

Inputs are synthetic: the Stage 0 Task B model initialized with seed 7, and
worker results that add seeded Gaussian noise to the round's start state.
Two work-unit kinds (D34): ``sliced`` (4 workers, capacity 4, rolling: 2
holders per expert) and ``full`` (5 workers). Plain averaging for one round;
Nesterov over two rounds, so round 1's velocity enters round 2.

Every tensor is produced on access (from a file or from its seed), so the
46M-parameter merges never hold all workers' states in memory.

Usage:
    python scripts/proto/p6_merge_determinism.py [--work-dir DIR] [--keep-files] [--no-cuda]
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import importlib
import random
import shutil
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch
from safetensors import safe_open
from safetensors.torch import save_file

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cassandra_chorus.config import build_config, read_config_file  # noqa: E402
from cassandra_chorus.coordinator.assignment import Slice, WorkerSpec, assign_slices  # noqa: E402
from cassandra_chorus.coordinator.merge import NesterovOuter, PlainAverage, WorkerResult, merge  # noqa: E402
from cassandra_chorus.model import MoETransformer, expert_param_owner  # noqa: E402
from cassandra_chorus.model.transformer import ModelSection  # noqa: E402
from cassandra_chorus.paths import runs_root  # noqa: E402
from cassandra_chorus.repro import derive_seed, environment_info  # noqa: E402
from scripts.proto.common import RESULTS_DIR, LazyState, bit_diff, canonical_hash, write_json  # noqa: E402

SEED = 7
NOISE_STD = 1e-3
NESTEROV = {"lr": 0.7, "momentum": 0.9}
EXAMPLES = {"sliced": [4000, 4096, 3900, 4100], "full": [4000, 4096, 3900, 4100, 3987]}
STATE_LABELS = ("plain-1", "nesterov-1", "nesterov-2")
VELOCITY_LABELS = ("velocity-1", "velocity-2")


@dataclasses.dataclass(frozen=True)
class Variant:
    """One way of computing the same merges. ``reference`` names the variant it is compared with."""

    name: str
    device: str = "cpu"
    threads: int | None = None          # None: PyTorch's default
    order: str = "member"               # member | reversed | shuffled
    representation: str = "full"        # full | delta-rebuild | delta-direct
    velocity_dtype: str = "float64"     # how the velocity is stored between rounds
    files: bool = True                  # inputs from files, outputs written and read back
    true_division: bool = False         # divide by a tensor on the device (see _true_division)
    reference: str | None = "baseline"
    keep: bool = False                  # keep outputs on disk: another variant compares with them


def variants(use_cuda: bool) -> list[Variant]:
    out = [
        Variant("baseline", reference=None, keep=True),
        Variant("baseline-repeat"),
        Variant("cpu-1-thread", threads=1),
        Variant("cpu-reversed", order="reversed"),
        Variant("cpu-shuffled", order="shuffled"),
        Variant("in-memory", files=False),
        Variant("velocity-float32", velocity_dtype="float32"),
        Variant("delta-rebuild-cpu", representation="delta-rebuild", keep=True),
        Variant("delta-direct-cpu", representation="delta-direct", keep=True),
    ]
    if use_cuda:
        out += [
            Variant("cuda", device="cuda"),
            Variant("cuda-repeat", device="cuda"),
            Variant("cuda-shuffled", device="cuda", order="shuffled"),
            Variant("cuda-true-division", device="cuda", true_division=True),
            Variant("cuda-shuffled-true-division", device="cuda", order="shuffled", true_division=True),
            Variant("delta-rebuild-cuda", device="cuda", representation="delta-rebuild", reference="delta-rebuild-cpu"),
            Variant("delta-direct-cuda", device="cuda", representation="delta-direct", reference="delta-direct-cpu"),
        ]
    return out


# --------------------------------------------------------------------------
# Inputs


def task_b_model_config() -> ModelSection:
    return build_config(ModelSection, read_config_file(REPO / "configs" / "task_b" / "sliced.toml")["model"])


def initial_state(cfg: ModelSection) -> dict[str, torch.Tensor]:
    torch.manual_seed(SEED)
    return {k: v.detach().clone() for k, v in MoETransformer(cfg).state_dict().items()}


def round_slices(kind: str, cfg: ModelSection, round_index: int) -> list[Slice]:
    """The round's slices in member order (m0, m1, ...)."""
    if kind == "sliced":
        specs = [WorkerSpec(f"m{i}", 4) for i in range(len(EXAMPLES["sliced"]))]
        by_name = assign_slices(specs, cfg.n_layers, cfg.n_experts, cfg.top_k, round_index, policy="rolling", seed=SEED)
        return [by_name[n] for n in sorted(by_name)]
    everything = tuple(range(cfg.n_experts))
    return [Slice(f"m{i}", {layer: everything for layer in range(cfg.n_layers)}) for i in range(len(EXAMPLES["full"]))]


def held_names(names: Mapping[str, Any], slice_: Slice) -> list[str]:
    return [n for n in names if (o := expert_param_owner(n)) is None or slice_.holds(*o)]


def noise(kind: str, round_index: int, worker: str, name: str, shape: torch.Size) -> torch.Tensor:
    g = torch.Generator().manual_seed(derive_seed(SEED, f"p6/{kind}/round{round_index}/{worker}/{name}"))
    return torch.randn(shape, generator=g, dtype=torch.float32) * NOISE_STD


def input_path(work: Path, kind: str, round_index: int, worker: str, what: str) -> Path:
    return work / "inputs" / f"{kind}-r{round_index}-{worker}-{what}.safetensors"


def write_round_inputs(work: Path, kind: str, cfg: ModelSection, round_index: int, start: Mapping[str, torch.Tensor]) -> None:
    """Each worker's full state W = start + noise and delta D = start - W, as files."""
    for s in round_slices(kind, cfg, round_index):
        states, deltas = {}, {}
        for n in held_names(start, s):
            base = start[n]
            w = base + noise(kind, round_index, s.worker, n, base.shape)
            states[n], deltas[n] = w, base - w
        save_file(states, str(input_path(work, kind, round_index, s.worker, "state")))
        save_file(deltas, str(input_path(work, kind, round_index, s.worker, "delta")))


def file_state(stack: contextlib.ExitStack, path: Path, device: torch.device) -> LazyState:
    f = stack.enter_context(safe_open(str(path), framework="pt", device="cpu"))
    return LazyState(list(f.keys()), lambda n: f.get_tensor(n).to(device))


# --------------------------------------------------------------------------
# One variant


def ordered(results: list[WorkerResult], order: str) -> list[WorkerResult]:
    if order == "member":
        return results
    if order == "reversed":
        return results[::-1]
    shuffled = results[:]
    random.Random(derive_seed(SEED, "p6/shuffle")).shuffle(shuffled)
    if shuffled in (results, results[::-1]):  # make sure "shuffled" is neither of the other orders
        shuffled = shuffled[1:] + shuffled[:1]
    return shuffled


def build_results(v: Variant, kind: str, cfg: ModelSection, round_index: int, start: Mapping[str, torch.Tensor],
                  published_start: Mapping[str, torch.Tensor], work: Path, stack: contextlib.ExitStack,
                  device: torch.device) -> list[WorkerResult]:
    """The round's worker results as the variant sees them.

    ``start`` is the variant's own start state (used to rebuild states from
    deltas); ``published_start`` is the start state the workers trained from
    (used to generate in-memory inputs).
    """
    results = []
    for s, examples in zip(round_slices(kind, cfg, round_index), EXAMPLES[kind]):
        if not v.files:
            names = held_names(published_start, s)
            state = LazyState(names, lambda n, s=s: (published_start[n].to("cpu")
                                                     + noise(kind, round_index, s.worker, n, published_start[n].shape)).to(device))
        elif v.representation == "full":
            state = file_state(stack, input_path(work, kind, round_index, s.worker, "state"), device)
        else:
            delta = file_state(stack, input_path(work, kind, round_index, s.worker, "delta"), device)
            if v.representation == "delta-rebuild":
                state = LazyState(list(delta), lambda n, d=delta: start[n] - d[n])
            else:
                state = delta  # delta-direct merges the deltas themselves
        results.append(WorkerResult(s, state, examples))
    return ordered(results, v.order)


def _weighted_mean_true_division(tensors: list[torch.Tensor], weights: list[float]) -> torch.Tensor:
    """``merge._weighted_mean`` with the final division by a float64 tensor on the same device.

    On CUDA, PyTorch divides by a Python number by multiplying with its
    reciprocal, which differs from the CPU's IEEE division in the last bit of
    float64 (checked 2026-10-14 on PyTorch 2.12.1+cu126). Dividing by a device
    tensor is true division on both. Same accumulation order as the original.
    """
    total = sum(weights)
    acc = torch.zeros_like(tensors[0], dtype=torch.float64)
    for t, w in zip(tensors, weights):
        acc += t.to(torch.float64) * w
    return acc / torch.tensor(total, dtype=torch.float64, device=acc.device)


@contextlib.contextmanager
def true_division(enabled: bool):
    """Swap the merge module's weighted mean for :func:`_weighted_mean_true_division` while active."""
    # The package re-exports the function ``merge``, which shadows the submodule as an attribute.
    merge_module = importlib.import_module("cassandra_chorus.coordinator.merge")
    original = merge_module._weighted_mean
    if enabled:
        merge_module._weighted_mean = _weighted_mean_true_division
    try:
        yield
    finally:
        merge_module._weighted_mean = original


def merge_once(global_state: Mapping[str, torch.Tensor], results: list[WorkerResult], outer: Any,
               representation: str) -> dict[str, torch.Tensor]:
    if representation != "delta-direct":
        return merge(global_state, results, router_rule="holders", outer=outer)[0]
    if not isinstance(outer, PlainAverage):
        raise ValueError("delta-direct is defined for plain averaging only")
    # new = G - (sum n_i D_i) / (sum n_i), with the holder rules of merge(): average the deltas
    # against a zero "global state" in float64, then subtract once and cast.
    zeros = LazyState(list(global_state), lambda n: torch.zeros(global_state[n].shape, dtype=torch.float64,
                                                                device=global_state[n].device))
    mean_delta = merge(zeros, results, router_rule="holders", outer=PlainAverage())[0]
    return {n: (g.double() - mean_delta[n]).to(g.dtype) for n, g in global_state.items()}


def run_variant(v: Variant, kind: str, cfg: ModelSection, g0: Mapping[str, torch.Tensor], work: Path,
                reference: Mapping[str, Mapping[str, torch.Tensor]],
                keep_open: contextlib.ExitStack) -> tuple[dict[str, Any], dict[str, Mapping[str, torch.Tensor]]]:
    """Run the variant's merges for one kind.

    Each output is hashed and compared with ``reference[label]`` as soon as it
    exists. Returns the per-label results and, when ``v.keep``, the outputs as
    file-backed states held open by ``keep_open`` (the caller closes it).
    """
    device = torch.device(v.device)
    out_dir = work / "outputs" / v.name
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {}
    kept: dict[str, Mapping[str, torch.Tensor]] = {}

    def emit(label: str, state: Mapping[str, torch.Tensor]) -> Mapping[str, torch.Tensor]:
        out: Mapping[str, torch.Tensor] = {n: t.detach().to("cpu").contiguous() for n, t in state.items()}
        if v.files:
            path = out_dir / f"{kind}-{label}.safetensors"
            save_file(dict(out), str(path))
            out = file_state(keep_open, path, torch.device("cpu"))
        ref = reference.get(label)
        results[label] = {"hash": canonical_hash(out), "against_reference": None if ref is None else bit_diff(ref, out)}
        if v.keep:
            kept[label] = out
        return out

    with contextlib.ExitStack() as stack:
        published_1 = file_state(stack, work / "inputs" / f"{kind}-published-1.safetensors", torch.device("cpu"))
        g = {n: t.to(device) for n, t in g0.items()}
        res1 = build_results(v, kind, cfg, 1, g, g0, work, stack, device)
        emit("plain-1", merge_once(g, res1, PlainAverage(), v.representation))
        if v.representation != "delta-direct":
            outer = NesterovOuter(**NESTEROV)
            n1 = emit("nesterov-1", merge_once(g, res1, outer, v.representation))
            emit("velocity-1", outer.velocity)
            dtype = getattr(torch, v.velocity_dtype)
            if v.files:  # the stored outer state goes through a file like everything else
                vpath = out_dir / f"{kind}-velocity-stored.safetensors"
                save_file({n: t.to(dtype).cpu() for n, t in outer.velocity.items()}, str(vpath))
                stored = file_state(stack, vpath, device)
                outer.velocity = {n: stored[n].to(torch.float64) for n in stored}
            else:
                outer.velocity = {n: t.to(dtype).to(torch.float64) for n, t in outer.velocity.items()}
            del g
            g1 = {n: n1[n].to(device) for n in n1}
            del n1
            res2 = build_results(v, kind, cfg, 2, g1, published_1, work, stack, device)
            emit("nesterov-2", merge_once(g1, res2, outer, v.representation))
            emit("velocity-2", outer.velocity)
    return results, kept


# --------------------------------------------------------------------------
# Driver


def prepare_inputs(work: Path, cfg: ModelSection, g0: Mapping[str, torch.Tensor]) -> dict[str, str]:
    """Round 1 inputs from G0; the published round-1 Nesterov merge; round 2 inputs from it."""
    hashes = {"g0": canonical_hash(g0)}
    (work / "inputs").mkdir(parents=True, exist_ok=True)
    for kind in EXAMPLES:
        write_round_inputs(work, kind, cfg, 1, g0)
        with contextlib.ExitStack() as stack:
            res = [WorkerResult(s, file_state(stack, input_path(work, kind, 1, s.worker, "state"), torch.device("cpu")), n)
                   for s, n in zip(round_slices(kind, cfg, 1), EXAMPLES[kind])]
            published, _ = merge(g0, res, router_rule="holders", outer=NesterovOuter(**NESTEROV))
        path = work / "inputs" / f"{kind}-published-1.safetensors"
        save_file(published, str(path))
        hashes[f"{kind}-published-1"] = canonical_hash(published)
        write_round_inputs(work, kind, cfg, 2, published)
        del published
    return hashes


def run(cfg: ModelSection, work: Path, use_cuda: bool) -> dict[str, Any]:
    """Prepare inputs, run every variant, return the report. Writes only under ``work``."""
    started = time.time()
    g0 = initial_state(cfg)
    report: dict[str, Any] = {
        "prototype": "P6 merge determinism",
        "plan": "docs/implementations/2026-10-14-solo-prototypes.md",
        "environment": environment_info(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "default_cpu_threads": torch.get_num_threads(),
        "model": {"config": dataclasses.asdict(cfg), "parameters": sum(t.numel() for t in g0.values())},
        "workers": {k: {"examples": v} for k, v in EXAMPLES.items()},
        "noise_std": NOISE_STD,
        "nesterov": NESTEROV,
        "input_hashes": prepare_inputs(work, cfg, g0),
        "variants": [],
    }
    kept: dict[str, dict[str, dict[str, Mapping[str, torch.Tensor]]]] = {}
    kept_stacks: list[contextlib.ExitStack] = []
    default_threads = torch.get_num_threads()
    try:
        for v in variants(use_cuda):
            t0 = time.time()
            entry: dict[str, Any] = {**dataclasses.asdict(v), "kinds": {}}
            stack = contextlib.ExitStack()
            if v.threads:
                torch.set_num_threads(v.threads)
            try:
                for kind in EXAMPLES:
                    reference = kept.get(v.reference or "", {}).get(kind, {})
                    with true_division(v.true_division):
                        entry["kinds"][kind], outs = run_variant(v, kind, cfg, g0, work, reference, stack)
                    if v.keep:
                        kept.setdefault(v.name, {})[kind] = outs
            finally:
                torch.set_num_threads(default_threads)
                if v.device == "cuda":
                    torch.cuda.empty_cache()
                if v.keep:
                    kept_stacks.append(stack)
                else:  # close the files before deleting them (Windows keeps open files)
                    stack.close()
                    shutil.rmtree(work / "outputs" / v.name, ignore_errors=True)
            entry["seconds_including_checks"] = round(time.time() - t0, 1)
            report["variants"].append(entry)
            print(f"[p6] {v.name}: {entry['seconds_including_checks']} s", flush=True)
    finally:
        for s in kept_stacks:
            s.close()
    report["seconds_total"] = round(time.time() - started, 1)
    return report


def summary_markdown(report: dict[str, Any]) -> str:
    env = report["environment"]
    lines = [
        "# P6 merge determinism",
        "",
        f"Plan: `{report['plan']}`. Model: Task B, {report['model']['parameters']:,} parameters, seed {SEED}. "
        f"Hardware: {(env.get('gpu') or {}).get('name', 'no GPU')}; {env['os']}; PyTorch {env['torch']} "
        f"(CUDA {env['torch_cuda']}); default CPU threads {report['default_cpu_threads']}; "
        f"deterministic algorithms {'on' if report['deterministic_algorithms'] else 'off'}. One machine.",
        "",
        "Each cell compares the variant's output with its reference variant: **equal** (bitwise), "
        "or the number of differing elements and the largest absolute difference.",
        "",
    ]
    for kind in EXAMPLES:
        lines += [f"## {kind}", "", "| Variant | Reference | " + " | ".join(STATE_LABELS + VELOCITY_LABELS) + " |",
                  "|---|---|" + "---|" * (len(STATE_LABELS) + len(VELOCITY_LABELS))]
        for entry in report["variants"]:
            cells = []
            for label in STATE_LABELS + VELOCITY_LABELS:
                item = entry["kinds"][kind].get(label)
                if item is None:
                    cells.append("n/a")
                elif item["against_reference"] is None:
                    cells.append(f"`{item['hash'][:12]}`")
                elif item["against_reference"]["bitwise_equal"]:
                    cells.append("equal")
                else:
                    d = item["against_reference"]
                    cells.append(f"{d['elements_differing']:,} differ, max {d['max_abs']:.2e}")
            lines.append(f"| {entry['name']} | {entry['reference'] or 'none'} | " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--work-dir", type=Path, default=None, help="folder for input and output files (default: runs folder)")
    parser.add_argument("--keep-files", action="store_true", help="keep the work folder afterwards")
    parser.add_argument("--no-cuda", action="store_true", help="skip the GPU variants")
    args = parser.parse_args(argv)
    work = args.work_dir or (runs_root() / "proto-p6")
    if work.exists():
        raise SystemExit(f"{work} exists; remove it or pass another --work-dir")
    use_cuda = torch.cuda.is_available() and not args.no_cuda
    try:
        report = run(task_b_model_config(), work, use_cuda)
    finally:
        if not args.keep_files:
            shutil.rmtree(work, ignore_errors=True)
    write_json(RESULTS_DIR / "p6_merge_determinism.json", report)
    (RESULTS_DIR / "p6_merge_determinism.md").write_text(summary_markdown(report), encoding="utf-8")
    print(f"[p6] done in {report['seconds_total']} s; results in {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
