from __future__ import annotations

from typing import Any


class AttentionGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, float] = {}

    def update(self, *, app: str, weight: float) -> None:
        self._nodes[app] = round(max(self._nodes.get(app, 0), weight), 3)

    def snapshot(self) -> dict[str, Any]:
        top = max(self._nodes, key=self._nodes.get) if self._nodes else None
        return {"nodes": len(self._nodes), "top_focus": top}
