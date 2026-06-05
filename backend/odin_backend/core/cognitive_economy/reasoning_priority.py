"""Reasoning priority scoring."""

from __future__ import annotations


def priority_score(*, urgency: float, value: float, cost: float) -> float:
    return round((urgency * value) / max(cost, 0.1), 4)
