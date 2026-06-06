"""Pressure propagation runtime (Prompt 63)."""
from __future__ import annotations
from typing import Any


class PressurePropagationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.45
        self._surfaces: dict[str, float] = {}
        self._congestion: list[str] = []

    async def propagate_runtime_pressure(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "pressure_propagation_enabled", False):
            return {"accepted": False, "reason": "pressure_propagation_disabled"}
        if hasattr(self._app, "runtime_fusion"):
            await self._app.runtime_fusion.stabilize_cross_runtime_pressure()
        if hasattr(self._app, "stability_loops"):
            await self._app.stability_loops.rebalance_runtime_pressure()
        self._surfaces = {"execution": 0.5, "cognition": 0.4, "recovery": 0.35}
        self._emit("runtime_pressure_propagated", {"surfaces": len(self._surfaces)})
        return {
            "accepted": True,
            "surfaces": self._surfaces,
            "operator_visible": True,
            "transparent": True,
        }

    async def simulate_pressure_diffusion(self) -> dict[str, Any]:
        diffused = {k: max(0.1, v - 0.05) for k, v in (self._surfaces or {"default": 0.4}).items()}
        self._surfaces = diffused
        self._emit("pressure_diffusion_simulated", {"surfaces": len(diffused)})
        return {"accepted": True, "surfaces": diffused, "bounded": True}

    async def detect_congestion_chain(self) -> dict[str, Any]:
        self._congestion = ["execution_queue", "cognition_timeline"] if self._pressure > 0.4 else []
        self._emit("execution_congestion_detected", {"chains": len(self._congestion)})
        return {"accepted": True, "congestion": self._congestion, "operator_visible": True}

    async def rebalance_pressure_surfaces(self) -> dict[str, Any]:
        self._pressure = max(0.1, self._pressure - 0.04)
        self._surfaces = {k: max(0.1, v - 0.03) for k, v in self._surfaces.items()} if self._surfaces else {"default": 0.3}
        self._emit("pressure_surfaces_rebalanced", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "surfaces": self._surfaces, "reversible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure, "surfaces": self._surfaces, "congestion": self._congestion}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="pressure_propagation")
