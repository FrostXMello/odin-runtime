"""Agent collaboration graph."""

from __future__ import annotations

from typing import Any


class CollaborationGraph:
    def __init__(self) -> None:
        self._edges: dict[str, set[str]] = {}

    def link(self, a: str, b: str) -> None:
        self._edges.setdefault(a, set()).add(b)
        self._edges.setdefault(b, set()).add(a)

    def neighbors(self, agent_id: str) -> list[str]:
        return sorted(self._edges.get(agent_id, set()))

    def snapshot(self) -> dict[str, Any]:
        return {"nodes": list(self._edges.keys()), "edge_count": sum(len(v) for v in self._edges.values()) // 2}
