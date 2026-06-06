"""Runtime stabilization runtime (Prompt 59)."""
from __future__ import annotations
from typing import Any


class RuntimeStabilizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "balanced"
        self._cooldown = False

    async def detect_runtime_instability(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_stabilization_enabled", False):
            return {"accepted": False, "reason": "runtime_stabilization_disabled"}
        unstable = False
        if hasattr(self._app, "live_orchestration"):
            r = await self._app.live_orchestration.detect_runtime_instability()
            unstable = r.get("unstable", False)
        if unstable:
            self._emit("runtime_instability_detected", {"mode": self._mode})
        return {"accepted": True, "unstable": unstable, "operator_visible": True}

    async def stabilize_runtime_pressure(self) -> dict[str, Any]:
        self._mode = getattr(self._app.settings, "runtime_stabilization_mode", "balanced")
        if hasattr(self._app, "execution_system"):
            await self._app.execution_system.stabilize_execution_flow()
        self._emit("runtime_stabilization_applied", {"mode": self._mode})
        return {"accepted": True, "stabilized": True, "mode": self._mode}

    async def trigger_governance_cooldown(self) -> dict[str, Any]:
        self._cooldown = True
        return {"accepted": True, "cooldown": True, "bounded": True}

    async def recover_degraded_runtime(self) -> dict[str, Any]:
        if hasattr(self._app, "distributed_execution"):
            return await self._app.distributed_execution.recover_distributed_pipeline()
        return {"accepted": True, "recovered": False, "reversible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "cooldown": self._cooldown}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_stabilization")
