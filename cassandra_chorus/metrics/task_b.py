"""Task B evaluation: bits per character on a text8 split (SRS S0-F-20).

Non-overlapping windows of the context length, context reset per window (the
parent CASSANDRA project's protocol), every character after a window's first
input scored once. bpc = total cross-entropy in nats / (scored characters × ln 2).
See docs/implementations/2026-10-09-task-b-data-and-timing-pilot.md.
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F

from cassandra_chorus.data.text8 import Text8


@torch.no_grad()
def evaluate_bpc(model, data: Text8, split: str, device: torch.device | str, max_chars: int | None = None,
                 batch_windows: int = 64) -> dict:
    """Bits per character of ``model`` on ``split`` (or its first ``max_chars`` characters).

    Returns ``bpc``, ``nll_nats`` (per character), ``scored`` and ``windows``. No side
    effects except evaluation mode, which is restored afterwards.
    """
    was_training = model.training
    model.eval()
    windows = data.n_windows(split, max_chars)
    total_nats, scored = 0.0, 0
    for first in range(0, windows, batch_windows):
        count = min(batch_windows, windows - first)
        inputs, targets = data.eval_windows(split, first, count)
        logits = model(inputs.to(device)).logits
        total_nats += F.cross_entropy(logits.reshape(-1, logits.shape[-1]), targets.to(device).reshape(-1),
                                      reduction="sum").item()
        scored += targets.numel()
    model.train(was_training)
    nll = total_nats / max(scored, 1)
    return {"bpc": nll / math.log(2), "nll_nats": nll, "scored": scored, "windows": windows}
