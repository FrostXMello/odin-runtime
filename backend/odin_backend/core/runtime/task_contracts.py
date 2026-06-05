"""Task execution contract schemas parsed from task.output."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.task_graph import TaskNode


class TaskContractType(StrEnum):
    EXECUTION = "execution"
    SHELL = "shell"
    WORKFLOW = "workflow"
    INTERNAL_API = "internal_api"
    MEMORY = "memory"
    GRAPH = "graph"
    DIAGNOSTICS = "diagnostics"
    TOOL = "tool"
    NOOP = "noop"


class TaskExecutionContract(BaseModel):
    """Normalized contract for routing a mission task to real work."""

    type: TaskContractType = TaskContractType.NOOP
    capability: str = "api.internal"
    params: dict[str, Any] = Field(default_factory=dict)
    workflow: str | None = None
    tool_name: str | None = None
    timeout_seconds: float | None = None
    depends_on: list[str] = Field(default_factory=list)
    blocking: bool = True
    parallelizable: bool = True
    affinity: str | None = None

    @property
    def uses_execution_engine(self) -> bool:
        return self.type in (
            TaskContractType.EXECUTION,
            TaskContractType.SHELL,
            TaskContractType.WORKFLOW,
            TaskContractType.INTERNAL_API,
            TaskContractType.MEMORY,
            TaskContractType.GRAPH,
            TaskContractType.DIAGNOSTICS,
        )


def parse_task_contract(task: TaskNode, *, mission_strategy: str = "standard") -> TaskExecutionContract:
    out = task.output or {}
    raw_type = str(out.get("type") or out.get("contract_type") or "").lower()

    if out.get("tool") == "noop" and not raw_type:
        if mission_strategy == "sandbox_only":
            return TaskExecutionContract(
                type=TaskContractType.EXECUTION,
                capability="python.safe",
                params={"code": f"print({repr(task.goal[:80])})"},
            )
        return TaskExecutionContract(type=TaskContractType.NOOP)

    if raw_type == "shell" or out.get("tool") == "shell":
        return TaskExecutionContract(
            type=TaskContractType.SHELL,
            capability=out.get("capability", "shell.safe"),
            params=out.get("params", {"command": out.get("command", "echo mission-step")}),
            timeout_seconds=out.get("timeout_seconds"),
            depends_on=list(out.get("depends_on") or task.dependencies),
            blocking=bool(out.get("blocking", True)),
            parallelizable=bool(out.get("parallelizable", True)),
            affinity=out.get("affinity"),
        )

    if raw_type == "workflow" or out.get("workflow"):
        return TaskExecutionContract(
            type=TaskContractType.WORKFLOW,
            capability="workflow.execute",
            workflow=str(out.get("workflow", "")),
            params=out.get("params", {"steps": out.get("steps", [{"action": out.get("workflow")}])}),
            depends_on=list(out.get("depends_on") or task.dependencies),
            blocking=bool(out.get("blocking", True)),
            parallelizable=bool(out.get("parallelizable", False)),
        )

    if raw_type in ("execution", "") and (
        out.get("capability") or out.get("code") or out.get("type") == "execution"
    ):
        cap = out.get("capability", "python.safe")
        params = dict(out.get("params") or {})
        if "code" in out and "code" not in params:
            params["code"] = out["code"]
        if not params.get("code") and not params.get("command"):
            params["code"] = f"print({repr(task.goal[:120])})"
        return TaskExecutionContract(
            type=TaskContractType.EXECUTION,
            capability=cap,
            params=params,
            timeout_seconds=out.get("timeout_seconds"),
            depends_on=list(out.get("depends_on") or task.dependencies),
            blocking=bool(out.get("blocking", True)),
            parallelizable=bool(out.get("parallelizable", True)),
            affinity=out.get("affinity"),
        )

    if raw_type == "internal_api":
        return TaskExecutionContract(
            type=TaskContractType.INTERNAL_API,
            capability="api.internal",
            params=out.get("params", {"action": out.get("action", "ping")}),
        )

    if raw_type == "memory":
        return TaskExecutionContract(
            type=TaskContractType.MEMORY,
            capability="filesystem.write",
            params=out.get("params", {"op": "write", "path": "memory_note.txt", "content": task.goal[:500]}),
        )

    if raw_type in ("graph", "diagnostics"):
        return TaskExecutionContract(
            type=TaskContractType.GRAPH if raw_type == "graph" else TaskContractType.DIAGNOSTICS,
            capability="api.internal",
            params={"action": raw_type, "goal": task.goal[:200]},
        )

    tool = out.get("tool", "noop")
    if tool and tool != "noop":
        return TaskExecutionContract(
            type=TaskContractType.TOOL,
            tool_name=tool,
            params=dict(out.get("params", {})),
        )

    return TaskExecutionContract(type=TaskContractType.NOOP)
