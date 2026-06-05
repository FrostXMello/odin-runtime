"""Confidence decay for stale or failed memory."""

from __future__ import annotations

from datetime import datetime, timezone


def decay_confidence(
    confidence: float,
    *,
    age_seconds: float,
    half_life_seconds: float = 86400.0 * 7,
    failure_penalty: float = 0.0,
) -> float:
    if half_life_seconds <= 0:
        return confidence
    import math

    factor = math.exp(-0.693 * age_seconds / half_life_seconds)
    value = confidence * factor - failure_penalty
    return max(0.05, min(0.99, value))


def decay_weight(weight: float, *, failures: int = 0) -> float:
    return max(0.01, weight * (0.9 ** failures))
