"""In-memory execution record store."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.core.execution.models import ExecutionRecord, ExecutionState


class ExecutionResultStore:
    def __init__(self) -> None:
        self._records: dict[str, ExecutionRecord] = {}
        self._lock = asyncio.Lock()

    async def put(self, record: ExecutionRecord) -> None:
        async with self._lock:
            self._records[record.execution_id] = record

    async def get(self, execution_id: str) -> ExecutionRecord | None:
        async with self._lock:
            return self._records.get(execution_id)

    async def update(self, execution_id: str, **fields: Any) -> ExecutionRecord | None:
        async with self._lock:
            rec = self._records.get(execution_id)
            if not rec:
                return None
            updated = rec.model_copy(update=fields)
            self._records[execution_id] = updated
            return updated

    async def list_active(self) -> list[ExecutionRecord]:
        active = {
            ExecutionState.QUEUED,
            ExecutionState.ALLOCATED,
            ExecutionState.RUNNING,
            ExecutionState.WAITING,
            ExecutionState.RETRYING,
            ExecutionState.ROLLING_BACK,
        }
        async with self._lock:
            return [r for r in self._records.values() if r.state in active]

    async def list_all(self, *, limit: int = 100) -> list[ExecutionRecord]:
        async with self._lock:
            items = sorted(
                self._records.values(),
                key=lambda r: r.created_at,
                reverse=True,
            )
            return items[:limit]

    async def list_by_mission(self, mission_id: str) -> list[ExecutionRecord]:
        async with self._lock:
            items = [r for r in self._records.values() if r.mission_id == mission_id]
            return sorted(items, key=lambda r: r.created_at, reverse=True)
