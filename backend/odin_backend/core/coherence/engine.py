"""Coherence engine — consistency over completeness."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.core.context_graph.graph import GlobalContextGraph
from odin_backend.core.kernel.state import CognitiveState
from odin_backend.core.priority.engine import CognitivePriorityEngine


class CoherenceReport(BaseModel):
    coherence_score: float = 1.0
    conflict_report: list[str] = Field(default_factory=list)
    resolution_suggestions: list[str] = Field(default_factory=list)
    affected_systems: list[str] = Field(default_factory=list)


class CoherenceEngine:
    """Detect and resolve contradictory internal state."""

    def __init__(
        self,
        graph: GlobalContextGraph,
        priority: CognitivePriorityEngine,
        *,
        execution_threshold: float = 0.4,
    ) -> None:
        self._graph = graph
        self._priority = priority
        self._execution_threshold = execution_threshold
        self._last_report = CoherenceReport()
        self._memory_claims: dict[str, str] = {}

    def validate(
        self,
        state: CognitiveState,
        recent_signals: list[Signal],
        *,
        task_graph: Any = None,
    ) -> CoherenceReport:
        conflicts: list[str] = []
        suggestions: list[str] = []
        affected: list[str] = []
        score = 1.0

        # Contradictory workflow vs recommendation
        has_wf_fail = any("failed" in s.name for s in recent_signals if s.kind == SignalKind.WORKFLOW)
        has_rec = any(s.kind == SignalKind.RECOMMENDATION for s in recent_signals[-10:])
        if has_wf_fail and has_rec:
            conflicts.append("Active workflow failure conflicts with pending recommendations")
            suggestions.append("Suppress recommendations until workflow state is resolved")
            affected.extend(["workflow", "proactive"])
            score -= 0.2

        # Duplicate priority titles
        ranked = self._priority.rank(20)
        titles = [r.title for r in ranked]
        if len(titles) != len(set(titles)):
            conflicts.append("Duplicate priority entries detected")
            suggestions.append("Normalize priority queue — keep highest score only")
            affected.append("priority")
            score -= 0.15

        # Stale graph nodes (many nodes, low signal activity)
        snap = self._graph.snapshot()
        if snap.get("node_count", 0) > 100 and state.signal_count < 5:
            conflicts.append("Context graph may contain stale nodes relative to activity")
            suggestions.append("Prune stale graph nodes via stability loop")
            affected.append("context_graph")
            score -= 0.1

        # Memory contradiction tracking
        for s in recent_signals:
            if s.kind == SignalKind.MEMORY and "content" in str(s.payload):
                key = s.payload.get("memory_id", s.id)
                content = str(s.payload.get("content", ""))[:80]
                prev = self._memory_claims.get(str(key))
                if prev and prev != content:
                    conflicts.append(f"Contradictory memory update for {key}")
                    suggestions.append("Run memory refinement merge pass")
                    affected.append("memory")
                    score -= 0.25
                self._memory_claims[str(key)] = content

        # Task graph linkage — blocked nodes with running focus
        if task_graph is not None:
            from odin_backend.models.task_graph import TaskNodeStatus

            blocked = [
                n.id
                for n in task_graph.nodes.values()
                if n.status == TaskNodeStatus.BLOCKED
            ]
            running = [
                n.id
                for n in task_graph.nodes.values()
                if n.status == TaskNodeStatus.RUNNING
            ]
            if blocked and running:
                conflicts.append("Task graph has blocked nodes while other tasks are running")
                suggestions.append("Resolve blocked dependencies before continuing execution")
                affected.append("task_graph")
                score -= 0.2
            dup_goals = [n.goal for n in task_graph.nodes.values()]
            if len(dup_goals) != len(set(dup_goals)) and dup_goals:
                conflicts.append("Duplicate goals in task graph")
                suggestions.append("Merge duplicate TaskNodes via kernel")
                affected.append("task_graph")
                score -= 0.1

        # Health vs focus mismatch
        if state.system_health.get("degraded") and "failure" not in state.current_focus.lower():
            conflicts.append("System degraded but focus does not reflect failure state")
            suggestions.append("Align current_focus with system_health")
            affected.append("kernel")
            score -= 0.1

        score = max(0.0, min(1.0, score))
        self._last_report = CoherenceReport(
            coherence_score=round(score, 3),
            conflict_report=conflicts,
            resolution_suggestions=suggestions,
            affected_systems=list(set(affected)),
        )
        return self._last_report

    @property
    def last_report(self) -> CoherenceReport:
        return self._last_report

    def blocks_execution(self, threshold: float | None = None) -> bool:
        t = threshold if threshold is not None else self._execution_threshold
        return self._last_report.coherence_score < t
