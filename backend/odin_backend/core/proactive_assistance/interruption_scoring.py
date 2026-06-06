from __future__ import annotations


def score(*, urgency: float, operator_busy: bool) -> float:
    if operator_busy:
        return urgency * 0.3
    return urgency
