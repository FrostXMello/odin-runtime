from __future__ import annotations


def score(*, distractions: int, focus_min: int) -> float:
    base = min(1.0, focus_min / 60.0)
    return max(0.0, base - distractions * 0.05)
