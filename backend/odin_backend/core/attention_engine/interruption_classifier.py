from __future__ import annotations


def classify(*, intensity: float) -> str:
    if intensity > 0.7:
        return "high"
    if intensity > 0.4:
        return "medium"
    return "low"
