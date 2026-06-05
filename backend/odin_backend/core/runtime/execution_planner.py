"""Enrich mission task graphs with execution contracts and dependency metadata."""

from __future__ import annotations

from typing import Any

from odin_backend.core.runtime.task_contracts import TaskContractType
from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus


class MissionExecutionPlanner:
    """Assigns execution contracts to tasks that would otherwise noop."""

    def enrich_mission(self, mission: Mission) -> int:
        updated = 0
        for node in mission.task_graph.nodes.values():
            if self._enrich_node(node, mission):
                updated += 1
        return updated

    def _enrich_node(self, node: TaskNode, mission: Mission) -> bool:
        out = node.output
        if out.get("type") in ("execution", "shell", "workflow"):
            return False
        if out.get("capability") or out.get("code"):
            out.setdefault("type", "execution")
            return True

        if out.get("tool") not in (None, "", "noop"):
            return False

        if node.status in (TaskNodeStatus.COMPLETE, TaskNodeStatus.SKIPPED):
            return False

        step_kind = out.get("step_kind", "")
        if step_kind == "mission_step" or "Execute" in node.goal or "execute" in node.goal.lower():
            out.update(
                {
                    "type": "execution",
                    "capability": "python.safe",
                    "params": {"code": f"print({repr(node.goal[:100])})"},
                    "parallelizable": True,
                    "blocking": True,
                }
            )
            return True

        if "Verify" in node.goal or "verify" in node.goal.lower():
            out.update(
                {
                    "type": "internal_api",
                    "params": {"action": "verify", "goal": node.goal[:200]},
                }
            )
            return True

        if mission.execution_strategy == "sandbox_only":
            out.update(
                {
                    "type": "execution",
                    "capability": "python.safe",
                    "params": {"code": f"print({repr(node.goal[:80])})"},
                }
            )
            return True

        return False

    def sync_dependencies(self, mission: Mission) -> None:
        """Merge depends_on from task output into graph dependencies."""
        for node in mission.task_graph.nodes.values():
            extra = node.output.get("depends_on") or []
            if not extra:
                continue
            merged = list(dict.fromkeys([*node.dependencies, *extra]))
            node.dependencies = merged

    def dependency_snapshot(self, mission: Mission) -> dict[str, Any]:
        nodes = []
        for n in mission.task_graph.nodes.values():
            nodes.append(
                {
                    "task_id": n.id,
                    "status": n.status.value,
                    "depends_on": n.dependencies,
                    "blocking": n.output.get("blocking", True),
                    "parallelizable": n.output.get("parallelizable", True),
                    "execution_id": n.output.get("execution_id"),
                }
            )
        return {
            "mission_id": mission.mission_id,
            "ready": [n.id for n in mission.task_graph.ready_nodes()],
            "nodes": nodes,
        }
