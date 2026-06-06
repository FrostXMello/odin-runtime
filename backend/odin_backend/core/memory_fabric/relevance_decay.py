from __future__ import annotations


def decay(*, age_hours: float) -> float:
    return max(0.1, 1.0 - age_hours / 168.0)
