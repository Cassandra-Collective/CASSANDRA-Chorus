"""Task B: text8 at character level (SRS S0-F-19).

text8 is 100,000,000 characters of cleaned lowercase Wikipedia over 27 symbols
(a to z and space), with the conventional split: train the first 90M,
validation the next 5M, test the last 5M. The file is read from the data
folder (``cassandra_chorus.paths.data_root``) and refused unless its SHA-256
matches the configuration, so a run's corpus is fixed by its configuration.

Training windows start at uniformly random offsets (with replacement) inside
the train split. Evaluation windows tile a split without overlap, and the
context is reset at each window, the parent CASSANDRA project's protocol.
See docs/implementations/2026-10-09-task-b-data-and-timing-pilot.md.
"""

from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path

import torch

from cassandra_chorus.paths import data_root

ALPHABET = " abcdefghijklmnopqrstuvwxyz"  # id = index: space 0, a 1, ..., z 26
TEXT8_SHA256 = "6e890197040d37d85beb962ae1f041ff1d9a9ca8d20c7d99c85027eebf51dca7"  # measured 2026-10-09
SPLITS = ("train", "valid", "test")


@dataclasses.dataclass(frozen=True)
class Text8Section:
    """Task B data configuration (the ``[text8]`` section).

    ``file`` is relative to the data folder. Split bounds are character offsets;
    the defaults are the conventional text8 split.
    """

    file: str = "text8/text8"
    sha256: str = TEXT8_SHA256
    context_length: int = 256
    train_end: int = 90_000_000
    valid_end: int = 95_000_000
    total: int = 100_000_000


class Text8:
    """The encoded corpus (a uint8 tensor of ids) and window sampling from its splits."""

    def __init__(self, cfg: Text8Section, data_dir: Path | None = None) -> None:
        if not 0 < cfg.train_end < cfg.valid_end < cfg.total:
            raise ValueError("text8 split bounds must satisfy 0 < train_end < valid_end < total")
        if cfg.context_length < 1:
            raise ValueError("text8 context_length must be positive")
        path = (data_dir or data_root()) / cfg.file
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != cfg.sha256:
            raise ValueError(f"{path}: SHA-256 is {digest}, the configuration expects {cfg.sha256}")
        if len(raw) != cfg.total:
            raise ValueError(f"{path}: {len(raw)} characters, the configuration expects {cfg.total}")
        lut = torch.full((256,), 255, dtype=torch.uint8)
        for i, ch in enumerate(ALPHABET):
            lut[ord(ch)] = i
        ids = lut[torch.frombuffer(bytearray(raw), dtype=torch.uint8).long()]
        if bool((ids == 255).any()):
            raise ValueError(f"{path}: characters outside the 27-symbol alphabet")
        self.cfg = cfg
        self.path = path
        self.data = ids
        self.vocab_size = len(ALPHABET)

    def bounds(self, split: str) -> tuple[int, int]:
        """Character offsets [start, end) of a split."""
        if split == "train":
            return 0, self.cfg.train_end
        if split == "valid":
            return self.cfg.train_end, self.cfg.valid_end
        if split == "test":
            return self.cfg.valid_end, self.cfg.total
        raise ValueError(f"unknown split {split!r}; expected one of {SPLITS}")

    def sample(self, batch_size: int, generator: torch.Generator, split: str = "train") -> tuple[torch.Tensor, torch.Tensor]:
        """``batch_size`` random windows: inputs and next-character targets, ``[B, L]`` int64 on the CPU."""
        start, end = self.bounds(split)
        length = self.cfg.context_length
        starts = torch.randint(start, end - length, (batch_size,), generator=generator)
        windows = self.data[starts.unsqueeze(1) + torch.arange(length + 1)].long()
        return windows[:, :-1], windows[:, 1:]

    def n_windows(self, split: str, max_chars: int | None = None) -> int:
        """Non-overlapping evaluation windows in a split, or in its first ``max_chars`` characters."""
        start, end = self.bounds(split)
        if max_chars is not None:
            end = min(end, start + max_chars)
        return (end - start - 1) // self.cfg.context_length

    def eval_windows(self, split: str, first: int, count: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Evaluation windows ``first`` to ``first + count - 1``: window w reads characters
        start + wL to start + wL + L - 1 and predicts the L characters one place later."""
        start, _ = self.bounds(split)
        length = self.cfg.context_length
        offsets = start + (first + torch.arange(count)).unsqueeze(1) * length
        windows = self.data[offsets + torch.arange(length + 1)].long()
        return windows[:, :-1], windows[:, 1:]

    def strided_windows(self, split: str, first: int, count: int, stride: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Windows ``first`` to ``first + count - 1`` starting every ``stride`` characters: window w reads
        characters start + w*stride to start + w*stride + L - 1 and predicts the L characters one place later.
        With ``stride = L`` these are exactly :meth:`eval_windows`."""
        start, _ = self.bounds(split)
        length = self.cfg.context_length
        offsets = start + (first + torch.arange(count)).unsqueeze(1) * stride
        windows = self.data[offsets + torch.arange(length + 1)].long()
        return windows[:, :-1], windows[:, 1:]
