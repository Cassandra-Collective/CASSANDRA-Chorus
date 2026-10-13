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
                 batch_windows: int = 64, stride: int | None = None) -> dict:
    """Bits per character of ``model`` on ``split`` (or its first ``max_chars`` characters).

    Returns ``bpc``, ``nll_nats`` (per character), ``scored``, ``windows`` and, for a
    mixture-of-experts model, ``expert_counts`` (``[layers][E]`` tokens routed to each
    expert over every scored position). No side effects except evaluation mode, which
    is restored afterwards.

    ``stride`` (default: the context length L, the protocol above) selects sliding
    windows instead: ``stride`` must divide L; windows start every ``stride`` characters,
    the first scores all L positions and every later one only its last ``stride``. The
    scored characters are then exactly those of the default protocol, each predicted from
    at least L - stride characters of context (except within the first window). In this
    mode ``expert_counts`` is not returned (unscored positions are routed too) and the
    result carries ``stride``.
    """
    length = data.cfg.context_length
    if stride is not None and stride != length:
        return _evaluate_bpc_strided(model, data, split, device, max_chars, batch_windows, stride)
    was_training = model.training
    model.eval()
    windows = data.n_windows(split, max_chars)
    total_nats, scored, counts = 0.0, 0, None
    for first in range(0, windows, batch_windows):
        count = min(batch_windows, windows - first)
        inputs, targets = data.eval_windows(split, first, count)
        out = model(inputs.to(device))
        logits = out.logits
        layer_counts = getattr(out, "expert_counts", None)
        if layer_counts is not None:
            layer_counts = layer_counts.cpu()
            counts = layer_counts if counts is None else counts + layer_counts
        total_nats += F.cross_entropy(logits.reshape(-1, logits.shape[-1]), targets.to(device).reshape(-1),
                                      reduction="sum").item()
        scored += targets.numel()
    model.train(was_training)
    nll = total_nats / max(scored, 1)
    result = {"bpc": nll / math.log(2), "nll_nats": nll, "scored": scored, "windows": windows}
    if counts is not None:
        result["expert_counts"] = counts.tolist()
    return result


@torch.no_grad()
def _evaluate_bpc_strided(model, data: Text8, split: str, device: torch.device | str, max_chars: int | None,
                          batch_windows: int, stride: int) -> dict:
    """The sliding-window protocol of :func:`evaluate_bpc` (see there)."""
    length = data.cfg.context_length
    if not 0 < stride < length or length % stride:
        raise ValueError(f"stride must divide the context length {length} and be smaller; got {stride}")
    blocks = data.n_windows(split, max_chars)  # the default protocol scores blocks * L characters
    windows = 1 + (blocks - 1) * (length // stride) if blocks else 0
    was_training = model.training
    model.eval()
    total_nats, scored = 0.0, 0
    for first in range(0, windows, batch_windows):
        count = min(batch_windows, windows - first)
        inputs, targets = data.strided_windows(split, first, count, stride)
        logits = model(inputs.to(device)).logits
        nll = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), targets.to(device).reshape(-1),
                              reduction="none").view(count, length)
        mask = torch.zeros(count, length, dtype=torch.bool, device=nll.device)
        mask[:, length - stride:] = True
        if first == 0:
            mask[0, :] = True  # the first window scores all its positions
        total_nats += nll[mask].sum().item()
        scored += int(mask.sum().item())
    model.train(was_training)
    nll_mean = total_nats / max(scored, 1)
    return {"bpc": nll_mean / math.log(2), "nll_nats": nll_mean, "scored": scored, "windows": windows,
            "stride": stride}
