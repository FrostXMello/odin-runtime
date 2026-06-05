"""Task graph — all work is a graph, not a queue."""

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskNodeStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    # Legacy alias
    RUNNING = "running"


class TaskNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str
    dependencies: list[str] = Field(default_factory=list)
    assigned_agent: str | None = None
    status: TaskNodeStatus = TaskNodeStatus.PENDING
    priority: int = 50
    input_signals: list[str] = Field(default_factory=list)
    output: dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0

    def is_ready(self, completed: set[str]) -> bool:
        if self.status not in (TaskNodeStatus.PENDING, TaskNodeStatus.READY):
            return False
        return all(dep in completed for dep in self.dependencies)

    def is_executable(self) -> bool:
        return self.status in (
            TaskNodeStatus.READY,
            TaskNodeStatus.ASSIGNED,
            TaskNodeStatus.PENDING,
            TaskNodeStatus.RUNNING,
        )


class TaskGraph(BaseModel):
    """Kernel-owned execution graph."""

    nodes: dict[str, TaskNode] = Field(default_factory=dict)

    def add_node(self, node: TaskNode) -> TaskNode:
        self.nodes[node.id] = node
        return node

    def get(self, node_id: str) -> TaskNode | None:
        return self.nodes.get(node_id)

    def update_status(
        self,
        node_id: str,
        status: TaskNodeStatus,
        *,
        output: dict[str, Any] | None = None,
        reason: str = "",
        strict: bool = True,
    ) -> TaskNode | None:
        node = self.nodes.get(node_id)
        if not node:
            return None
        if strict:
            from odin_backend.core.missions.lifecycle import TaskStateMachine

            TaskStateMachine.transition(node, status, reason=reason or "update_status")
        else:
            node.status = status
        if output is not None:
            node.output.update(output)
        return node

    def ready_nodes(self) -> list[TaskNode]:
        completed = {
            nid
            for nid, n in self.nodes.items()
            if n.status in (TaskNodeStatus.COMPLETE, TaskNodeStatus.SKIPPED)
        }
        ready: list[TaskNode] = []
        for n in self.nodes.values():
            if n.is_ready(completed):
                if n.status == TaskNodeStatus.PENDING:
                    n.status = TaskNodeStatus.READY
                ready.append(n)
        return ready

    def snapshot(self) -> dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "nodes": {k: v.model_dump(mode="json") for k, v in self.nodes.items()},
            "ready": [n.id for n in self.ready_nodes()],
        }
