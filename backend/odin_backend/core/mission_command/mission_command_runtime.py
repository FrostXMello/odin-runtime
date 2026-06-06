"""Mission command runtime (Prompt 60)."""
from __future__ import annotations
from typing import Any

PHASES = ("planning", "execution", "recovery", "stabilization", "overnight", "supervision_review")


class MissionCommandRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._phase = "planning"
        self._pressure = 0.5

    async def initialize_mission_command(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "mission_command_enabled", False):
            return {"accepted": False, "reason": "mission_command_disabled"}
        self._phase = "planning"
        return {"accepted": True, "phase": self._phase, "supervised": True}

    async def synchronize_objective_graph(self) -> dict[str, Any]:
        if hasattr(self._app, "objective_management"):
            await self._app.objective_management.summarize_active_objectives()
        if hasattr(self._app, "mission_graph"):
            await self._app.mission_graph.build_mission_graph()
        self._emit("objective_graph_synchronized", {"phase": self._phase})
        return {"accepted": True, "synchronized": True, "approval_gated": True}

    async def compute_mission_pressure(self) -> dict[str, Any]:
        return {"accepted": True, "pressure": round(self._pressure, 2), "phase": self._phase}

    async def transition_operational_phase(self, *, phase: str = "execution") -> dict[str, Any]:
        if phase not in PHASES:
            return {"accepted": False, "reason": "invalid_phase"}
        self._phase = phase
        self._emit("mission_phase_transitioned", {"phase": phase})
        return {"accepted": True, "phase": phase, "operator_controlled": True}

    def snapshot(self) -> dict[str, Any]:
        return {"phase": self._phase, "pressure": self._pressure}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="mission_command")
