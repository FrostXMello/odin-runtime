"""Interaction energy tracking."""
from __future__ import annotations

def track_energy(*, events: int, duration_s: float) -> float:
    rate = events / max(duration_s, 1.0)
    return min(1.0, rate / 5.0)
