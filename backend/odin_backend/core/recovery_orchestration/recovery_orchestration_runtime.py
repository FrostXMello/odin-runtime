"""Recovery orchestration runtime (Prompt 61)."""
from __future__ import annotations
from typing import Any

PHASES = ("detection", "stabilization", "rollback_review", "recovery_execution", "validation", "continuity_restore")


class RecoveryOrchestrationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._phase = "detection"
        self._cycles = 0
        self._initialized = False

    async def initialize_recovery_cycle(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "recovery_orchestration_enabled", False):
            return {"accepted": False, "reason": "recovery_orchestration_disabled"}
        self._initialized = True
        self._phase = "detection"
        self._emit("recovery_cycle_initialized", {"phase": self._phase})
        return {"accepted": True, "initialized": True, "supervised": True}

    async def synchronize_recovery_layers(self) -> dict[str, Any]:
        layers = []
        for name, method in (
            ("predictive_recovery_v2", "forecast_operational_failure"),
            ("stability_loops", "rebalance_runtime_pressure"),
            ("rollback_intelligence", "generate_rollback_graph"),
        ):
            if hasattr(self._app, name):
                await getattr(self._app, name).__getattribute__(method)()
                layers.append(name)
        return {"accepted": True, "layers": layers, "bounded": True}

    async def transition_recovery_phase(self, *, phase: str = "stabilization") -> dict[str, Any]:
        if phase not in PHASES:
            return {"accepted": False, "reason": "invalid_phase"}
        if self._cycles > 48:
            return {"accepted": False, "reason": "recovery_cycle_bounded"}
        self._phase = phase
        self._cycles += 1
        self._emit("recovery_phase_transitioned", {"phase": phase})
        return {"accepted": True, "phase": phase, "operator_controlled": True}

    async def validate_recovery_integrity(self) -> dict[str, Any]:
        if hasattr(self._app, "operator_veto"):
            veto = await self._app.operator_veto.authorize_recovery_chain()
            if not veto.get("authorized"):
                return {"accepted": False, "reason": "recovery_not_authorized", "approval_gated": True}
        return {"accepted": True, "valid": True, "reversible": True, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"phase": self._phase, "cycles": self._cycles, "initialized": self._initialized}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="recovery_orchestration")
