"""Execution feedback — outcome analysis and adaptive responses."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.perception import PerceptionCategory, PerceptionRecord


class OutcomeClass(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    REPEATED_FAILURE = "repeated_failure"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class FailureClass(StrEnum):
    TOOL_ERROR = "tool_error"
    GOVERNANCE_BLOCK = "governance_block"
    ENVIRONMENT_UNSTABLE = "environment_unstable"
    TIMEOUT = "timeout"
    REPEATED = "repeated"
    UNKNOWN = "unknown"


class AdaptiveAction(BaseModel):
    action: str
    reason: str
    priority: int = 50
    payload: dict[str, Any] = Field(default_factory=dict)


class FeedbackReport(BaseModel):
    outcome: OutcomeClass
    failure_class: FailureClass | None = None
    perceptions: list[PerceptionRecord] = Field(default_factory=list)
    recommended_actions: list[AdaptiveAction] = Field(default_factory=list)
    confidence_decay: dict[str, float] = Field(default_factory=dict)
    should_replan: bool = False
    should_rollback: bool = False
    should_switch_strategy: bool = False


class OutcomeAnalyzer:
    def analyze(
        self,
        *,
        success: bool,
        tool: str,
        output: dict[str, Any] | None = None,
        partial: bool = False,
    ) -> OutcomeClass:
        if partial:
            return OutcomeClass.PARTIAL
        if success:
            return OutcomeClass.SUCCESS
        if output and output.get("blocked"):
            return OutcomeClass.BLOCKED
        return OutcomeClass.FAILURE


class FailureClassifier:
    def classify(
        self,
        *,
        tool: str,
        reason: str,
        repeat_count: int = 0,
    ) -> FailureClass:
        r = reason.lower()
        if repeat_count >= 3:
            return FailureClass.REPEATED
        if "governor" in r or "gate" in r or "coherence" in r:
            return FailureClass.GOVERNANCE_BLOCK
        if "browser" in tool or "desktop" in r:
            return FailureClass.ENVIRONMENT_UNSTABLE
        if "timeout" in r:
            return FailureClass.TIMEOUT
        if repeat_count >= 2:
            return FailureClass.REPEATED
        return FailureClass.TOOL_ERROR


class AdaptiveResponsePlanner:
    def plan(
        self,
        outcome: OutcomeClass,
        failure_class: FailureClass | None,
        *,
        tool: str = "",
        repeat_count: int = 0,
        mission_id: str | None = None,
    ) -> list[AdaptiveAction]:
        actions: list[AdaptiveAction] = []
        if outcome == OutcomeClass.SUCCESS:
            return actions

        if failure_class == FailureClass.REPEATED or outcome == OutcomeClass.REPEATED_FAILURE:
            actions.append(
                AdaptiveAction(
                    action="switch_strategy",
                    reason=f"Repeated failures on {tool}",
                    priority=90,
                    payload={"tool": tool, "mission_id": mission_id},
                )
            )
            actions.append(
                AdaptiveAction(
                    action="reduce_concurrency",
                    reason="Instability detected",
                    priority=85,
                )
            )

        if failure_class == FailureClass.ENVIRONMENT_UNSTABLE:
            actions.append(
                AdaptiveAction(
                    action="switch_strategy",
                    reason="Environment unstable — alternate path",
                    priority=80,
                    payload={"from_tool": tool},
                )
            )

        if outcome in (OutcomeClass.FAILURE, OutcomeClass.PARTIAL):
            actions.append(
                AdaptiveAction(
                    action="replan",
                    reason="Execution outcome requires replan",
                    priority=70,
                )
            )

        if repeat_count >= 2:
            actions.append(
                AdaptiveAction(
                    action="escalate",
                    reason="Failure threshold exceeded",
                    priority=95,
                )
            )

        return actions


class ExecutionFeedbackEngine:
    def __init__(self) -> None:
        self._analyzer = OutcomeAnalyzer()
        self._classifier = FailureClassifier()
        self._planner = AdaptiveResponsePlanner()
        self._failure_counts: dict[str, int] = {}

    def process(
        self,
        *,
        success: bool,
        tool: str = "noop",
        reason: str = "",
        output: dict[str, Any] | None = None,
        mission_id: str | None = None,
        task_id: str | None = None,
        partial: bool = False,
    ) -> FeedbackReport:
        key = f"{mission_id}:{tool}:{task_id or ''}"
        if not success:
            self._failure_counts[key] = self._failure_counts.get(key, 0) + 1
        else:
            self._failure_counts[key] = max(0, self._failure_counts.get(key, 0) - 1)

        repeat_count = self._failure_counts.get(key, 0)
        outcome = self._analyzer.analyze(
            success=success, tool=tool, output=output, partial=partial
        )
        if repeat_count >= 3:
            outcome = OutcomeClass.REPEATED_FAILURE

        failure_class = None
        if not success:
            failure_class = self._classifier.classify(
                tool=tool, reason=reason, repeat_count=repeat_count
            )

        actions = self._planner.plan(
            outcome,
            failure_class,
            tool=tool,
            repeat_count=repeat_count,
            mission_id=mission_id,
        )

        perceptions: list[PerceptionRecord] = []
        category = PerceptionCategory.EXECUTION_RESULT
        if not success:
            category = (
                PerceptionCategory.FAILURE_DETECTED
                if repeat_count >= 2
                else PerceptionCategory.EXECUTION_RESULT
            )

        perceptions.append(
            PerceptionRecord(
                category=category,
                source="execution_feedback",
                mission_id=mission_id,
                task_id=task_id,
                tool=tool,
                summary=f"{outcome.value}: {tool}",
                payload={"reason": reason, "repeat_count": repeat_count},
                confidence_impact=-0.1 if not success else 0.05,
            )
        )

        decay = {}
        if not success:
            decay = {"execution": 0.08, "tool": 0.1, "stability": 0.05 * repeat_count}

        return FeedbackReport(
            outcome=outcome,
            failure_class=failure_class,
            perceptions=perceptions,
            recommended_actions=actions,
            confidence_decay=decay,
            should_replan=any(a.action == "replan" for a in actions),
            should_rollback=repeat_count >= 4,
            should_switch_strategy=any(a.action == "switch_strategy" for a in actions),
        )
