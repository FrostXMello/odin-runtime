from __future__ import annotations


def prune(*, age_days: int) -> dict:
    return {"pruned": age_days > 30, "bounded": True}
