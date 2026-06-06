from __future__ import annotations


def plan(*, days: int) -> dict:
    return {"horizon_days": min(days, 60), "prune_after_days": 45}
