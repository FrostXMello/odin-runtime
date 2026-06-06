from __future__ import annotations

def decay(*, weight: float, age_h: float) -> float:
    return max(0.0, weight - age_h * 0.01)
