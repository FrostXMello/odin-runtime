from __future__ import annotations


def safe_intervene(*, score: float) -> bool:
    return score > 0.55
