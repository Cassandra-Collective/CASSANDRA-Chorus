"""Replayable synthetic timing and fault tapes for P7, without training or sleeping."""

from __future__ import annotations

import dataclasses
import hashlib
import math
import random
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from cassandra_chorus.config import load_config
from cassandra_chorus.coordinator import Slice
from cassandra_chorus.repro import derive_seed

if TYPE_CHECKING:
    from cassandra_chorus.sim.harness import SimSection


@dataclasses.dataclass(frozen=True)
class ChurnEvent:
    """A persistent membership transition at a zero-based tape round and offset."""

    round: int
    at: float
    worker: str
    action: Literal["depart", "arrive"]


@dataclasses.dataclass(frozen=True)
class HolderDrop:
    """A temporary failure of one or both reference holders, confined to one slot."""

    round: int
    at: float
    layer: int
    expert: int
    remaining: Literal[0, 1]


@dataclasses.dataclass(frozen=True)
class ChurnTape:
    """Validated immutable events and interventions; workers initially start online."""

    version: int = 1
    event: tuple[ChurnEvent, ...] = ()
    holder_drop: tuple[HolderDrop, ...] = ()


def validate_deadline(sim: SimSection) -> list[str]:
    """Return setting errors without side effects; legacy settings must remain inert."""
    problems = []
    if sim.round_mode == "legacy":
        defaults = type(sim)()
        fields = [f.name for f in dataclasses.fields(sim)]
        if any(getattr(sim, key) != getattr(defaults, key) for key in fields[fields.index("q_min"):]):
            problems.append("P7 settings require a non-legacy round_mode")
        return problems
    if not 1 <= sim.q_min <= sim.n_workers:
        problems.append("q_min must be between 1 and n_workers")
    values = (sim.round_length, sim.deadline, sim.grace, sim.speed_min, sim.speed_max,
              sim.upload_min, sim.upload_max, sim.sync_timeout)
    if not all(math.isfinite(v) for v in values):
        problems.append("P7 timing values must be finite")
    if not 0 <= sim.grace < sim.round_length or not 0 < sim.deadline <= sim.round_length - sim.grace:
        problems.append("require 0 < deadline <= round_length - grace and 0 <= grace < round_length")
    if not 0 < sim.speed_min <= sim.speed_max or not 0 <= sim.upload_min <= sim.upload_max:
        problems.append("require positive ordered speeds and nonnegative ordered upload times")
    if sim.sync_timeout < sim.deadline:
        problems.append("sync_timeout must be at least deadline")
    if sim.drop_prob or sim.decay_local_steps or sim.mode != "sliced" or sim.policy != "rolling":
        problems.append("P7 requires sliced rolling assignment, drop_prob=0 and decay_local_steps=0")
    if bool(sim.churn_file) != bool(sim.churn_sha256):
        problems.append("churn_file and churn_sha256 must be supplied together")
    if sim.churn_sha256 and (len(sim.churn_sha256) != 64
                             or any(c not in "0123456789abcdef" for c in sim.churn_sha256)):
        problems.append("churn_sha256 must be a lowercase SHA-256 hex digest")
    if sim.round_mode == "centralized" and sim.outer != "plain":
        problems.append("centralized uses AdamW directly; outer must be plain")
    return problems


def load_tape(sim: SimSection, n_layers: int, n_experts: int, top_k: int,
              path: Path | None = None) -> ChurnTape:
    """Read and validate the pinned tape, optionally from a run's snapshot.

    Raises ValueError for a hash mismatch or invalid event. Reads files only;
    no state is changed. Without a configured file, returns an empty tape.
    """
    from cassandra_chorus.sim.harness import round_slices

    if not sim.churn_file:
        return ChurnTape()
    source = Path(sim.churn_file) if path is None else path
    if hashlib.sha256(source.read_bytes()).hexdigest() != sim.churn_sha256:
        raise ValueError("churn tape SHA-256 does not match churn_sha256")
    tape = load_config(source, ChurnTape)
    if tape.version != 1:
        raise ValueError("unsupported churn tape version")
    online = {f"w{i}": True for i in range(sim.n_workers)}
    previous = (-1, -1.0, "")
    seen = set()
    for event in tape.event:
        key = (event.round, event.at, event.worker)
        if key < previous or key in seen:
            raise ValueError("churn events must be sorted and cannot repeat a worker at one instant")
        previous = key
        seen.add(key)
        _check_offset(sim, event.round, event.at)
        if event.worker not in online:
            raise ValueError(f"unknown churn worker {event.worker!r}")
        arriving = event.action == "arrive"
        if online[event.worker] == arriving:
            raise ValueError(f"invalid membership transition for {event.worker}")
        online[event.worker] = arriving
    seen_targets = set()
    for drop in tape.holder_drop:
        _check_offset(sim, drop.round, drop.at)
        target = (drop.round, drop.layer, drop.expert)
        if target in seen_targets or not 0 <= drop.layer < n_layers or not 0 <= drop.expert < n_experts:
            raise ValueError("invalid or repeated holder-drop target")
        seen_targets.add(target)
        reference = round_slices(sim, n_layers, n_experts, top_k, drop.round, 0)
        # The run seed matters for independent layer relabelling. Require common indices here.
        if sim.cross_layer != "same" or len(_holders(reference, drop.layer, drop.expert)) != 2:
            raise ValueError("holder drops require same-layer rolling assignment with exactly two holders")
    return tape


