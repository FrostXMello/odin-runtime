from __future__ import annotations

def graph(*, nodes: list[str]) -> dict:
    return {"nodes": nodes, "edges": max(0, len(nodes) - 1)}
