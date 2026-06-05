"""Unified cognitive state — single source of truth (kernel write authority only)."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.priority.engine import PriorityItem


class CognitiveState(BaseModel):
    """
    Single source of truth for ODIN runtime cognition.

    All subsystems READ this object; only OdinCognitiveKernel commits writes.
    """

    # --- Prompt 9 required fields ---
    active_signals: list[dict[str, Any]] = Field(default_factory=list)
    task_graph: dict[str, Any] = Field(default_factory=lambda: {"node_count": 0, "nodes": {}})
    priority_queue: list[dict[str, Any]] = Field(default_factory=list)
    coherence_snapshot: dict[str, Any] = Field(
        default_factory=lambda: {"score": 1.0, "conflicts": [], "suggestions": [], "affected": []}
    )
    autonomy_state: dict[str, Any] = Field(default_factory=dict)
    memory_context: dict[str, Any] = Field(default_factory=dict)
    active_agents: dict[str, Any] = Field(default_factory=dict)
    execution_log: list[dict[str, Any]] = Field(default_factory=list)
    system_health: dict[str, Any] = Field(
        default_factory=lambda: {"status": "healthy", "degraded": False}
    )
    last_stability_check: datetime | None = None

    # --- Milestone 11 live mind observability ---
    reasoning_trace: list[dict[str, Any]] = Field(default_factory=list)
    model_used: str | None = None
    decision_path: list[str] = Field(default_factory=list)
    memory_delta: dict[str, Any] = Field(default_factory=dict)
    graph_delta: dict[str, Any] = Field(default_factory=dict)
    environment_snapshot: dict[str, Any] = Field(default_factory=dict)
    execution_gate_decision: str | None = None
    valkyrie_action_trace: list[str] = Field(default_factory=list)

    # --- Focus & trace (retained for API/UX) ---
    current_focus: str = "Initializing cognitive kernel"
    active_context: dict[str, Any] = Field(default_factory=dict)
    recommended_actions: list[dict[str, Any]] = Field(default_factory=list)
    graph_summary: dict[str, Any] = Field(default_factory=dict)
    last_signal: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signal_count: int = 0

    # Runtime stability observability (Prompt 13)
    recursion_events_detected: int = 0
    suppressed_signal_count: int = 0
    runtime_loop_health: str = "healthy"
    active_signal_chains: int = 0
    kernel_processing_rate: float = 0.0

    # Milestone 14 — persistent missions
    active_missions: list[dict[str, Any]] = Field(default_factory=list)
    mission_execution_rate: float = 0.0
    mission_failures: int = 0
    mission_retries: int = 0
    mission_checkpoint_count: int = 0
    long_horizon_focus: str | None = None

    # Milestone 15 — active perception
    environment_awareness: dict[str, Any] = Field(default_factory=dict)
    active_perceptions: list[dict[str, Any]] = Field(default_factory=list)
    adaptive_actions: list[dict[str, Any]] = Field(default_factory=list)
    failure_patterns: dict[str, int] = Field(default_factory=dict)
    confidence_score: float = 1.0
    mission_stability_score: float = 1.0
    execution_recovery_rate: float = 1.0

    # Legacy mirrors (kept for backward-compatible consumers)
    priority_tasks: list[dict[str, Any]] = Field(default_factory=list)
    execution_decisions: list[dict[str, Any]] = Field(default_factory=list)
    coherence_score: float = 1.0
    coherence_conflicts: list[str] = Field(default_factory=list)
    coherence_suggestions: list[str] = Field(default_factory=list)

    def apply_priorities(self, items: list[PriorityItem]) -> None:
        dumped = [i.model_dump(mode="json") for i in items]
        self.priority_queue = dumped
        self.priority_tasks = dumped
        if items:
            self.current_focus = items[0].title

    def apply_coherence(self, report: Any) -> None:
        self.coherence_snapshot = {
            "score": report.coherence_score,
            "conflicts": report.conflict_report,
            "suggestions": report.resolution_suggestions,
            "affected": report.affected_systems,
        }
        self.coherence_score = report.coherence_score
        self.coherence_conflicts = report.conflict_report
        self.coherence_suggestions = report.resolution_suggestions

    def apply_perception_metrics(self, metrics: dict[str, Any]) -> None:
        self.environment_awareness = dict(metrics.get("environment_awareness", {}))
        self.active_perceptions = list(metrics.get("active_perceptions", []))[:20]
        self.adaptive_actions = list(metrics.get("adaptive_actions", []))[:20]
        self.failure_patterns = dict(metrics.get("failure_patterns", {}))
        self.confidence_score = float(metrics.get("confidence_score", 1.0))
        self.mission_stability_score = float(metrics.get("mission_stability_score", 1.0))
        self.execution_recovery_rate = float(metrics.get("execution_recovery_rate", 1.0))
        self.system_health["confidence_score"] = self.confidence_score

    def apply_mission_metrics(self, metrics: dict[str, Any]) -> None:
        self.active_missions = list(metrics.get("active_missions", []))
        self.mission_execution_rate = float(metrics.get("mission_execution_rate", 0.0))
        self.mission_failures = int(metrics.get("mission_failures", 0))
        self.mission_retries = int(metrics.get("mission_retries", 0))
        self.mission_checkpoint_count = int(metrics.get("mission_checkpoint_count", 0))
        focus = metrics.get("long_horizon_focus")
        if focus:
            self.long_horizon_focus = str(focus)
        self.system_health["active_missions"] = len(self.active_missions)
        self.system_health["mission_failures"] = self.mission_failures

    def apply_runtime_metrics(self, metrics: dict[str, Any]) -> None:
        self.recursion_events_detected = int(metrics.get("recursion_events_detected", 0))
        self.suppressed_signal_count = int(metrics.get("suppressed_signal_count", 0))
        self.runtime_loop_health = str(metrics.get("runtime_loop_health", "healthy"))
        self.active_signal_chains = int(metrics.get("active_signal_chains", 0))
        self.kernel_processing_rate = float(metrics.get("kernel_processing_rate", 0.0))
        self.system_health["runtime_loop_health"] = self.runtime_loop_health
        self.system_health["recursion_events"] = self.recursion_events_detected
        self.system_health["suppressed_signals"] = self.suppressed_signal_count

    def append_execution_step(self, step: str, detail: dict[str, Any]) -> None:
        entry = {
            "step": step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **detail,
        }
        self.execution_log.append(entry)
        if len(self.execution_log) > 100:
            self.execution_log = self.execution_log[-100:]
