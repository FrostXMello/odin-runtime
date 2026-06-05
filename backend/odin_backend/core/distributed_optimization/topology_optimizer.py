"""Federation topology optimization."""

from __future__ import annotations

from typing import Any


def optimize_topology(*, edge_count: int, node_count: int) -> dict[str, Any]:
    density = edge_count / max(node_count * (node_count - 1) / 2, 1)
    return {"density": round(density, 4), "recommendation": "add_links" if density < 0.3 else "stable"}
