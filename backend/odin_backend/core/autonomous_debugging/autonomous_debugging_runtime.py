"""Autonomous debugging orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.autonomous_debugging.debugging_workflows import build_workflow
from odin_backend.core.autonomous_debugging.failure_localizer import localize_failure
from odin_backend.core.autonomous_debugging.fix_strategy_selector import select_strategy
from odin_backend.core.autonomous_debugging.patch_validator import validate_patch
from odin_backend.core.autonomous_debugging.regression_detector import detect_regression
from odin_backend.core.autonomous_debugging.root_cause_engine import analyze_root_cause
from odin_backend.core.autonomous_debugging.runtime_bug_replayer import replay_failure
from odin_backend.core.autonomous_debugging.stacktrace_reasoner import reason_stacktrace


class AutonomousDebuggingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cases: list[dict] = []

    async def analyze(self, *, stacktrace: str, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_debugging_enabled", False):
            return {"accepted": False, "reason": "autonomous_debugging_disabled"}
        traced = reason_stacktrace(stacktrace)
        localized = localize_failure(stacktrace=stacktrace, frames=traced.get("frames", []))
        root = analyze_root_cause(error=traced.get("error", ""), location=localized.get("file"))
        strategy = select_strategy(root_cause=root.get("cause", ""), prior_failures=0)
        workflow = build_workflow(strategy=strategy["strategy"])
        confidence = round(min(0.95, 0.4 + root.get("confidence", 0) * 0.5), 3)
        self._cases.append({"repo": repo, "confidence": confidence})
        self._emit("bug_localized", {"file": localized.get("file"), "confidence": confidence})
        self._emit("debugging_strategy_selected", strategy)
        return {
            "accepted": True,
            "trace": traced,
            "localized": localized,
            "root_cause": root,
            "strategy": strategy,
            "workflow": workflow,
            "confidence": confidence,
            "supervised": True,
        }

    async def replay(self, *, command: str) -> dict[str, Any]:
        result = replay_failure(command=command)
        return {"accepted": True, **result}

    async def validate_fix(self, *, diff: str, baseline: str) -> dict[str, Any]:
        validated = validate_patch(diff=diff)
        regression = detect_regression(before=baseline, after=diff)
        if regression.get("regression"):
            self._emit("regression_detected", regression)
        else:
            self._emit("patch_validated", validated)
        return {"accepted": True, "validation": validated, "regression": regression}

    def snapshot(self) -> dict[str, Any]:
        return {"cases": len(self._cases)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_debugging")
