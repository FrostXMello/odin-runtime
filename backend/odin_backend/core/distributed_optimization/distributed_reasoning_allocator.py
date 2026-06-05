"""Distributed reasoning placement."""

from __future__ import annotations

from typing import Any


def allocate(nodes: list[dict], *, query_cost: float = 1.0) -> dict[str, Any]:
    if not nodes:
        return {"node_id": None, "reason": "no_nodes"}
    best = min(nodes, key=lambda n: n.get("latency_ms", 100) + (1 - n.get("trust_level", 0.5)) * 50)
    return {"node_id": best.get("node_id"), "latency_ms": best.get("latency_ms", 0)}
