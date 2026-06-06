"""Autonomous debugging pipeline (Prompt 47 extension)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_debugging.confidence_gates import gate
from odin_backend.core.autonomous_debugging.failure_clusterer import cluster
from odin_backend.core.autonomous_debugging.patch_hypothesis import hypothesize
from odin_backend.core.autonomous_debugging.regression_predictor import predict
from odin_backend.core.autonomous_debugging.runtime_debug_sessions import RuntimeDebugSessions
from odin_backend.core.autonomous_debugging.stack_reasoner import reason
from odin_backend.core.autonomous_debugging.test_failure_mapper import map_failures
from odin_backend.core.autonomous_debugging.trace_analyzer import analyze


class AutonomousDebuggingPipelineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions = RuntimeDebugSessions()

    async def analyze(self, *, stacktrace: str, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_debugging_enabled", False):
            return {"accepted": False, "reason": "autonomous_debugging_disabled"}
        traced = analyze(stacktrace)
        stacked = reason(traced.get("frames", []))
        clusters = cluster([traced.get("error", "")])
        if clusters.get("repeated"):
            self._emit("debug_cluster_created", clusters)
        hypothesis = hypothesize(cause=traced.get("error", ""), file=stacked.get("root_frame", "unknown"))
        risk = predict(diff_size=len(stacktrace), tests_touched=1)
        if risk.get("regression_likely"):
            self._emit("regression_risk_detected", risk)
        self._emit("patch_hypothesis_generated", hypothesis)
        confidence = 0.62
        g = gate(confidence=confidence)
        base = {}
        if hasattr(self._app, "autonomous_debugging"):
            base = await self._app.autonomous_debugging.analyze(stacktrace=stacktrace, repo=repo)
        return {
            "accepted": True,
            "trace": traced,
            "stack": stacked,
            "clusters": clusters,
            "hypothesis": hypothesis,
            "risk": risk,
            "gate": g,
            "base_analysis": base,
            "supervised": True,
            "auto_patch": False,
        }

    async def map_tests(self, *, tests: list[str]) -> dict[str, Any]:
        mapped = map_failures(tests)
        return {"accepted": True, **mapped}

    def snapshot(self) -> dict[str, Any]:
        return {"pipeline": "autonomous_debugging_v2"}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_debugging_pipeline")
