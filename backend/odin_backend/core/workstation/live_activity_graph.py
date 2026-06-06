from __future__ import annotations

from typing import Any


class ActivityGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, float] = {}

    def add_node(self, *, app: str, weight: float) -> None:
        self._nodes[app] = max(self._nodes.get(app, 0), weight)

    def nodes(self) -> list[str]:
        return list(self._nodes.keys())

    def snapshot(self) -> dict[str, Any]:
        return {"nodes": len(self._nodes), "top": max(self._nodes, key=self._nodes.get) if self._nodes else None}
