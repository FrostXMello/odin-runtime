"""Persistent autonomous agent loop V2 (Prompt 50)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_loop_v2.autonomous_tick_scheduler import tick
from odin_backend.core.autonomous_loop_v2.deferred_execution_planner import plan
from odin_backend.core.autonomous_loop_v2.goal_continuation_engine import continue_goal
from odin_backend.core.autonomous_loop_v2.long_horizon_coordinator import coordinate
from odin_backend.core.autonomous_loop_v2.persistent_task_graph import graph


class AutonomousLoopV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._goals: list[str] = []

    async def resume_goal(self, *, goal: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_loop_v2_enabled", False):
            return {"accepted": False, "reason": "autonomous_loop_v2_disabled"}
        cont = continue_goal(goal=goal)
        g = graph(goals=[goal])
        self._goals.append(goal[:120])
        self._emit("autonomous_goal_resumed", cont)
        self._emit("persistent_reasoning_restored", {"goal": goal[:120]})
        return {"accepted": True, "continuation": cont, "graph": g, "execution_approval_required": True}

    async def plan_horizon(self, *, days: int = 3) -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_loop_v2_enabled", False):
            return {"accepted": False, "reason": "autonomous_loop_v2_disabled"}
        coord = coordinate(horizon_days=days)
        self._emit("long_horizon_plan_updated", coord)
        return {"accepted": True, "plan": coord, "no_self_modifying_writes": True}

    async def defer_task(self, *, task: str) -> dict[str, Any]:
        p = plan(task=task)
        return {"accepted": True, "deferred": p}

    async def autonomous_tick(self, *, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_loop_v2_enabled", False):
            return {"accepted": False, "reason": "autonomous_loop_v2_disabled"}
        result = await tick(self._app, idle_s=idle_s)
        self._emit("autonomous_tick_executed", {"idle_s": idle_s})
        return {"accepted": True, "tick": result, "recursion_bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"goals": len(self._goals)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_loop_v2")
