"""Self-reasoning — refine TaskGraph without bypassing kernel."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus


class PlanningReport(BaseModel):
    actions: list[str] = Field(default_factory=list)
    priority_adjustments: dict[str, int] = Field(default_factory=dict)
    new_nodes: list[TaskNode] = Field(default_factory=list)
    merged_node_ids: list[str] = Field(default_factory=list)


class SelfReasoningPlanner:
    """Proactive planning: refine, split, merge, reprioritize."""

    def refine(self, task_graph: TaskGraph, *, focus: str = "") -> PlanningReport:
        report = PlanningReport()
        goals: dict[str, list[str]] = {}

        for node_id, node in task_graph.nodes.items():
            key = node.goal.strip().lower()[:120]
            goals.setdefault(key, []).append(node_id)

        for _goal, ids in goals.items():
            if len(ids) > 1:
                report.actions.append(f"merge_duplicate_goals:{ids[0]}")
                report.merged_node_ids.extend(ids[1:])
                for dup_id in ids[1:]:
                    dup = task_graph.get(dup_id)
                    if dup and dup.status in (TaskNodeStatus.PENDING, TaskNodeStatus.READY):
                        task_graph.update_status(dup_id, TaskNodeStatus.BLOCKED)
                        report.actions.append(f"blocked_duplicate:{dup_id}")

        for node in task_graph.nodes.values():
            if node.status != TaskNodeStatus.PENDING:
                continue
            if len(node.goal) > 160 and not node.dependencies:
                report.actions.append(f"split_complex_task:{node.id}")
                sub = TaskNode(
                    goal=f"Plan: {node.goal[:80]}",
                    dependencies=[node.id],
                    assigned_agent=node.assigned_agent,
                    priority=max(10, node.priority - 5),
                    status=TaskNodeStatus.PENDING,
                )
                report.new_nodes.append(sub)
            if focus and focus.lower() not in node.goal.lower() and node.priority < 80:
                report.priority_adjustments[node.id] = min(100, node.priority + 10)

        pending = [n for n in task_graph.nodes.values() if n.status == TaskNodeStatus.PENDING]
        if len(pending) > 8:
            report.actions.append("reprioritize_backlog")
            for n in sorted(pending, key=lambda x: x.priority, reverse=True)[8:]:
                report.priority_adjustments[n.id] = max(1, n.priority - 15)

        return report
