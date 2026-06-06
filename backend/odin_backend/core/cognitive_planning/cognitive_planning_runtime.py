"""Cognitive planning runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class CognitivePlanningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "balanced"
        self._budget = 1.0

    async def generate_cognitive_plan(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_planning_enabled", False):
            return {"accepted": False, "reason": "cognitive_planning_disabled"}
        self._mode = getattr(self._app.settings, "reasoning_budget_mode", "adaptive")
        plan = {"horizon": "medium", "mode": self._mode, "approval_gated": True, "no_auto_deploy": True}
        self._emit("cognitive_plan_generated", {"mode": self._mode})
        return {"accepted": True, "plan": plan, "bounded": True}

    async def allocate_reasoning_budget(self) -> dict[str, Any]:
        mode = getattr(self._app.settings, "reasoning_budget_mode", "adaptive")
        if mode == "adaptive":
            self._budget = max(0.2, self._budget - 0.05)
        self._emit("reasoning_budget_rebalanced", {"budget": self._budget})
        return {"accepted": True, "budget": self._budget, "throttled": mode == "adaptive"}

    async def estimate_task_horizon(self, *, task: str = "engineering") -> dict[str, Any]:
        horizon = "long" if task == "research" else "medium"
        return {"accepted": True, "task": task[:60], "horizon": horizon}

    async def optimize_focus_schedule(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_focus"):
            snap = self._app.operator_focus.snapshot()
            return {"accepted": True, "focus_active": snap.get("active", False), "low_power": self._mode == "compact"}
        return {"accepted": True, "focus_active": False}

    async def compress_background_reasoning(self) -> dict[str, Any]:
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=True)
        return {"accepted": True, "compressed": True, "low_power": True}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "budget": self._budget}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_planning")
