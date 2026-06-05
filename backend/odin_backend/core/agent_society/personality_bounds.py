"""Bounded behavioral trait updates."""

from __future__ import annotations

MAX_DELTA = 0.15


def bounded_update(current: float, delta: float) -> float:
    return max(0.0, min(1.0, current + max(-MAX_DELTA, min(MAX_DELTA, delta))))
