from __future__ import annotations


def breakdown(goal: str) -> list[dict]:
    return [{"title": f"{goal[:40]} — stage {i}", "stage": i} for i in range(1, 4)]
