"""Node specialization recommendations."""

from __future__ import annotations

from typing import Any


def recommend(nodes: list[dict]) -> list[dict[str, Any]]:
    return [{"node_id": n.get("node_id"), "specialization": n.get("role", "worker")} for n in nodes]
