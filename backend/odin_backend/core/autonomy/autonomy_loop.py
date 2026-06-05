"""Autonomous loop engine — continuous bounded cognitive operation."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

from odin_backend.core.autonomy.autonomy_metrics import AutonomyMetrics
from odin_backend.core.autonomy.autonomy_policy import AutonomyPolicyConfig, AutonomyPermissionMode
from odin_backend.core.autonomy.autonomy_state import AutonomyRunState, AutonomyState
from odin_backend.core.autonomy.initiative_engine import InitiativeEngine
from odin_backend.core.autonomy.scheduler import AutonomyScheduler
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

LOOP_TYPES = (
    "monitoring_loop",
    "optimization_loop",
    "research_loop",
    "reflection_loop",
    "memory_consolidation_loop",
    "planner_improvement_loop",
)


class AutonomousLoopEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._state = AutonomyState()
        self._metrics = AutonomyMetrics()
        self._policy = AutonomyPolicyConfig()
        self._initiative = InitiativeEngine(app)
        self._scheduler = AutonomyScheduler(app)
        self._task: asyncio.Task | None = None
        self._missions_this_hour: list[float] = []

    @property
    def state(self) -> AutonomyState:
        return self._state

    @property
    def metrics(self) -> AutonomyMetrics:
        return self._metrics

    @property
    def policy(self) -> AutonomyPolicyConfig:
        return self._policy

    def set_mode(self, mode: str) -> None:
        try:
            self._policy.mode = AutonomyPermissionMode(mode)
        except ValueError:
            self._policy.mode = AutonomyPermissionMode.SUPERVISED
        self._state.mode = mode

    async def start(self) -> dict[str, Any]:
        if self._state.run_state == AutonomyRunState.RUNNING:
            return self._state.snapshot()
        self._state.run_state = AutonomyRunState.RUNNING
        self._state.paused_at = None
        await self._scheduler.start(interval=30.0)
        self._task = asyncio.create_task(self._main_loop())
        self._emit("autonomy_cycle_started", {"mode": self._state.mode})
        logger.info("autonomous_loop_started", mode=self._state.mode)
        return self._state.snapshot()

    async def pause(self) -> dict[str, Any]:
        self._state.run_state = AutonomyRunState.PAUSED
        self._state.paused_at = datetime.now(timezone.utc)
        self._emit("autonomy_paused", {})
        return self._state.snapshot()

    async def stop(self) -> None:
        self._state.run_state = AutonomyRunState.STOPPED
        await self._scheduler.stop()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _main_loop(self) -> None:
        interval = getattr(self._app.settings, "autonomy_cycle_interval_seconds", 60.0)
        while self._state.run_state == AutonomyRunState.RUNNING:
            try:
                if self._state.run_state == AutonomyRunState.PAUSED:
                    await asyncio.sleep(1.0)
                    continue
                if self._in_cooldown():
                    await asyncio.sleep(1.0)
                    continue
                safety = self._app.autonomy_safety
                if not safety.allow_cycle():
                    self._metrics.loops_skipped_budget += 1
                    await asyncio.sleep(interval)
                    continue
                alerts = await self._app.environment_monitor.collect_alerts()
                for loop_type in self._enabled_loops():
                    await self._run_loop(loop_type, alerts=alerts)
                await self._maybe_spawn_missions(alerts)
                self._state.cycle_count += 1
                self._state.last_cycle_at = datetime.now(timezone.utc)
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("autonomous_loop_error", error=str(exc))
                await asyncio.sleep(interval)

    def _enabled_loops(self) -> list[str]:
        return [lt for lt in LOOP_TYPES if lt in self._policy.enabled_loop_types]

    async def _run_loop(self, loop_type: str, *, alerts: list[dict]) -> None:
        budget = self._policy.max_cycle_budget_seconds
        start = time.perf_counter()
        self._state.active_loops = [loop_type]
        try:
            if loop_type == "monitoring_loop":
                self._metrics.environment_alerts += len(alerts)
            elif loop_type == "optimization_loop" and self._policy.allow_optimization:
                if hasattr(self._app, "improvement_loop"):
                    await self._app.improvement_loop.run_cycle()
            elif loop_type == "research_loop" and self._policy.allow_research:
                if self._policy.mode in (AutonomyPermissionMode.RESEARCH_ONLY, AutonomyPermissionMode.FULLY_LOCAL_AUTONOMOUS, AutonomyPermissionMode.SEMI_AUTONOMOUS):
                    await self._app.research_engine.run_iteration(topic="runtime improvement")
            elif loop_type == "reflection_loop":
                await self._app.cognitive_reflection.reflect(
                    plan="Autonomous reflection",
                    objective="Review operational patterns",
                )
            elif loop_type == "memory_consolidation_loop":
                await self._app.improvement_loop.recalibrate_confidence()
            elif loop_type == "planner_improvement_loop":
                await self._app.improvement_loop.run_cycle()
            self._metrics.record_loop(loop_type)
        finally:
            elapsed = time.perf_counter() - start
            if elapsed > budget:
                self._metrics.loops_skipped_budget += 1
            self._state.active_loops = []

    async def _maybe_spawn_missions(self, alerts: list[dict]) -> None:
        if self._policy.mode == AutonomyPermissionMode.OBSERVE_ONLY:
            return
        if not self._policy.allow_proactive_missions and self._policy.mode != AutonomyPermissionMode.FULLY_LOCAL_AUTONOMOUS:
            if self._policy.mode == AutonomyPermissionMode.SUPERVISED:
                return
        safety = self._app.autonomy_safety
        if not safety.allow_mission_spawn():
            return
        initiatives = await self._initiative.propose_initiatives(alerts=alerts)
        for init in initiatives[:2]:
            objective = init.get("mission_objective", "")
            if not objective:
                continue
            approved = not self._policy.require_approval_for_missions
            if self._policy.mode == AutonomyPermissionMode.FULLY_LOCAL_AUTONOMOUS:
                approved = True
            try:
                result = await self._app.mission_manager.create_checked(
                    objective,
                    human_approved=approved,
                    created_by="autonomous_operator",
                    originating_signal="autonomy_loop",
                    autonomy_level=2,
                )
                if result.created:
                    safety.record_mission_spawned()
                    self._metrics.missions_spawned += 1
                    self._state.missions_generated += 1
                    self._missions_this_hour.append(time.time())
                    self._emit(
                        "autonomy_objective_generated",
                        {"mission_id": result.mission.mission_id, "initiative": init.get("kind")},
                    )
            except Exception as exc:
                logger.debug("autonomous_mission_skipped", error=str(exc))

    def _in_cooldown(self) -> bool:
        if self._state.cooldown_until and datetime.now(timezone.utc) < self._state.cooldown_until:
            return True
        return False

    def snapshot(self) -> dict[str, Any]:
        return {
            "state": self._state.snapshot(),
            "metrics": self._metrics.model_dump(),
            "policy": self._policy.model_dump(mode="json"),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_loop")
