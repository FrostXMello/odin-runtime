"""Operator productivity orchestrator (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.operator_productivity.attention_metrics import score
from odin_backend.core.operator_productivity.daily_strategy import plan
from odin_backend.core.operator_productivity.distraction_detection import detect
from odin_backend.core.operator_productivity.focus_cycles import FocusCycles
from odin_backend.core.operator_productivity.operator_burnout import risk
from odin_backend.core.operator_productivity.session_energy import energy_level
from odin_backend.core.operator_productivity.workflow_optimizer import optimize


class OperatorProductivityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cycles = FocusCycles()
        self._focus_min = 0
        self._distractions = 0

    async def start_focus(self, *, minutes: int = 25) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_productivity_enabled", False):
            return {"accepted": False, "reason": "operator_productivity_disabled"}
        cycle = self._cycles.start(minutes=minutes)
        self._focus_min = 0
        return {"accepted": True, "cycle": cycle}

    async def record_distraction(self, *, context_switches: int = 1) -> dict[str, Any]:
        self._distractions += context_switches
        hit = detect(context_switches=self._distractions)
        if hit.get("distracted"):
            self._emit("operator_focus_degraded", hit)
        return {"accepted": True, **hit}

    async def summary(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_productivity_enabled", False):
            return {"accepted": False, "reason": "operator_productivity_disabled"}
        attn = score(distractions=self._distractions, focus_min=self._focus_min)
        energy = energy_level(focus_minutes=self._focus_min)
        strategy = await plan(self._app)
        burnout = risk(session_hours=self._focus_min / 60.0)
        opt = optimize(bottlenecks=["context switching", "long meetings"])
        return {
            "accepted": True,
            "attention_score": attn,
            "energy": energy,
            "strategy": strategy,
            "burnout": burnout,
            "optimizer": opt,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"focus_min": self._focus_min, "distractions": self._distractions}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_productivity")
