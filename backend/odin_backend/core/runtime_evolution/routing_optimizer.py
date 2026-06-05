"""Routing heuristic optimization."""

from __future__ import annotations

from typing import Any


def optimize_routing(*, latency_ms: float, success: float) -> dict[str, Any]:
    weight = min(1.0, max(0.2, success - latency_ms / 10000))
    return {"routing_weight": round(weight, 4), "optimized": True}
