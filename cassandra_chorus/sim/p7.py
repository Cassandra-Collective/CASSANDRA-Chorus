"""Opt-in P7 execution and diagnostics, using the unchanged worker and merge."""

from __future__ import annotations

import dataclasses
import math

import torch
import torch.nn.functional as F

from cassandra_chorus.coordinator import WorkerResult, merge
from cassandra_chorus.model import MoETransformer
from cassandra_chorus.sim.worker import train_worker
from cassandra_chorus.train import make_optimizer, train_steps


class P7Runtime:
    """Mutable counters and optional central optimizer, restored from checkpoint metadata.

    Construction reads a metadata dictionary without mutating it. Model and
    optimizer construction is deferred until central training is requested.
    """

    def __init__(self, saved: dict | None = None):
        saved = saved or {}
        self.steps_run = saved.get("steps_run", 0)
        self.steps_merged = saved.get("steps_merged", 0)
        self.elapsed = saved.get("elapsed", 0.0)
        self.assignment_round = saved.get("assignment_round", 0)
        self.pending_workers = saved.get("pending_workers")
        self.optimizer_state = saved.get("optimizer")
        self.model = None
        self.optimizer = None

    def snapshot(self) -> dict:
        """Return checkpoint metadata, including AdamW state when present; no mutation."""
        return {"steps_run": self.steps_run, "steps_merged": self.steps_merged,
                "elapsed": self.elapsed, "assignment_round": self.assignment_round,
                "pending_workers": self.pending_workers,
                "optimizer": self.optimizer.state_dict() if self.optimizer is not None else self.optimizer_state}


def execute_round(cfg, global_state, outer, runtime: P7Runtime, timing: dict, slices: dict,
                  round_index: int, batch_factory, device) -> tuple[dict, dict, list[dict], dict]:
    """Execute planned work and return (global state, merge report, workers, accounting).

    The batch factory takes a worker index and returns its seeded next-batch
    callback. Updates runtime accounting for all work, and the supplied outer
    optimizer only for counted updates. Late and partial work is charged then discarded. The
    central arm instead updates one persistent model and AdamW immediately.
    Global input tensors are never changed in place.
    """
    sim = cfg.sim
    central = sim.round_mode == "centralized"
    if central and runtime.model is None:
        with torch.random.fork_rng(devices=[]):
            runtime.model = MoETransformer(cfg.model)
        runtime.model.load_state_dict(global_state)
        runtime.model.to(device)
        runtime.optimizer = make_optimizer(runtime.model, cfg.optim)
        if runtime.optimizer_state is not None:
            runtime.optimizer.load_state_dict(runtime.optimizer_state)
    workers, results = [], []
    run_steps = merged_steps = examples = 0
    for i, record in enumerate(timing["workers"]):
        name = record["worker"]
        item = {**record, "held": {layer: list(e) for layer, e in slices[name].experts.items()}}
        steps = record["steps_run"]
        if steps:
            if central:
                stats = train_steps(runtime.model, runtime.optimizer, batch_factory(i), steps, cfg.optim, device,
                                    start_step=runtime.steps_run + run_steps, total_steps=sim.equal_compute_steps)
            else:
                wr = train_worker(cfg.model, cfg.optim, global_state, slices[name], sim.mode, batch_factory(i),
                                  round_index, steps, sim.rounds * sim.local_steps, device,
                                  start_step=runtime.assignment_round * sim.local_steps)
                stats = wr.stats
                if name in timing["counted"]:
                    results.append(WorkerResult(slices[name], wr.state, stats.sequences))
                    merged_steps += steps
                del wr
            item["train"] = dataclasses.asdict(stats)
            examples += stats.sequences
        run_steps += steps
        item["counted"] = steps > 0 if central else name in timing["counted"]
        workers.append(item)
    if central:
        new_state = {k: v.detach().clone() for k, v in runtime.model.state_dict().items()}
        merged_steps = run_steps
        report = {"workers": [w["worker"] for w in workers if w["steps_run"]], "total_examples": examples,
                  "holder_counts": {layer: [1] * cfg.model.n_experts for layer in range(cfg.model.n_layers)},
                  "router_rule": "all", "outer": {"name": "centralized_adamw"}}
    else:
        results.sort(key=lambda result: result.slice.worker)
        new_state, merged = merge(global_state, results, sim.router_rule, outer)
        report = dataclasses.asdict(merged)
    runtime.steps_run += run_steps
    runtime.steps_merged += merged_steps
    runtime.elapsed += timing["duration"]
    if sim.round_mode == "synchronous" and timing["aborted"]:
        runtime.pending_workers = timing["assigned"] or None
    else:
        runtime.pending_workers = None
        runtime.assignment_round += 1
    tokens_per_step = cfg.optim.batch_size * cfg.optim.grad_accum * cfg.text8.context_length
    accounting = {"steps_run": run_steps, "steps_merged": merged_steps,
                  "cumulative_steps_run": runtime.steps_run, "cumulative_steps_merged": runtime.steps_merged,
                  "tokens_run": run_steps * tokens_per_step, "tokens_merged": merged_steps * tokens_per_step,
                  "cumulative_tokens_run": runtime.steps_run * tokens_per_step,
                  "cumulative_tokens_merged": runtime.steps_merged * tokens_per_step,
                  "simulated_seconds": timing["duration"], "cumulative_simulated_seconds": runtime.elapsed}
    return new_state, report, workers, accounting


@torch.no_grad()
def evaluate_holder_quality(model, data, counts: dict[int, list[int]], device, max_chars: int,
                            tracked: set[tuple[int, int]] | None = None) -> list[dict]:
    """Return conditional BPC for low-holder experts and explicitly tracked targets.

    Observes existing router selections on the fixed validation prefix. No
    gradients, parameters or routing change. Restores training mode even on
    failure. A population with no routed positions has BPC None.
    Tracked targets are observed even before their holder drop and after
    recovery. Conditional losses describe the full model, not a causal expert score.
    """
    targets = [(layer, e, holders) for layer, layer_counts in counts.items()
               for e, holders in enumerate(layer_counts) if holders <= 1 or (layer, e) in (tracked or set())]
    if not targets:
        return []
    totals = {key[:2]: [0.0, 0] for key in targets}
    was_training = model.training
    try:
        model.eval()
        windows = data.n_windows("valid", max_chars)
        for first in range(0, windows, 64):
            inputs, expected = data.eval_windows("valid", first, min(64, windows - first))
            out = model(inputs.to(device), return_routing=True)
            loss = F.cross_entropy(out.logits.reshape(-1, out.logits.shape[-1]),
                                   expected.to(device).reshape(-1), reduction="none")
            for layer, expert, _ in targets:
                selected = (out.routing[layer] == expert).any(dim=-1).reshape(-1)
                totals[layer, expert][0] += loss[selected].sum().item()
                totals[layer, expert][1] += int(selected.sum().item())
    finally:
        model.train(was_training)
    return [{"layer": layer, "expert": expert, "holders": holders,
             "scored": totals[layer, expert][1],
             "bpc": totals[layer, expert][0] / (totals[layer, expert][1] * math.log(2))
             if totals[layer, expert][1] else None} for layer, expert, holders in targets]
