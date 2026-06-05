"""Causal world graph for simulation."""

from __future__ import annotations

from typing import Any


class CausalWorldGraph:
    def __init__(self) -> None:
        self._edges: list[dict[str, Any]] = []

    def add_causal_link(self, *, cause: str, effect: str, strength: float) -> dict[str, Any]:
        edge = {"cause": cause, "effect": effect, "strength": min(1.0, max(0.0, strength))}
        self._edges.append(edge)
        return edge

    def snapshot(self) -> dict[str, Any]:
        return {"edge_count": len(self._edges), "edges": self._edges[-30:]}

    def predict_effect(self, cause: str) -> list[dict[str, Any]]:
        return [e for e in self._edges if e["cause"] == cause]
