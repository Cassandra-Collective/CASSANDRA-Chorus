"""CPU checks for P7's synthetic protocol, without experiment runs."""

from __future__ import annotations

import dataclasses
import hashlib
import math
import random
from pathlib import Path

import pytest
import torch

from cassandra_chorus.config import RunSection, load_config
from cassandra_chorus.coordinator import NesterovOuter, PlainAverage
from cassandra_chorus.data.text8 import Text8Section
from cassandra_chorus.model import ModelSection, MoETransformer, expert_param_owner, router_param_layer
from cassandra_chorus.paths import REPO_ROOT
from cassandra_chorus.sim import SimSection, data_generator, round_slices, validate_sim
from cassandra_chorus.sim.deadline import ChurnEvent, ChurnTape, HolderDrop, load_tape, timed_round, worker_times
from cassandra_chorus.sim.p7 import P7Runtime, evaluate_holder_quality, execute_round
from cassandra_chorus.train import OptimSection, make_optimizer, train_steps
from scripts.train_task_b_sliced import SlicedTaskBConfig


def config(**changes):
    """Return a tiny three-worker CPU configuration with deterministic fast timing."""
    sim = SimSection(n_workers=3, capacities=(3, 3, 2), local_steps=2, rounds=3, equal_compute_steps=18,
                     policy="rolling", round_mode="deadline", deadline=2.0, round_length=4.0, grace=1.0,
                     speed_min=1.0, speed_max=1.0, upload_min=0.0, upload_max=0.0, sync_timeout=4.0)
    return SlicedTaskBConfig(run=RunSection(name="p7-unit", device="cpu"),
                            model=ModelSection(vocab_size=7, context_length=4, d_model=8, n_layers=1,
                                               n_heads=1, expert_hidden=8, n_experts=4, top_k=2),
                            optim=OptimSection(batch_size=2, warmup_steps=1),
                            text8=Text8Section(context_length=4),
                            sim=dataclasses.replace(sim, **changes))


def state(cfg):
    """Return reproducible independent CPU model tensors."""
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(7)
        return {k: v.clone() for k, v in MoETransformer(cfg.model).state_dict().items()}


def factory(cfg, round_index=0):
    """Return worker callbacks with independent replayable tiny token streams."""
    def make(i):
        generator = data_generator(7, i, round_index)
        return lambda: (torch.randint(0, 7, (2, 4), generator=generator),
                        torch.randint(0, 7, (2, 4), generator=generator))
    return make


def slices(cfg, r=0):
    """Return the test model's full-roster rolling reference assignment."""
    return round_slices(cfg.sim, 1, 4, 2, r, 7)


