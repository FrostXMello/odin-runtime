"""Adaptive batching."""

from __future__ import annotations


def batch_size(*, mode: str, ram_mb: int) -> int:
    if mode in ("ultra_light", "overnight"):
        return 1
    if ram_mb <= 16384:
        return 2
    return 4
