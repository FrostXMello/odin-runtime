"""Heal blocked dependency chains."""

from __future__ import annotations

from typing import Any

from odin_backend.models.task_graph import TaskNodeStatus


def heal_dependencies(task_graph: Any) -> list[str]:
    healed: list[str] = []
    for node_id, node in getattr(task_graph, "nodes", {}).items():
        if node.status != TaskNodeStatus.BLOCKED:
            continue
        deps = node.dependencies or []
        if not deps:
            task_graph.update_status(node_id, TaskNodeStatus.READY, reason="dependency_heal")
            healed.append(node_id)
    return healed
