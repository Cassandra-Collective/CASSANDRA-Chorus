from __future__ import annotations

import hashlib
import math
import types

import pytest
import torch

from cassandra_chorus.data.text8 import ALPHABET, Text8, Text8Section
from cassandra_chorus.metrics.task_b import evaluate_bpc

TEXT = ("the quick brown fox jumps over the lazy dog " * 30)[:1000]  # 1,000 characters, 27-symbol alphabet


def corpus(tmp_path, text=TEXT, **overrides):
    (tmp_path / "text8").mkdir(exist_ok=True)
    (tmp_path / "text8" / "text8").write_bytes(text.encode("ascii"))
    cfg = dict(sha256=hashlib.sha256(text.encode("ascii")).hexdigest(), context_length=16,
               train_end=800, valid_end=900, total=len(text))
    cfg.update(overrides)
    return Text8(Text8Section(**cfg), data_dir=tmp_path)


def test_encoding_and_bounds(tmp_path):
    data = corpus(tmp_path)
    assert data.vocab_size == 27
    assert "".join(ALPHABET[i] for i in data.data[:9].tolist()) == "the quick"
    assert data.bounds("train") == (0, 800) and data.bounds("valid") == (800, 900) and data.bounds("test") == (900, 1000)
    with pytest.raises(ValueError, match="unknown split"):
        data.bounds("dev")


def test_refuses_wrong_hash_size_or_alphabet(tmp_path):
    with pytest.raises(ValueError, match="SHA-256"):
        corpus(tmp_path, sha256="0" * 64)
    with pytest.raises(ValueError, match="characters, the configuration expects"):
        corpus(tmp_path, total=999)
    bad = TEXT[:-1] + "!"
    with pytest.raises(ValueError, match="outside the 27-symbol alphabet"):
        corpus(tmp_path, text=bad)


def test_training_windows_are_shifted_and_inside_train(tmp_path):
    data = corpus(tmp_path)
    inputs, targets = data.sample(500, torch.Generator().manual_seed(7))
    assert inputs.shape == targets.shape == (500, 16) and inputs.dtype == torch.int64
    assert torch.equal(inputs[:, 1:], targets[:, :-1])  # targets are the inputs one place later
    flat = data.data.long()
    for row in range(0, 500, 50):  # every window is a contiguous piece of the train split
        s = next(i for i in range(0, 800 - 16) if torch.equal(flat[i:i + 16], inputs[row]) and torch.equal(flat[i + 1:i + 17], targets[row]))
        assert s + 16 < 800


def test_sampling_is_reproducible(tmp_path):
    data = corpus(tmp_path)
    a = data.sample(8, torch.Generator().manual_seed(11))
    b = data.sample(8, torch.Generator().manual_seed(11))
    assert torch.equal(a[0], b[0]) and torch.equal(a[1], b[1])


def test_eval_windows_tile_the_split(tmp_path):
    data = corpus(tmp_path)
    n = data.n_windows("test")
    assert n == (100 - 1) // 16 == 6
    inputs, targets = data.eval_windows("test", 0, n)
    assert torch.equal(targets.reshape(-1), data.data[901:901 + 16 * n].long())  # every scored character once
    assert torch.equal(inputs.reshape(-1), data.data[900:900 + 16 * n].long())
    assert data.n_windows("valid", max_chars=50) == (50 - 1) // 16


class Uniform(torch.nn.Module):
    def forward(self, x):
        return types.SimpleNamespace(logits=torch.zeros(*x.shape, 27))


class Oracle(torch.nn.Module):
    """Puts almost all probability on the true next character (it peeks at the corpus)."""

    def __init__(self, data):
        super().__init__()
        self.data = data

    def forward(self, x):
        nxt = {}
        flat = self.data.data.long()
        logits = torch.full((*x.shape, 27), -30.0)
        for b in range(x.shape[0]):
            s = next(i for i in range(len(flat) - x.shape[1]) if torch.equal(flat[i:i + x.shape[1]], x[b]))
            logits[b, torch.arange(x.shape[1]), flat[s + 1:s + 1 + x.shape[1]]] = 30.0
        return types.SimpleNamespace(logits=logits)


def test_bpc_of_uniform_and_oracle_models(tmp_path):
    data = corpus(tmp_path)
    uniform = evaluate_bpc(Uniform(), data, "test", "cpu", batch_windows=4)
    assert uniform["bpc"] == pytest.approx(math.log2(27)) and uniform["scored"] == 6 * 16 and uniform["windows"] == 6
    assert evaluate_bpc(Oracle(data), data, "test", "cpu")["bpc"] < 1e-6
