from __future__ import annotations


def graph(*, goals: list[str]) -> dict:
    return {"nodes": len(goals), "edges": max(0, len(goals) - 1), "depth_limit": 8}
