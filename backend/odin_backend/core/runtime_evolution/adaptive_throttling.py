"""Adaptive throttling based on load."""

from __future__ import annotations


def throttle_factor(*, load: float, max_load: float = 1.0) -> float:
    if load >= max_load:
        return 0.5
    return round(1.0 - load * 0.3, 4)
