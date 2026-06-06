from __future__ import annotations
from typing import Any


class AdaptiveAssistanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._intensity = 0.5

    async def adjust(self, *, fatigue: bool = False) -> dict[str, Any]:
        self._intensity = 0.3 if fatigue else 0.6
        self._emit("adaptive_assistance_adjusted", {"intensity": self._intensity})
        self._emit("attention_heatmap_updated", {"cells": [20, 40, 60]})
        return {"accepted": True, "intensity": self._intensity, "transparent": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence_v2")
