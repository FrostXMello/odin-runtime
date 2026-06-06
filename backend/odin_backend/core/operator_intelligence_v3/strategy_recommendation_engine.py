from __future__ import annotations


def recommend(*, fatigue: bool) -> dict:
    if fatigue:
        return {"strategy": "recovery", "break_minutes": 15}
    return {"strategy": "deep_work", "focus_block_minutes": 45}
