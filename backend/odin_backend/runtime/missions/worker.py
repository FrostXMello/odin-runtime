"""Background mission workers — scheduler facade for execution dispatcher."""

import asyncio
from typing import Any

from odin_backend.runtime.missions.scheduler import MissionScheduler
from odin_backend.core.missions.lifecycle import DISPATCHABLE_MISSION_STATES, migrate_legacy_state
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class MissionWorkerPool:
    """
    Provides mission scheduling queue.

    When ``mission_dispatch_enabled`` is true, ``ExecutionDispatcher`` owns the
    execution loop; this pool only exposes ``scheduler`` and optional legacy loop.
    """

    def __init__(self, app: Any) -> None:
        self._app = app
        if app.settings.queue_persist_enabled:
            from odin_backend.runtime.missions.persistent_scheduler import PersistentMissionScheduler

            self._scheduler = PersistentMissionScheduler(app)
        else:
            self._scheduler = MissionScheduler(
                cooldown_seconds=app.settings.mission_cooldown_seconds
            )
        self._task: asyncio.Task | None = None
        self._running = False

    @property
    def scheduler(self) -> MissionScheduler:
        return self._scheduler

    async def start(self) -> None:
        if self._app.settings.mission_dispatch_enabled:
            logger.info("mission_worker_scheduler_only", dispatch_enabled=True)
            return
        if not self._app.settings.mission_worker_enabled:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("mission_worker_started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def enqueue_mission(self, mission_id: str, *, delay_seconds: float = 0.0) -> None:
        self._scheduler.schedule(mission_id, delay_seconds=delay_seconds)
        dispatcher = getattr(self._app, "mission_dispatcher", None)
        if dispatcher:
            dispatcher.enqueue(mission_id, delay=delay_seconds)

    async def _loop(self) -> None:
        """Legacy worker loop — used only when dispatch is disabled."""
        from odin_backend.core.missions.dispatcher import ExecutionDispatcher

        interval = self._app.settings.mission_worker_interval_seconds
        while self._running:
            try:
                due_ids = self._scheduler.pop_due()
                if not due_ids:
                    manager = self._app.mission_manager
                    for mission in await manager.list_active_missions():
                        st = migrate_legacy_state(mission.current_state)
                        if st in DISPATCHABLE_MISSION_STATES:
                            self._scheduler.schedule(mission.mission_id)
                    await asyncio.sleep(interval)
                    continue

                sem = asyncio.Semaphore(self._app.settings.mission_max_concurrent_missions)
                dispatcher = ExecutionDispatcher(self._app)
                await asyncio.gather(
                    *[
                        dispatcher._dispatch_with_sem(  # noqa: SLF001
                            self._app.mission_runtime,
                            self._app.mission_manager,
                            mid,
                            sem,
                        )
                        for mid in due_ids[:10]
                    ],
                    return_exceptions=True,
                )
            except Exception as exc:
                logger.exception("mission_worker_tick_error", error=str(exc))
            await asyncio.sleep(interval)
