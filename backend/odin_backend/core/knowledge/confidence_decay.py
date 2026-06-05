"""Temporal confidence decay."""

from __future__ import annotations

from datetime import datetime, timezone


def decay_confidence(*, confidence: float, age_days: float, half_life_days: float = 30.0) -> float:
    if age_days <= 0:
        return confidence
    factor = 0.5 ** (age_days / max(half_life_days, 1.0))
    return max(0.05, confidence * factor)


def is_stale(*, updated_at: datetime, stale_days: float = 90.0) -> bool:
    age = (datetime.now(timezone.utc) - updated_at).total_seconds() / 86400.0
    return age > stale_days
