"""Prototype helpers and P6 at toy scale (docs/implementations/2026-10-14-solo-prototypes.md)."""

from __future__ import annotations

import pytest
import torch

pytest.importorskip("safetensors")

from cassandra_chorus.model.transformer import ModelSection  # noqa: E402
from scripts.proto import p6_merge_determinism as p6  # noqa: E402
from scripts.proto.common import LazyState, bit_diff, canonical_hash, scope_problems  # noqa: E402


def _state() -> dict[str, torch.Tensor]:
    g = torch.Generator().manual_seed(0)
    return {"b.weight": torch.randn(3, 4, generator=g), "a.bias": torch.randn(4, generator=g),
            "c.v": torch.randn(2, generator=g, dtype=torch.float64)}


# --------------------------------------------------------------------------
# canonical_hash and bit_diff


def test_hash_ignores_insertion_order_and_laziness():
    s = _state()
    reordered = {k: s[k] for k in reversed(list(s))}
    lazy = LazyState(list(s), lambda n: s[n].clone())
    assert canonical_hash(s) == canonical_hash(reordered) == canonical_hash(lazy)


def test_hash_sees_one_bit_dtype_shape_and_name():
    s = _state()
    base = canonical_hash(s)
    flipped = dict(s)
    bits = s["a.bias"].clone().view(torch.int32)
    bits[0] ^= 1
    flipped["a.bias"] = bits.view(torch.float32)
    assert canonical_hash(flipped) != base
    assert canonical_hash({**s, "a.bias": s["a.bias"].double()}) != base
    assert canonical_hash({**s, "b.weight": s["b.weight"].reshape(4, 3)}) != base  # same bytes, other shape
    renamed = {("z.bias" if k == "a.bias" else k): v for k, v in s.items()}
    assert canonical_hash(renamed) != base


def test_hash_of_device_copy_is_equal():
    s = _state()
    if torch.cuda.is_available():
        assert canonical_hash({k: v.cuda() for k, v in s.items()}) == canonical_hash(s)


def test_bit_diff():
    s = _state()
    assert bit_diff(s, {k: v.clone() for k, v in s.items()})["bitwise_equal"]
    other = dict(s)
    other["b.weight"] = s["b.weight"] + 1e-3
    d = bit_diff(s, other)
    assert not d["bitwise_equal"] and d["tensors_differing"] == 1 and d["elements_differing"] == 12
    assert d["max_abs"] == pytest.approx(1e-3, rel=1e-3)
    with pytest.raises(ValueError):
        bit_diff(s, {**s, "b.weight": s["b.weight"].double()})


def test_negative_zero_differs_bitwise():
    a = {"x": torch.tensor([0.0])}
    b = {"x": torch.tensor([-0.0])}
    assert not bit_diff(a, b)["bitwise_equal"]
    assert canonical_hash(a) != canonical_hash(b)


# --------------------------------------------------------------------------
# Token guard, on whoami shapes seen 2026-10-14 (no tokens involved)


def _info(scoped, global_=(), role="fineGrained"):
    return {"auth": {"accessToken": {"role": role, "fineGrained": {"scoped": scoped, "global": list(global_)}}}}


def test_guard_accepts_org_only_token():
    info = _info([{"entity": {"type": "org", "name": "cassandra-chorus"}, "permissions": ["repo.contribute.write"]},
                  {"entity": {"type": "user", "name": "someone"}, "permissions": []}])
    assert scope_problems(info, "cassandra-chorus") == []


def test_guard_refuses_broad_tokens():
    personal = _info([{"entity": {"type": "user", "name": "someone"}, "permissions": ["repo.content.read", "repo.write"]}],
                     global_=["discussion.write", "post.write"])
    problems = scope_problems(personal, "cassandra-chorus")
    assert len(problems) == 3  # user write, global write, org missing
    assert scope_problems(_info([{"entity": {"type": "org", "name": "other"}, "permissions": ["repo.write"]}]),
                          "cassandra-chorus")
    assert scope_problems(_info([], role="write"), "cassandra-chorus")


# --------------------------------------------------------------------------
# P6 at toy scale


TINY = ModelSection(vocab_size=27, context_length=16, d_model=16, n_layers=2, n_heads=2, expert_hidden=32,
                    n_experts=8, top_k=2)


