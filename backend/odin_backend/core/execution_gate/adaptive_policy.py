"""Adaptive execution policy — dynamic gate behavior under instability."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.confidence.model import ConfidenceSnapshot
from odin_backend.core.execution_gate.gate import ExecutionGate, GateDecision, GateResult
from odin_backend.core.governor.decisions import ExecutionRequest


class AdaptivePolicyState(BaseModel):
    concurrency_limit: int = 3
    checkpoint_interval: int = 1
    require_confirmation: bool = False
    pacing_delay_seconds: float = 0.0
    reasons: list[str] = Field(default_factory=list)


class AdaptiveExecutionPolicy:
    """Wraps ExecutionGate with confidence- and failure-aware adjustments."""

    def __init__(self, gate: ExecutionGate) -> None:
        self._gate = gate
        self._state = AdaptivePolicyState()

    @property
    def state(self) -> AdaptivePolicyState:
        return self._state.model_copy()

    def apply_instability(
        self,
        *,
        confidence: ConfidenceSnapshot,
        failure_count: int = 0,
        repeated_tool_failures: bool = False,
    ) -> AdaptivePolicyState:
        reasons: list[str] = []
        concurrency = 3
        checkpoint_every = 1
        require_confirm = False
        pacing = 0.0

        if confidence.aggregate < 0.5:
            concurrency = 1
            checkpoint_every = 1
            pacing = 2.0
            reasons.append("low_aggregate_confidence")

        if failure_count >= 2:
            concurrency = max(1, concurrency - 1)
            pacing += 1.5
            reasons.append("recent_failures")

        if repeated_tool_failures:
            require_confirm = True
            concurrency = 1
            reasons.append("repeated_tool_failures")

        if confidence.mission_stability < 0.4:
            checkpoint_every = 1
            reasons.append("unstable_mission")

        self._state = AdaptivePolicyState(
            concurrency_limit=concurrency,
            checkpoint_interval=checkpoint_every,
            require_confirmation=require_confirm,
            pacing_delay_seconds=pacing,
            reasons=reasons,
        )
        return self._state

    def validate(self, app: Any, request: ExecutionRequest) -> GateResult:
        result = self._gate.validate(app, request)
        if self._state.require_confirmation and result.decision == GateDecision.ALLOW:
            if not request.user_confirmed and request.tool_name not in (
                "get_system_info",
                "read_file",
                "list_directory",
                "noop",
            ):
                return GateResult(
                    decision=GateDecision.REQUIRE_CONFIRMATION,
                    reason="Adaptive policy requires confirmation under instability",
                    explainable={"policy": self._state.model_dump()},
                )
        return result
