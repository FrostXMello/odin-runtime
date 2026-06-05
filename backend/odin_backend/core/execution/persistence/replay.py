"""Execution replay utilities."""

from __future__ import annotations

from typing import Any

from odin_backend.core.execution.models import ExecutionRecord, ExecutionState


async def replay_execution_metadata(store: Any, execution_id: str) -> ExecutionRecord | None:
    return await store.get(execution_id)


async def list_recoverable_executions(store: Any) -> list[ExecutionRecord]:
    active = await store.list_active()
    return [r for r in active if r.state in {
        ExecutionState.QUEUED,
        ExecutionState.ALLOCATED,
        ExecutionState.RUNNING,
        ExecutionState.RETRYING,
    }]
