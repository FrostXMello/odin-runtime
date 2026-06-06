"""Execution confidence runtime (Prompt 59)."""
from __future__ import annotations
from typing import Any


class ExecutionConfidenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._confidence = 0.7
        self._rollback_conf = 0.8

    async def estimate_execution_confidence(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_confidence_enabled", False):
            return {"accepted": False, "reason": "execution_confidence_disabled"}
        if hasattr(self._app, "predictive_recovery"):
            r = await self._app.predictive_recovery.compute_execution_resilience()
            self._confidence = r.get("resilience", 0.7)
        self._emit("execution_confidence_estimated", {"confidence": self._confidence})
        return {"accepted": True, "confidence": round(self._confidence, 2), "bounded": True}

    async def forecast_workflow_completion(self) -> dict[str, Any]:
        prob = min(1.0, self._confidence + 0.1)
        self._emit("workflow_completion_forecasted", {"probability": prob})
        return {"accepted": True, "probability": round(prob, 2), "supervised": True}

    async def compute_rollback_confidence(self) -> dict[str, Any]:
        return {"accepted": True, "rollback_confidence": round(self._rollback_conf, 2), "reversible": True}

    async def surface_execution_probability(self) -> dict[str, Any]:
        return {"accepted": True, "probability": round(self._confidence, 2), "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"confidence": self._confidence, "rollback_confidence": self._rollback_conf}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_confidence")
