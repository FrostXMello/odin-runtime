"""Scheduled cognition jobs for autonomous operator."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class AutonomyScheduler:
    """Periodic jobs: consolidation, reflection, embedding optimization, objective reevaluation."""

    def __init__(self, app: Any) -> None:
        self._app = app
        self._task: asyncio.Task | None = None
        self._jobs: dict[str, float] = {
            "memory_consolidation": 3600.0,
            "nightly_reflection": 7200.0,
            "embedding_optimization": 1800.0,
            "objective_reevaluation": 900.0,
            "planner_improvement": 1800.0,
        }
        self._last_run: dict[str, float] = {}

    async def start(self, *, interval: float = 30.0) -> None:
        if self._task:
            return
        self._task = asyncio.create_task(self._loop(interval))

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self, interval: float) -> None:
        import time

        while True:
            try:
                await asyncio.sleep(interval)
                now = time.monotonic()
                for name, cadence in self._jobs.items():
                    last = self._last_run.get(name, 0.0)
                    if now - last >= cadence:
                        await self._run_job(name)
                        self._last_run[name] = now
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("autonomy_scheduler_error", error=str(exc))

    async def _run_job(self, name: str) -> None:
        handlers: dict[str, Callable[[], Coroutine[Any, Any, None]]] = {
            "memory_consolidation": self._memory_consolidation,
            "nightly_reflection": self._reflection,
            "embedding_optimization": self._embedding_opt,
            "objective_reevaluation": self._reevaluate_objectives,
            "planner_improvement": self._planner_improvement,
        }
        handler = handlers.get(name)
        if handler:
            await handler()

    async def _memory_consolidation(self) -> None:
        if hasattr(self._app, "improvement_loop"):
            await self._app.improvement_loop.run_cycle()

    async def _reflection(self) -> None:
        if hasattr(self._app, "cognitive_reflection"):
            await self._app.cognitive_reflection.reflect(
                plan="Review recent mission outcomes",
                objective="Autonomous reflection cycle",
            )

    async def _embedding_opt(self) -> None:
        if hasattr(self._app, "improvement_loop"):
            await self._app.improvement_loop.recalibrate_confidence()

    async def _reevaluate_objectives(self) -> None:
        objs = await self._app.objective_manager.list_all(status="active")
        for obj in objs:
            if obj.confidence < 0.3:
                await self._app.objective_manager.graph.defer(obj.objective_id)

    async def _planner_improvement(self) -> None:
        if hasattr(self._app, "improvement_loop"):
            await self._app.improvement_loop.run_cycle()
