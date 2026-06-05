"""Episodic memory — specific execution histories."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.entities import MemoryEntity, MemoryEntityKind


def episodic_from_execution(
    *,
    mission_id: str,
    task_id: str | None,
    execution_id: str,
    summary: str,
    success: bool,
    metadata: dict[str, Any] | None = None,
) -> MemoryEntity:
    return MemoryEntity(
        kind=MemoryEntityKind.EPISODIC,
        label=summary[:500],
        mission_id=mission_id,
        task_id=task_id,
        execution_id=execution_id,
        confidence=0.75 if success else 0.35,
        metadata={"success": success, **(metadata or {})},
    )
