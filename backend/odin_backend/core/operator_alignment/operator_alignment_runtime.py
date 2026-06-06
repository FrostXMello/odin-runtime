"""Operator alignment runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class OperatorAlignmentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._alignment = 0.7
        self._confidence = 0.8
        self._drift = 0.0

    async def estimate_operator_alignment(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_alignment_enabled", False):
            return {"accepted": False, "reason": "operator_alignment_disabled"}
        if hasattr(self._app, "operator_intelligence_v4"):
            self._alignment = min(1.0, self._alignment + 0.02)
        self._emit("operator_alignment_updated", {"alignment": self._alignment})
        return {"accepted": True, "alignment": round(self._alignment, 2), "bounded": True, "transparent": True}

    async def adapt_assistance_strategy(self) -> dict[str, Any]:
        strategy = "conservative" if self._alignment < 0.5 else "balanced"
        return {"accepted": True, "strategy": strategy, "operator_override": True}

    async def compute_supervision_confidence(self) -> dict[str, Any]:
        if hasattr(self._app, "desktop_attention"):
            await self._app.desktop_attention.prioritize_desktop_attention()
        return {"accepted": True, "confidence": round(self._confidence, 2), "supervised": True}

    async def detect_alignment_drift(self) -> dict[str, Any]:
        self._drift = max(0.0, self._drift + 0.01 - self._alignment * 0.01)
        drifted = self._drift > 0.15
        return {"accepted": True, "drift": round(self._drift, 3), "drifted": drifted, "operator_visible": True}

    def snapshot(self) -> dict[str, Any]:
        return {"alignment": self._alignment, "confidence": self._confidence, "drift": self._drift}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_alignment")
