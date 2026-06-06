from __future__ import annotations

def graph(*, decisions: list[str]) -> dict:
    return {"nodes": decisions[:8], "edges": max(0, len(decisions) - 1)}
