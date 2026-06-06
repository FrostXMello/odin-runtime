from __future__ import annotations


def score(*, sessions: int) -> float:
    return min(1.0, sessions / 50.0)