def test_p6_tiny_run(tmp_path):
    report = p6.run(TINY, tmp_path / "work", use_cuda=False)
    by_name = {v["name"]: v for v in report["variants"]}
    assert set(by_name) == {v.name for v in p6.variants(False)}
    for kind in p6.EXAMPLES:
        # The same computation twice, and the same inputs from seeds instead of files, are bitwise equal.
        for name in ("baseline-repeat", "in-memory"):
            for label, item in by_name[name]["kinds"][kind].items():
                assert item["against_reference"]["bitwise_equal"], (name, kind, label)
        assert set(by_name["delta-direct-cpu"]["kinds"][kind]) == {"plain-1"}
        assert set(by_name["baseline"]["kinds"][kind]) == set(p6.STATE_LABELS + p6.VELOCITY_LABELS)
    assert "| baseline |" in p6.summary_markdown(report)
    assert not (tmp_path / "work" / "outputs" / "cpu-shuffled").exists()  # non-reference outputs are deleted


@pytest.mark.gpu
@pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA GPU")
def test_p6_true_division_matches_cpu(tmp_path):
    """With the division done by a device tensor, the GPU merge equals the CPU baseline bit for bit."""
    report = p6.run(TINY, tmp_path / "work", use_cuda=True)
    by_name = {v["name"]: v for v in report["variants"]}
    for name in ("cuda-true-division", "cuda-shuffled-true-division"):
        for kind in p6.EXAMPLES:
            for label, item in by_name[name]["kinds"][kind].items():
                assert item["against_reference"]["bitwise_equal"], (name, kind, label)


def test_p9_signing_cases(tmp_path):
    pytest.importorskip("cryptography")
    from scripts.proto import p9_signing_dry_run as p9

    report = p9.run(tmp_path / "work")
    assert report["all_as_expected"], [c for c in report["cases"] if not c["as_expected"]]
    assert [c["accepted"] for c in report["cases"]].count(True) == 1  # only the genuine set


def test_p5_schedule_and_resume():
    from scripts.proto.p5_commit_rate import ROUND_SECONDS, AttemptLog, plan_next, round_steps

    steps = round_steps(2)
    assert steps == ["update/m0", "update/m1", "entry/m0", "entry/m1", "close", "checkpoint"]
    a = plan_next(set(), set(), t0=1000.0, now=1000.0, rounds=10, steps=steps)
    assert (a.kind, a.round_index, a.step, a.gaps) == ("step", 0, "update/m0", ())
    assert plan_next(set(), set(), t0=1000.0, now=900.0, rounds=10, steps=steps).kind == "wait"
    round0 = {(0, s) for s in steps}
    w = plan_next(round0, set(), t0=0.0, now=100.0, rounds=10, steps=steps)
    assert w.kind == "wait" and w.wait_seconds == ROUND_SECONDS - 100
    # The laptop was off for rounds 1 and 2: they become gaps and are never attempted late.
    r = plan_next(round0, set(), t0=0.0, now=3 * ROUND_SECONDS + 5, rounds=10, steps=steps)
    assert (r.kind, r.round_index, r.step, r.gaps) == ("step", 3, "update/m0", (1, 2))
    assert plan_next(round0, {1, 2}, t0=0.0, now=3 * ROUND_SECONDS + 5, rounds=10, steps=steps).gaps == ()
    d = plan_next(round0, {1, 2}, t0=0.0, now=10 * ROUND_SECONDS, rounds=10, steps=steps)
    assert d.kind == "done" and d.gaps == tuple(range(3, 10))


def test_p5_attempt_log_round_trip(tmp_path):
    from scripts.proto.p5_commit_rate import AttemptLog

    log = AttemptLog(tmp_path / "a.jsonl")
    log.append({"event": "start", "t0": 5.0})
    log.append({"event": "attempt", "round": 0, "step": "close", "status": 200})
    log.append({"event": "gap", "round": 3})
    again = AttemptLog(tmp_path / "a.jsonl")
    assert again.t0() == 5.0 and again.done() == {(0, "close")} and again.gaps() == {3}


def test_shuffled_order_is_new():
    items = list(range(4))
    s = p6.ordered(items, "shuffled")
    assert sorted(s) == items and s not in (items, items[::-1])
