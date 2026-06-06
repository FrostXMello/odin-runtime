from __future__ import annotations


def predict_idle(*, idle_s: float) -> bool:
    return idle_s > 45
