from __future__ import annotations
from typing import Any

def build_graph(*, nodes: list[str]) -> dict[str, Any]:
    edges = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]
    return {"nodes": nodes, "edges": edges}
