"""Personal knowledge graph."""

from __future__ import annotations

from typing import Any


class PersonalKnowledgeGraph:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}

    def add_node(self, node_id: str, *, label: str, kind: str) -> dict[str, Any]:
        node = {"id": node_id, "label": label, "kind": kind}
        self._nodes[node_id] = node
        return node

    def snapshot(self) -> dict[str, Any]:
        return {"nodes": len(self._nodes), "sample": list(self._nodes.values())[-10:]}
