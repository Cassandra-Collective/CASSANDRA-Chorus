"""Canonical tensor, part, and model hashes (architecture section 7.2, issue #62)."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Iterator, Mapping

import pytest
import torch

from cassandra_chorus.coordinator import canonical_hash, model_hash, part_hashes, split_state, tensor_bytes
from cassandra_chorus.model import ModelSection, MoETransformer, expert_param_owner, router_param_layer

CFG = ModelSection(vocab_size=11, context_length=8, d_model=16, n_layers=2, n_heads=2, expert_hidden=8, n_experts=4)

# Captured with scripts.proto.common.canonical_hash before moving its code.
GOLDEN_DIGESTS = (
    "e082cbae4f221a95d74bcfc55a915e8f874a2cd03ffb8cd01379d909055e1c94",
    "fc61228b9a6472cd64e433355a1a8763ef0d1479312369577861a8e374d01ec0",
    "3339744837d70f472657890d07ca30bdccc6a92d511c174148e1534d18fc1aa0",
)


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


class GeneratedState(Mapping[str, torch.Tensor]):
    """Build each tensor through ``fetch`` on access, without caching values."""

    def __init__(self, names: Iterable[str], fetch: Callable[[str], torch.Tensor]):
        self.names = tuple(names)
        self.fetch = fetch

    def __getitem__(self, name: str) -> torch.Tensor:
        if name not in self.names:
            raise KeyError(name)
        return self.fetch(name)

    def __iter__(self) -> Iterator[str]:
        return iter(self.names)

    def __len__(self) -> int:
        return len(self.names)


@pytest.fixture
def state():
    torch.manual_seed(0)
    return {name: t.clone() for name, t in MoETransformer(CFG).state_dict().items()}


@pytest.mark.parametrize("index", range(3))
def test_pre_move_golden_digests(index):
    assert canonical_hash(golden_states()[index]) == GOLDEN_DIGESTS[index]


def test_prototype_reexports_the_package_definitions():
    from scripts.proto import common

    assert common.canonical_hash is canonical_hash
    assert common.tensor_bytes is tensor_bytes


def test_hash_ignores_insertion_order_and_reads_lazy_tensors_once(state):
    reads = []

    def fetch(name):
        reads.append(name)
        return state[name].clone()

    lazy = GeneratedState(reversed(state), fetch)
    reordered = dict(reversed(list(state.items())))
    assert canonical_hash(state) == canonical_hash(reordered) == canonical_hash(lazy)
    assert reads == sorted(state)


@pytest.mark.parametrize("change", ["bit", "dtype", "shape", "name"])
def test_hash_sees_one_bit_dtype_shape_and_name(state, change):
    changed = dict(state)
    name = "embed.weight"
    if change == "bit":
        bits = state[name].clone().view(torch.int32)
        bits[0, 0] ^= 1
        changed[name] = bits.view(torch.float32)
    elif change == "dtype":
        changed[name] = state[name].view(torch.int32)
        assert tensor_bytes(changed[name]) == tensor_bytes(state[name])
    elif change == "shape":
        changed[name] = state[name].reshape(-1)
        assert tensor_bytes(changed[name]) == tensor_bytes(state[name])
    else:
        changed["renamed.weight"] = changed.pop(name)
    assert canonical_hash(changed) != canonical_hash(state)


def test_negative_zero_differs_from_positive_zero():
    assert canonical_hash({"x": torch.tensor([-0.0])}) != canonical_hash({"x": torch.tensor([0.0])})


@pytest.mark.parametrize("dtype", [torch.float32, torch.float64, torch.float16, torch.bfloat16, torch.int64])
def test_hash_ignores_strides_and_gradient_tracking(dtype):
    t = torch.arange(12).to(dtype).reshape(3, 4).T
    if t.is_floating_point():
        t.requires_grad_()
    assert not t.is_contiguous()
    assert canonical_hash({"x": t}) == canonical_hash({"x": t.detach().contiguous()})


def test_parts_use_real_names_and_router_rows(state):
    parts = split_state(state, state)
    expected_ids = {"shared"} | {f"L{l}.E{e}" for l in range(CFG.n_layers) for e in range(CFG.n_experts)}
    assert set(parts) == expected_ids
    assert list(parts) == sorted(expected_ids)
    expected_shared = {n for n in state if expert_param_owner(n) is None and router_param_layer(n) is None}
    assert set(parts["shared"]) == expected_shared
    for layer in range(CFG.n_layers):
        router = f"blocks.{layer}.moe.router.weight"
        for expert in range(CFG.n_experts):
            part_id = f"L{layer}.E{expert}"
            row_name = f"{router}[{expert}]"
            expert_names = {n for n in state if expert_param_owner(n) == (layer, expert)}
            assert set(parts[part_id]) == expert_names | {row_name}
            assert parts[part_id][row_name].shape == (CFG.d_model,)
            assert torch.equal(parts[part_id][row_name], state[router][expert])
            for name in expert_names:
                assert parts[part_id][name] is state[name]
    assert part_hashes(state, state) == {p: canonical_hash(tensors) for p, tensors in parts.items()}


def test_part_ids_use_string_order():
    state = {"blocks.0.moe.router.weight": torch.zeros(11, 1)}
    state.update({f"blocks.0.moe.experts.{e}.w1.weight": torch.tensor([e]) for e in range(11)})
    ids = list(part_hashes(state, state))
    assert ids == sorted(ids)
    assert ids.index("L0.E10") < ids.index("L0.E2")


@pytest.mark.parametrize(
    ("name", "row", "part_id"),
    [
        ("blocks.0.moe.experts.2.w1.weight", None, "L0.E2"),
        ("blocks.1.moe.router.weight", 1, "L1.E1"),
        ("embed.weight", None, "shared"),
    ],
)
def test_changes_are_local_to_one_part_and_change_the_model(state, name, row, part_id):
    before = part_hashes(state, state)
    changed = dict(state)
    changed[name] = state[name].clone()
    target = changed[name] if row is None else changed[name][row]
    target.reshape(-1)[0] += 1.0
    after = part_hashes(changed, state)
    assert {p for p in before if before[p] != after[p]} == {part_id}
    assert model_hash(after) != model_hash(before)


def test_part_hashes_ignore_order_and_laziness(state):
    reordered = dict(reversed(list(state.items())))
    lazy = GeneratedState(reversed(state), lambda name: state[name].clone())
    assert part_hashes(state, state) == part_hashes(reordered, iter(reordered)) == part_hashes(lazy, state)


def test_model_hash_encoding_and_input_order():
    hashes = {"shared": "a" * 64, "L0.E2": "b" * 64, "L0.E10": "c" * 64}
    encoded = b"L0.E10\0" + b"c" * 64 + b"\0L0.E2\0" + b"b" * 64 + b"\0shared\0" + b"a" * 64 + b"\0"
    expected = hashlib.sha256(encoded).hexdigest()
    assert model_hash(hashes) == model_hash(dict(reversed(list(hashes.items())))) == expected
    assert model_hash({"shared": "a" * 64}) != model_hash({"L0.E0": "a" * 64})
    assert model_hash({}) == hashlib.sha256(b"").hexdigest()


def test_slice_hashes_match_the_full_state(state):
    held = {0: {0, 2}, 1: {1, 3}}
    slice_names = MoETransformer(CFG, held).state_dict()
    sliced = {name: state[name].clone() for name in slice_names}
    full_hashes = part_hashes(state, state)
    sliced_hashes = part_hashes(sliced, state)
    expected_parts = {"shared", "L0.E0", "L0.E2", "L1.E1", "L1.E3"}
    assert set(sliced_hashes) == expected_parts
    assert sliced_hashes == {p: full_hashes[p] for p in sorted(expected_parts)}
    # Unheld router rows do not enter a slice's hashes.
    sliced["blocks.0.moe.router.weight"][1] += 1
    assert part_hashes(sliced, state) == sliced_hashes


@pytest.mark.parametrize("function", [split_state, part_hashes])
@pytest.mark.parametrize(
    ("missing", "part_id"),
    [
        ("embed.weight", "shared"),
        ("blocks.0.moe.experts.1.w1.weight", "L0.E1"),
        ("blocks.0.moe.router.weight", "L0.E"),
    ],
)
def test_incomplete_parts_raise(state, function, missing, part_id):
    partial = dict(state)
    del partial[missing]
    with pytest.raises(ValueError, match=f"incomplete part {part_id}"):
        function(partial, state)


def test_absent_shared_and_experts_are_omitted(state):
    router_name = "blocks.1.moe.router.weight"
    only_expert = {n: t for n, t in state.items() if expert_param_owner(n) == (1, 2) or n == router_name}
    assert part_hashes(only_expert, state) == {"L1.E2": part_hashes(state, state)["L1.E2"]}
    assert split_state({}, state) == {}
    assert split_state({}, []) == {"shared": {}}


@pytest.mark.parametrize("shape", [(4,), (3, 16), (4, 0), (4, 16, 1)])
def test_invalid_router_shapes_raise(state, shape):
    changed = {**state, "blocks.0.moe.router.weight": torch.zeros(shape)}
    with pytest.raises(ValueError, match="expected router shape"):
        part_hashes(changed, state)


def test_unexpected_parameter_raises(state):
    with pytest.raises(ValueError, match="unexpected parameter names"):
        part_hashes({**state, "extra.weight": torch.zeros(1)}, state)


@pytest.mark.parametrize("problem", ["missing_router", "missing_experts", "noncontiguous_experts"])
def test_invalid_full_inventory_raises(state, problem):
    if problem == "missing_router":
        names = [n for n in state if n != "blocks.0.moe.router.weight"]
    elif problem == "missing_experts":
        names = [n for n in state if (expert_param_owner(n) or (-1, -1))[0] != 0]
    else:
        names = [n for n in state if expert_param_owner(n) != (0, 0)]
    with pytest.raises(ValueError, match="inventory"):
        split_state({}, names)


@pytest.mark.parametrize("part_id", ["", "shared\0extra"])
def test_model_hash_rejects_invalid_ids(part_id):
    with pytest.raises(ValueError, match="part IDs"):
        model_hash({part_id: "a" * 64})


@pytest.mark.parametrize("digest", ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64, "a" * 63 + "\0"])
def test_model_hash_rejects_invalid_digests(digest):
    with pytest.raises(ValueError, match="64 lowercase hex"):
        model_hash({"shared": digest})


def test_hashing_does_not_mutate_inputs_or_consume_randomness(state):
    state["embed.weight"].requires_grad_()
    snapshot = {n: tensor_bytes(t) for n, t in state.items()}
    rng = torch.get_rng_state().clone()
    hashes = part_hashes(state, state)
    hashes_before = dict(hashes)
    model_hash(hashes)
    canonical_hash(state)
    assert snapshot == {n: tensor_bytes(t) for n, t in state.items()}
    assert state["embed.weight"].requires_grad
    assert hashes == hashes_before
    assert torch.equal(rng, torch.get_rng_state())


@pytest.mark.gpu
@pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA GPU")
def test_device_copy_hashes_equal(state):
    cuda = {name: t.cuda() for name, t in state.items()}
    assert canonical_hash(cuda) == canonical_hash(state)
    assert part_hashes(cuda, state) == part_hashes(state, state)
    assert model_hash(part_hashes(cuda, state)) == model_hash(part_hashes(state, state))
