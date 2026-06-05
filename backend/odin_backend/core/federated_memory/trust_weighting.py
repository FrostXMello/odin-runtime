"""Trust-weighted memory scoring."""

from __future__ import annotations


def weight_by_trust(*, value: float, trust: float, source_count: int = 1) -> float:
    source_factor = min(1.0, source_count * 0.15)
    return round(value * trust * (0.5 + 0.5 * source_factor), 4)
