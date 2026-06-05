"""Cognitive confidence model — mission/task/execution certainty."""

from pydantic import BaseModel, Field


class ConfidenceSnapshot(BaseModel):
    execution_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    environmental_certainty: float = Field(default=0.8, ge=0.0, le=1.0)
    reasoning_confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    tool_reliability: float = Field(default=0.8, ge=0.0, le=1.0)
    mission_stability: float = Field(default=0.85, ge=0.0, le=1.0)

    @property
    def aggregate(self) -> float:
        weights = (0.3, 0.2, 0.15, 0.2, 0.15)
        vals = (
            self.execution_confidence,
            self.environmental_certainty,
            self.reasoning_confidence,
            self.tool_reliability,
            self.mission_stability,
        )
        return round(sum(w * v for w, v in zip(weights, vals)), 4)

    def decay(self, *, execution: float = 0.0, environment: float = 0.0, tool: float = 0.0, stability: float = 0.0) -> "ConfidenceSnapshot":
        return ConfidenceSnapshot(
            execution_confidence=max(0.0, self.execution_confidence - execution),
            environmental_certainty=max(0.0, self.environmental_certainty - environment),
            reasoning_confidence=self.reasoning_confidence,
            tool_reliability=max(0.0, self.tool_reliability - tool),
            mission_stability=max(0.0, self.mission_stability - stability),
        )

    def reinforce(self, *, execution: float = 0.0, stability: float = 0.0) -> "ConfidenceSnapshot":
        return ConfidenceSnapshot(
            execution_confidence=min(1.0, self.execution_confidence + execution),
            environmental_certainty=self.environmental_certainty,
            reasoning_confidence=min(1.0, self.reasoning_confidence + 0.02),
            tool_reliability=min(1.0, self.tool_reliability + execution * 0.5),
            mission_stability=min(1.0, self.mission_stability + stability),
        )


class ConfidenceTracker:
    """Global and per-mission confidence tracking."""

    def __init__(self) -> None:
        self._global = ConfidenceSnapshot()
        self._missions: dict[str, ConfidenceSnapshot] = {}
        self._tool_failures: dict[str, int] = {}

    @property
    def global_snapshot(self) -> ConfidenceSnapshot:
        return self._global.model_copy()

    def for_mission(self, mission_id: str) -> ConfidenceSnapshot:
        return self._missions.setdefault(mission_id, ConfidenceSnapshot()).model_copy()

    def set_mission(self, mission_id: str, snap: ConfidenceSnapshot) -> None:
        self._missions[mission_id] = snap

    def record_tool_outcome(self, tool: str, success: bool) -> None:
        if success:
            self._tool_failures[tool] = max(0, self._tool_failures.get(tool, 0) - 1)
            self._global = self._global.reinforce(execution=0.03)
        else:
            self._tool_failures[tool] = self._tool_failures.get(tool, 0) + 1
            penalty = min(0.25, 0.05 * self._tool_failures[tool])
            self._global = self._global.decay(tool=penalty, execution=penalty * 0.5)

    def failure_rate(self, tool: str) -> float:
        fails = self._tool_failures.get(tool, 0)
        return min(1.0, fails / 5.0)

    def should_escalate(self, mission_id: str | None = None) -> bool:
        snap = self.for_mission(mission_id) if mission_id else self._global
        return snap.aggregate < 0.35

    def replan_frequency_boost(self, mission_id: str) -> bool:
        return self.for_mission(mission_id).mission_stability < 0.5