def pinned(cfg, tmp_path, text):
    """Write a test tape and return settings pinned to its exact bytes."""
    path = tmp_path / "churn.toml"
    path.write_text(text, encoding="utf-8")
    return dataclasses.replace(cfg.sim, churn_file=str(path), churn_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def test_tape_and_time_replay_from_seed_and_file(tmp_path):
    cfg = config(speed_min=0.5, speed_max=2.0)
    sim = pinned(cfg, tmp_path, '[[event]]\nround=0\nat=1.0\nworker="w0"\naction="depart"\n'
                 '[[event]]\nround=1\nat=1.0\nworker="w0"\naction="arrive"\n')
    a = load_tape(sim, 1, 4, 2)
    b = load_tape(sim, 1, 4, 2)
    py_rng, torch_rng = random.getstate(), torch.get_rng_state()
    assert timed_round(sim, a, 7, 0, slices(cfg), 4) == timed_round(sim, b, 7, 0, slices(cfg), 4)
    assert worker_times(sim, 7, 0, "w0") != worker_times(sim, 11, 0, "w0")
    assert random.getstate() == py_rng and torch.equal(torch_rng, torch.get_rng_state())
    assert [timed_round(sim, a, 7, r, slices(cfg, r), 4)["workers"][0]["ready"]
            for r in range(3)] == [True, False, True]
    Path(sim.churn_file).write_text("version=1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256"):
        load_tape(sim, 1, 4, 2)


@pytest.mark.parametrize("text, message", [
    ('[[event]]\nround=0\nat=0.0\nworker="w9"\naction="depart"\n', "unknown churn"),
    ('[[event]]\nround=0\nat=0.0\nworker="w0"\naction="arrive"\n', "transition"),
    ('[[event]]\nround=4\nat=0.0\nworker="w0"\naction="depart"\n', "outside"),
    ('[[event]]\nround=0\nat=3.0\nworker="w0"\naction="depart"\n', "outside"),
    ('[[event]]\nround=1\nat=0.0\nworker="w0"\naction="depart"\n'
     '[[event]]\nround=0\nat=0.0\nworker="w1"\naction="depart"\n', "sorted"),
    ('version=2\n', "version"),
    ('[[holder_drop]]\nround=0\nat=1.0\nlayer=2\nexpert=0\nremaining=1\n', "target"),
])
def test_invalid_tapes_are_rejected(tmp_path, text, message):
    sim = pinned(config(), tmp_path, text)
    with pytest.raises(ValueError, match=message):
        load_tape(sim, 1, 4, 2)


def test_holder_intervention_requires_two_nominal_holders(tmp_path):
    sim = pinned(config(capacities=(2, 2, 2)), tmp_path,
                 '[[holder_drop]]\nround=0\nat=1.0\nlayer=0\nexpert=2\nremaining=1\n')
    with pytest.raises(ValueError, match="exactly two holders"):
        load_tape(sim, 1, 4, 2)


@pytest.mark.parametrize("changes", [
    {"q_min": 0}, {"q_min": 4}, {"speed_min": 0.0}, {"speed_max": float("nan")},
    {"upload_min": -1.0}, {"deadline": 3.1}, {"grace": 4.0}, {"sync_timeout": 1.0},
    {"churn_file": "unhashed.toml"}, {"round_mode": "legacy", "holder_quality": True},
    {"mode": "full", "router_rule": "all"}, {"drop_prob": 0.1},
])
def test_invalid_p7_settings(changes):
    with pytest.raises(ValueError):
        validate_sim(config(**changes).sim, 4, 2)


def test_deadline_and_departure_boundaries():
    cfg = config()
    on_time = timed_round(cfg.sim, ChurnTape(), 7, 0, slices(cfg), 4)
    assert on_time["counted"] == ["w0", "w1", "w2"]  # post exactly at D counts
    tape = ChurnTape(event=(ChurnEvent(0, 2.0, "w0", "depart"),))
    tied = timed_round(cfg.sim, tape, 7, 0, slices(cfg), 4)
    assert "w0" not in tied["counted"] and tied["workers"][0]["steps_run"] == 2
    early = ChurnTape(event=(ChurnEvent(0, 0.0, "w0", "depart"),))
    assert timed_round(cfg.sim, early, 7, 0, slices(cfg), 4)["workers"][0]["steps_run"] == 0
    missing = timed_round(cfg.sim, early, 7, 0, slices(cfg), 4)["workers"][0]
    assert missing["post_time"] is None and missing["lateness"] is None


def test_upload_departure_loses_complete_work():
    cfg = config(upload_min=0.5, upload_max=0.5, deadline=3.0)
    tape = ChurnTape(event=(ChurnEvent(0, 2.25, "w0", "depart"),))
    timing = timed_round(cfg.sim, tape, 7, 0, slices(cfg), 4)
    worker = timing["workers"][0]
    assert worker["steps_run"] == 2 and worker["reason"] == "departed" and not worker["posted"]
    assert worker["post_time"] is None and worker["lateness"] is None
    assert worker["planned_post_time"] == 2.5
    assert timing["counted"] == ["w1", "w2"]


@pytest.mark.parametrize("outer_type", [PlainAverage, NesterovOuter])
def test_nonempty_subquorum_keeps_global_and_outer_state(monkeypatch, outer_type):
    cfg = config(q_min=3)
    monkeypatch.setattr("cassandra_chorus.sim.deadline.worker_times",
                        lambda sim, seed, r, name: (2.0 if name == "w0" else 0.5, 0.0))
    timing = timed_round(cfg.sim, ChurnTape(), 7, 0, slices(cfg), 4)
    assert timing["on_time"] == ["w0"] and timing["counted"] == []
    before, outer = state(cfg), outer_type()
    if isinstance(outer, NesterovOuter):
        outer.velocity = {k: torch.ones_like(v, dtype=torch.float64) for k, v in before.items()}
        velocity = {k: v.clone() for k, v in outer.velocity.items()}
    after, report, workers, accounting = execute_round(cfg, before, outer, P7Runtime(), timing, slices(cfg),
                                                       0, factory(cfg), "cpu")
    assert all(torch.equal(before[k], after[k]) for k in before)
    if isinstance(outer, NesterovOuter):
        assert velocity.keys() == outer.velocity.keys()
        assert all(torch.equal(velocity[k], outer.velocity[k]) for k in velocity)
    assert report["workers"] == [] and accounting["steps_run"] == 4 and accounting["steps_merged"] == 0
    assert sum(w["train"]["steps"] for w in workers) == 4


def test_late_work_executes_but_is_not_counted(monkeypatch):
    cfg = config()
    monkeypatch.setattr("cassandra_chorus.sim.deadline.worker_times",
                        lambda sim, seed, r, name: (0.8 if name == "w0" else 1.0, 0.0))
    timing = timed_round(cfg.sim, ChurnTape(), 7, 0, slices(cfg), 4)
    assert timing["workers"][0]["steps_run"] == 2 and timing["workers"][0]["lateness"] == 0.5
    _, report, _, accounting = execute_round(cfg, state(cfg), PlainAverage(), P7Runtime(), timing,
                                             slices(cfg), 0, factory(cfg), "cpu")
    assert report["workers"] == ["w1", "w2"]
    assert (accounting["steps_run"], accounting["steps_merged"]) == (6, 4)


@pytest.mark.parametrize("remaining", [1, 0])
def test_injected_drops_record_intended_counts_and_keep_unheld_state(remaining):
    cfg, outer = config(), NesterovOuter()
    before = state(cfg)
    outer.velocity = {k: torch.ones_like(v, dtype=torch.float64) for k, v in before.items()}
    velocity = {k: v.clone() for k, v in outer.velocity.items()}
    tape = ChurnTape(holder_drop=(HolderDrop(0, 1.0, 0, 0, remaining),))
    timing = timed_round(cfg.sim, tape, 7, 0, slices(cfg), 4)
    assert timing["nominal_holders"][0][0] == 2
    assert timing["intervention_holders"][0][0] == remaining
    after, report, _, accounting = execute_round(cfg, before, outer, P7Runtime(), timing, slices(cfg),
                                                 0, factory(cfg), "cpu")
    assert report["holder_counts"][0][0] == remaining
    assert accounting["steps_run"] > accounting["steps_merged"]
    if remaining == 0:
        for name in before:
            if expert_param_owner(name) == (0, 0):
                assert torch.equal(before[name], after[name]) and torch.equal(velocity[name], outer.velocity[name])
            elif router_param_layer(name) == 0:
                assert torch.equal(before[name][0], after[name][0])
                assert torch.equal(velocity[name][0], outer.velocity[name][0])


def test_synchronous_aborts_and_retries_assignment():
    cfg = config(round_mode="synchronous")
    runtime, outer = P7Runtime(), NesterovOuter()
    before = state(cfg)
    tape = ChurnTape(holder_drop=(HolderDrop(0, 1.0, 0, 0, 1),))
    timing = timed_round(cfg.sim, tape, 7, 0, slices(cfg), 4)
    after, _, _, acc = execute_round(cfg, before, outer, runtime, timing, slices(cfg), 0, factory(cfg), "cpu")
    assert timing["aborted"] and acc["steps_merged"] == 0 and runtime.assignment_round == 0
    assert all(torch.equal(after[k], before[k]) for k in before)
    assert runtime.pending_workers == ["w0", "w1", "w2"]
    retry = timed_round(cfg.sim, tape, 7, 1, slices(cfg, 1), 4, runtime.pending_workers)
    _, report, _, _ = execute_round(cfg, after, outer, runtime, retry, slices(cfg), 1, factory(cfg, 1), "cpu")
    assert report["workers"] == ["w0", "w1", "w2"] and runtime.assignment_round == 1
    assert runtime.pending_workers is None


def test_centralized_uses_one_continuing_optimizer_and_retains_partial_work():
    cfg, runtime = config(round_mode="centralized"), P7Runtime()
    current = state(cfg)
    model = MoETransformer(cfg.model)
    model.load_state_dict(current)
    optimizer = make_optimizer(model, cfg.optim)
    tape = ChurnTape(holder_drop=(HolderDrop(0, 1.0, 0, 0, 1),))
    step = 0
    for r in range(2):
        timing = timed_round(cfg.sim, tape, 7, r, slices(cfg, r), 4)
        for i, worker in enumerate(timing["workers"]):
            n = worker["steps_run"]
            if n:
                train_steps(model, optimizer, factory(cfg, r)(i), n, cfg.optim, "cpu",
                            start_step=step, total_steps=cfg.sim.equal_compute_steps)
                step += n
        current, _, _, _ = execute_round(cfg, current, PlainAverage(), runtime, timing, slices(cfg, r),
                                          r, factory(cfg, r), "cpu")
    assert runtime.steps_run == runtime.steps_merged == step == 11
    assert all(torch.equal(current[k], v) for k, v in model.state_dict().items())
    for key, expected in optimizer.state_dict()["state"].items():
        assert all(torch.equal(expected[field], runtime.optimizer.state_dict()["state"][key][field])
                   for field in expected)


def test_holder_quality_matches_routed_population_and_restores_mode():
    cfg = config()
    model = MoETransformer(cfg.model)
    model.load_state_dict(state(cfg))
    inputs, targets = factory(cfg)(0)()

    class Data:
        def n_windows(self, split, max_chars):
            return 2

        def eval_windows(self, split, first, count):
            return inputs, targets

    before = {k: v.clone() for k, v in model.state_dict().items()}
    quality = evaluate_holder_quality(model, Data(), {0: [0, 1, 2, 2]}, "cpu", 8)
    tracked = evaluate_holder_quality(model, Data(), {0: [2, 2, 2, 2]}, "cpu", 8, {(0, 0)})
    assert len(tracked) == 1 and tracked[0]["expert"] == 0 and tracked[0]["holders"] == 2
    out = model(inputs, return_routing=True)
    loss = torch.nn.functional.cross_entropy(out.logits.reshape(-1, 7), targets.reshape(-1), reduction="none")
    for result in quality:
        mask = (out.routing[0] == result["expert"]).any(dim=-1).reshape(-1)
        assert result["scored"] == int(mask.sum())
        if result["scored"]:
            assert result["bpc"] == pytest.approx(float(loss[mask].mean().detach()) / math.log(2))
        else:
            assert result["bpc"] is None
    assert model.training and not model.blocks[0].moe._forward_hooks
    assert all(torch.equal(before[k], v) for k, v in model.state_dict().items())


def test_holder_quality_restores_mode_on_evaluation_failure():
    model = MoETransformer(config().model)

    class BrokenData:
        def n_windows(self, split, max_chars):
            raise RuntimeError("broken fixture")

    with pytest.raises(RuntimeError, match="broken fixture"):
        evaluate_holder_quality(model, BrokenData(), {0: [0, 1, 2, 2]}, "cpu", 8)
    assert model.training


def test_queue_is_complete_pinned_and_replays_identical_interventions():
    from scripts.ops.run_queue import load_queue

    runs, stop = load_queue(REPO_ROOT / "configs/queues/p7_deadline_quorum.toml")
    assert stop and len(runs) == 36
    seen, interventions = set(), {}
    for entry in runs:
        args = entry["args"]
        cfg = load_config(REPO_ROOT / args[args.index("--config") + 1], SlicedTaskBConfig,
                          [args[i + 1] for i, value in enumerate(args) if value == "--set"])
        validate_sim(cfg.sim, cfg.model.n_experts, cfg.model.top_k)
        tape = load_tape(cfg.sim, cfg.model.n_layers, cfg.model.n_experts, cfg.model.top_k)
        key = (cfg.run.seed, cfg.sim.n_workers)
        seen.add((*key, cfg.sim.round_mode, cfg.sim.q_min))
        resolved = []
        for r in range(cfg.sim.rounds):
            reference = round_slices(cfg.sim, cfg.model.n_layers, 8, 2, r, cfg.run.seed)
            timing = timed_round(cfg.sim, tape, cfg.run.seed, r, reference, 8)
            assert all(count == 2 for counts in timing["nominal_holders"].values() for count in counts)
            resolved.extend(timing["interventions"])
        if key in interventions:
            assert resolved == interventions[key]
        interventions[key] = resolved
        assert [event["remaining"] for event in resolved] == [1, 0]
    assert seen == {(seed, n, mode, q) for seed in (7, 11, 19) for n in (3, 4, 5)
                    for mode, q in (("deadline", 1), ("deadline", 2), ("synchronous", 1), ("centralized", 1))}
