"""Unified command center runtime (Prompt 60)."""
from __future__ import annotations
from typing import Any


class UnifiedCommandCenterRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._initialized = False
        self._health = 0.9
        self._pressure = 0.4
        self._profile = "balanced"

    async def initialize_command_center(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "unified_command_center_enabled", False):
            return {"accepted": False, "reason": "unified_command_center_disabled"}
        self._initialized = True
        self._profile = getattr(self._app.settings, "command_profile", "balanced")
        self._emit("command_center_initialized", {"profile": self._profile})
        return {"accepted": True, "initialized": True, "supervised": True, "operator_visible": True}

    async def synchronize_runtime_layers(self) -> dict[str, Any]:
        layers = []
        for name, method in (
            ("predictive_governance", "rebalance_governance_pressure"),
            ("live_orchestration", "stream_orchestration_state"),
            ("distributed_execution", "synchronize_distributed_execution"),
        ):
            if hasattr(self._app, name):
                await getattr(self._app, name).__getattribute__(method)()
                layers.append(name)
        self._emit("runtime_layers_synchronized", {"layers": layers})
        return {"accepted": True, "layers": layers, "bounded": True}

    async def compute_global_operational_health(self) -> dict[str, Any]:
        if hasattr(self._app, "predictive_governance"):
            h = await self._app.predictive_governance.compute_governance_health()
            self._health = h.get("health", self._health)
        self._emit("global_operational_health_updated", {"health": self._health})
        return {"accepted": True, "health": round(self._health, 2), "transparent": True}

    async def rebalance_command_pressure(self) -> dict[str, Any]:
        self._pressure = max(0.1, self._pressure - 0.05)
        if hasattr(self._app, "desktop_attention"):
            await self._app.desktop_attention.prioritize_desktop_attention()
        return {"accepted": True, "pressure": round(self._pressure, 2), "throttled": self._profile == "compact"}

    def snapshot(self) -> dict[str, Any]:
        return {"initialized": self._initialized, "health": self._health, "pressure": self._pressure, "profile": self._profile}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="unified_command_center")
