"""Attention visualization metadata."""

from __future__ import annotations

from typing import Any


def visualize_attention(*, nodes: list[dict], focus_id: str | None = None) -> dict[str, Any]:
    highlighted = focus_id or (nodes[0]["id"] if nodes else None)
    return {
        "nodes": nodes,
        "focus_id": highlighted,
        "edge_count": max(0, len(nodes) - 1),
    }
