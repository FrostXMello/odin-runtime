from __future__ import annotations

from typing import Any


def map_relationships(*, nodes: list[str]) -> dict[str, Any]:
    return {"nodes": len(nodes), "edges": max(0, len(nodes) - 1)}
