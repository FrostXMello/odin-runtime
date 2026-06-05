"""Planner worker — semantic planning, replanning, validation analysis."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.monitoring.logging import get_logger
from odin_backend.runtime_worker.heartbeat import WorkerHeartbeat
from odin_backend.runtime_worker.registration import WorkerRegistration

logger = get_logger(__name__)


class PlannerWorker:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._task: asyncio.Task | None = None
        self._heartbeat = WorkerHeartbeat(app)
        self._registration = WorkerRegistration(app)
        self._metrics: dict[str, int] = {
            "plans_generated": 0,
            "replans": 0,
            "validations": 0,
        }

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    async def start(self) -> None:
        await self._registration.register(role="planner", capabilities=["workflow.execute", "planner.reasoning"])
        await self._heartbeat.start()
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        await self._heartbeat.stop()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        interval = max(5.0, self._app.settings.mission_dispatch_interval_seconds * 2)
        while True:
            try:
                await self._tick()
            except Exception as exc:
                logger.warning("planner_tick_error", error=str(exc))
            await asyncio.sleep(interval)

    async def _tick(self) -> None:
        mgr = self._app.mission_manager
        active = await mgr.list_active_missions()
        for mission in active[:10]:
            failed = sum(
                1
                for n in mission.task_graph.nodes.values()
                if n.status.value in ("failed", "blocked")
            )
            if failed >= 2 and mission.metadata.get("semantic_plan"):
                self._app.mission_planner.replan(mission, reason="planner_worker_recovery")
                self._metrics["replans"] += 1
                pubsub = getattr(self._app, "distributed_pubsub", None)
                if pubsub:
                    await pubsub.publish(
                        "planner_replan",
                        {"mission_id": mission.mission_id, "reason": "worker_recovery"},
                    )

            semantic = self._app.mission_planner.get_semantic_plan(mission.mission_id)
            if semantic and self._app.plan_validator:
                v = self._app.plan_validator.validate_plan(semantic.task_graph, semantic.contracts)
                self._metrics["validations"] += 1
                if not v["consistent"]:
                    mission.append_reasoning("planner_validation", detail=v)
