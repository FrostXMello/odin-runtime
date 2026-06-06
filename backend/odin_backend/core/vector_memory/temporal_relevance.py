"""Temporal relevance weighting."""

from __future__ import annotations

from typing import Any


def temporal_weight(*, age_hours: float, importance: float = 0.5) -> float:
    decay = max(0.1, 1.0 - (age_hours / (24 * 30)))
    return round(decay * 0.6 + importance * 0.4, 4)