def _check_offset(sim: SimSection, round_index: int, at: float) -> None:
    """Reject offsets outside the offered tape; has no side effects."""
    if not 0 <= round_index < sim.rounds or not math.isfinite(at) or not 0 <= at < sim.round_length - sim.grace:
        raise ValueError("tape round/offset lies outside the simulation")


def _holders(slices: dict[str, Slice], layer: int, expert: int) -> list[str]:
    """Return holder IDs in lexical order without changing slices."""
    return sorted(name for name, slice_ in slices.items() if slice_.holds(layer, expert))


def holder_counts(slices: dict[str, Slice], workers, n_experts: int) -> dict[int, list[int]]:
    """Count the supplied workers' holders per expert and layer, without mutation."""
    names = set(workers)
    layers = next(iter(slices.values())).experts
    return {layer: [sum(name in names and slice_.holds(layer, e) for name, slice_ in slices.items())
                    for e in range(n_experts)] for layer in layers}


def worker_times(sim: SimSection, seed: int, round_index: int, worker: str) -> tuple[float, float]:
    """Return seeded (steps per unit, upload units); never touch a process RNG."""
    rng = random.Random(derive_seed(seed, f"sim/time/{worker}/r{round_index}"))
    return rng.uniform(sim.speed_min, sim.speed_max), rng.uniform(sim.upload_min, sim.upload_max)


def timed_round(sim: SimSection, tape: ChurnTape, seed: int, round_index: int,
                reference: dict[str, Slice], n_experts: int,
                assigned: list[str] | None = None) -> dict:
    """Return membership, work, fault and close records without changing inputs.

    Reference slices resolve interventions identically for every arm. Optional
    assigned IDs preserve the participants of an aborted synchronous attempt.
    Does not execute training, mutate the tape, or consume global random state.
    """
    online = {name: True for name in reference}
    departures = {}
    for event in tape.event:
        if (event.round, event.at) <= (round_index, 0):
            online[event.worker] = event.action == "arrive"
        elif event.round == round_index and event.action == "depart":
            departures.setdefault(event.worker, event.at)
    injected, interventions = {}, []
    for drop in tape.holder_drop:
        if drop.round != round_index:
            continue
        holders = _holders(reference, drop.layer, drop.expert)
        failed = holders[:2 - drop.remaining]
        for name in failed:
            injected[name] = min(injected.get(name, math.inf), drop.at)
        interventions.append({**dataclasses.asdict(drop), "nominal_holders": holders, "failed_workers": failed})
    ready = [name for name in reference if online[name]]
    participants = ready if assigned is None else assigned
    cancel = sim.sync_timeout if sim.round_mode == "synchronous" else sim.round_length - sim.grace
    workers, posted = [], []
    for name in reference:
        speed, upload = worker_times(sim, seed, round_index, name)
        leave = min(departures.get(name, math.inf), injected.get(name, math.inf))
        active = name in participants and online[name]
        available = min(leave, cancel) if active else 0.0
        finish = sim.local_steps / speed
        steps = min(sim.local_steps, math.floor(available * speed))
        if finish <= available:  # avoid a rounding loss at an exact full-training boundary
            steps = sim.local_steps
        post = finish + upload
        valid_post = active and steps == sim.local_steps and post < leave and post <= cancel
        if valid_post:
            posted.append(name)
        reason = ("not_ready" if not active else "departed" if leave <= min(post, cancel)
                  else "cancelled" if steps < sim.local_steps else "upload_cancelled" if not valid_post
                  else "late" if post > sim.deadline else "posted")
        workers.append({"worker": name, "ready": active, "speed": speed, "upload": upload,
                        "departure": leave if math.isfinite(leave) else None, "steps_run": steps,
                        "planned_train_finish": finish, "planned_post_time": post,
                        "train_finish": finish if steps == sim.local_steps else None,
                        "post_time": post if valid_post else None, "posted": valid_post,
                        "lateness": post - sim.deadline if valid_post else None, "reason": reason})
    on_time = [w["worker"] for w in workers if w["posted"] and w["post_time"] <= sim.deadline]
    aborted = False
    if sim.round_mode == "synchronous":
        aborted = not participants or set(posted) != set(participants)
        counted = [] if aborted else posted
        close = sim.sync_timeout if aborted else max(w["post_time"] for w in workers if w["worker"] in counted)
    elif sim.round_mode == "centralized":
        counted, close = [], 0.0
    else:
        counted = on_time if len(on_time) >= sim.q_min else []
        close = sim.deadline
    duration = max(sim.round_length, close + sim.grace)
    if sim.round_mode == "centralized":
        duration = max(sim.round_length, sum(w["steps_run"] / w["speed"] for w in workers) + sim.grace)
    return {"workers": workers, "assigned": list(participants), "on_time": sorted(on_time),
            "counted": sorted(counted), "aborted": aborted, "close": close, "duration": duration,
            "interventions": interventions,
            "nominal_holders": holder_counts(reference, reference, n_experts),
            "intervention_holders": holder_counts(reference, set(reference) - set(injected), n_experts)}
