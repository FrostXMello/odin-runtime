"""Validation fabric orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.validation_fabric.confidence_gates import check_confidence_gate
from odin_backend.core.validation_fabric.engineering_quality_score import score_engineering
from odin_backend.core.validation_fabric.isolated_test_runner import run_isolated
from odin_backend.core.validation_fabric.patch_benchmarking import benchmark_patch
from odin_backend.core.validation_fabric.regression_matrix import build_regression_matrix
from odin_backend.core.validation_fabric.runtime_validation import validate_runtime


class ValidationFabricRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def validate_patch(self, *, before: str, after: str, confidence: float) -> dict[str, Any]:
        if not getattr(self._app.settings, "validation_fabric_enabled", False):
            return {"accepted": False, "reason": "validation_fabric_disabled"}
        matrix = build_regression_matrix(before=before, after=after)
        bench = benchmark_patch(before=before, after=after)
        gate = check_confidence_gate(confidence=confidence, min_confidence=0.55)
        runtime = validate_runtime()
        quality = score_engineering(patch_score=bench["score"], gate_passed=gate["passed"])
        isolated = run_isolated(test_pattern="test_*")
        return {
            "accepted": True,
            "matrix": matrix,
            "benchmark": bench,
            "gate": gate,
            "runtime": runtime,
            "quality": quality,
            "isolated_tests": isolated,
            "approval_required": not gate["passed"],
        }

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": getattr(self._app.settings, "validation_fabric_enabled", False)}
