"""Stuck/orphan execution recovery."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from odin_backend.core.execution.models import ExecutionState
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ExecutionRecoveryLoop:
    def __init__(self, engine: Any, *, interval_seconds: float = 30.0) -> None:
        self._engine = engine
        self._interval = interval_seconds
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task:
            return
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._interval)
                await self._engine.recover_stuck()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("execution_recovery_error", error=str(exc))

    @staticmethod
    def is_stuck(record: Any, *, heartbeat_seconds: float, lease_expired: bool) -> bool:
        if record.state not in (
            ExecutionState.RUNNING,
            ExecutionState.ALLOCATED,
            ExecutionState.WAITING,
        ):
            return False
        if lease_expired:
            return True
        if not record.last_heartbeat_at:
            return False
        age = (datetime.now(timezone.utc) - record.last_heartbeat_at).total_seconds()
        return age > heartbeat_seconds
