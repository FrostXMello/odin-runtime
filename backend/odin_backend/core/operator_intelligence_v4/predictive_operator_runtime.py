"""Predictive operator intelligence V4 (Prompt 51)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.operator_intelligence_v4.attention_prediction_engine import AttentionPredictionEngine
from odin_backend.core.operator_intelligence_v4.cognitive_load_forecast_runtime import CognitiveLoadForecastRuntime
from odin_backend.core.operator_intelligence_v4.focus_recovery_runtime import FocusRecoveryRuntime
from odin_backend.core.operator_intelligence_v4.long_session_health_runtime import health
from odin_backend.core.operator_intelligence_v4.workflow_optimization_runtime import WorkflowOptimizationRuntime


class PredictiveOperatorRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attention = AttentionPredictionEngine(app)
        self._load = CognitiveLoadForecastRuntime(app)
        self._workflow = WorkflowOptimizationRuntime(app)
        self._recovery = FocusRecoveryRuntime(app)

    async def predict(self, *, hours: float = 4.0, switches: int = 3, context: str = "engineering") -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_intelligence_v4_enabled", False):
            return {"accepted": False, "reason": "operator_intelligence_v4_disabled"}
        attn = await self._attention.forecast(switches=switches)
        load = await self._load.forecast(hours=hours)
        wf = await self._workflow.optimize(context=context)
        rec = await self._recovery.recover(fatigue=hours > 5.0)
        h = health(hours=hours)
        return {
            "accepted": True,
            "attention": attn,
            "load_forecast": load,
            "workflow": wf,
            "recovery": rec,
            "session_health": h,
            "local_only": True,
            "operator_override": True,
        }

    async def forecast_focus(self, *, switches: int = 3) -> dict[str, Any]:
        return await self._attention.forecast(switches=switches)

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_intelligence_v4")
