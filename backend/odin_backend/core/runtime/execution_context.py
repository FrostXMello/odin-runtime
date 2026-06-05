"""Execution context binding mission tasks to engine runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from odin_backend.core.runtime.task_contracts import TaskExecutionContract
from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskNode


@dataclass
class MissionTaskExecutionContext:
    mission: Mission
    task: TaskNode
    contract: TaskExecutionContract
    execution_id: str | None = None
    trace_id: str | None = None
    rollback_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
