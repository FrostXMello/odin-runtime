"""Runtime execution visibility (Prompt 57)."""
from __future__ import annotations
from typing import Any


class RuntimeExecutionVisibilityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._pressure = 0.3
        self._density = "balanced"
        self._stream_count = 0

    async def render_execution_heatmap(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_execution_visibility_enabled", False):
            return {"accepted": False, "reason": "runtime_execution_visibility_disabled"}
        return {"accepted": True, "heatmap": True, "adaptive": True}

    async def stream_execution_visibility(self) -> dict[str, Any]:
        if self._stream_count > 56:
            return {"accepted": False, "reason": "stream_bounded"}
        self._stream_count += 1
        self._emit("execution_visibility_streamed", {"count": self._stream_count})
        return {"accepted": True, "streamed": True, "transparent": True}

    async def compute_execution_pressure(self) -> dict[str, Any]:
        if hasattr(self._app, "task_orchestration"):
            snap = self._app.task_orchestration.snapshot()
            self._pressure = min(1.0, snap.get("queue_size", 0) / 20.0)
        self._emit("execution_pressure_updated", {"pressure": self._pressure})
        return {"accepted": True, "pressure": round(self._pressure, 2), "operator_visible": True}

    async def compress_execution_streams(self) -> dict[str, Any]:
        self._density = getattr(self._app.settings, "execution_stream_density", "balanced")
        return {"accepted": True, "density": self._density, "low_power": self._density == "compact"}

    def snapshot(self) -> dict[str, Any]:
        return {"pressure": self._pressure, "stream_count": self._stream_count}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_execution_visibility")
