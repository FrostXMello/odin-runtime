"""Overnight cognition orchestration (Prompt 53)."""
from __future__ import annotations
from typing import Any

MODES = ("passive", "balanced", "engineering", "deep_overnight")


class OvernightCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = False
        self._cycles = 0
        self._mode = "balanced"
        self._summary: dict = {}

    async def start_overnight_cycle(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "overnight_cognition_enabled", False):
            return {"accepted": False, "reason": "overnight_cognition_disabled"}
        max_cycles = int(getattr(self._app.settings, "overnight_max_cycles", 32))
        if self._cycles >= max_cycles:
            return {"accepted": False, "reason": "max_cycles_reached", "bounded": True}
        self._active = True
        self._emit("overnight_cycle_started", {"mode": self._mode, "cycle": self._cycles})
        if hasattr(self._app, "unified_cognitive_core"):
            await self._app.unified_cognitive_core.cognition_tick()
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=True)
        return {"accepted": True, "active": True, "mode": self._mode, "no_auto_deploy": True}

    async def pause_overnight_cycle(self) -> dict[str, Any]:
        self._active = False
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=False)
        return {"accepted": True, "active": False}

    async def execute_idle_reasoning(self) -> dict[str, Any]:
        if not self._active:
            return {"accepted": False, "reason": "overnight_not_active"}
        max_cycles = int(getattr(self._app.settings, "overnight_max_cycles", 32))
        if self._cycles >= max_cycles:
            return {"accepted": False, "reason": "max_cycles_reached"}
        self._cycles += 1
        if hasattr(self._app, "realtime_cognition"):
            await self._app.realtime_cognition.reason(thought=f"idle reasoning cycle {self._cycles}")
        if hasattr(self._app, "autonomous_loop_v2"):
            await self._app.autonomous_loop_v2.autonomous_tick(idle_s=120.0)
        self._emit("idle_reasoning_executed", {"cycle": self._cycles})
        if self._cycles >= max_cycles:
            await self.complete_overnight_cycle()
        return {"accepted": True, "cycle": self._cycles, "bounded": True}

    async def complete_overnight_cycle(self) -> dict[str, Any]:
        self._emit("overnight_cycle_completed", {"cycles": self._cycles})
        self._active = False
        return {"accepted": True, "completed": True, "cycles": self._cycles}

    async def prepare_resume_state(self) -> dict[str, Any]:
        if hasattr(self._app, "deferred_reasoning"):
            restored = await self._app.deferred_reasoning.restore_reasoning()
            return {"accepted": True, "resume": restored}
        return {"accepted": True, "resume": {}}

    async def generate_overnight_summary(self) -> dict[str, Any]:
        self._summary = {"cycles": self._cycles, "mode": self._mode, "active": self._active}
        if hasattr(self._app, "morning_briefing"):
            b = await self._app.morning_briefing.summarize_overnight_activity()
            self._summary["briefing"] = b
        return {"accepted": True, "summary": self._summary}

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        return {"accepted": True, "mode": mode}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "cycles": self._cycles, "mode": self._mode}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="overnight_cognition")
