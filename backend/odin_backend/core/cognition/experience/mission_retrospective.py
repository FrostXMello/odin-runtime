"""Mission retrospective generation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.models.mission import Mission


def build_retrospective(
    mission: Mission,
    *,
    outcome_analysis: dict[str, Any],
    success_patterns: list[dict[str, Any]],
    failure_clusters: list[dict[str, Any]],
    tool_chains: list[dict[str, Any]],
    confidence_drift: dict[str, float] | None = None,
) -> dict[str, Any]:
    completed = len(mission.completed_tasks)
    failed = len(mission.blocked_tasks)
    retries = mission.retry_count + sum(t.retry_count for t in mission.active_tasks)
    return {
        "mission_id": mission.mission_id,
        "objective": mission.objective[:300],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "final_state": mission.current_state.value,
        "succeeded": {
            "tasks_completed": completed,
            "patterns": success_patterns[:5],
            "tool_chains": tool_chains[:5],
        },
        "failed": {
            "blocked_tasks": failed,
            "clusters": failure_clusters[:5],
        },
        "bottlenecks": outcome_analysis.get("bottlenecks", []),
        "wasted_retries": max(0, retries - outcome_analysis.get("failures", 0)),
        "latency": {"avg_ms": outcome_analysis.get("avg_latency_ms")},
        "confidence_drift": confidence_drift or mission.confidence,
        "execution_strategy": mission.execution_strategy,
        "adaptation_count": len(mission.adaptation_log),
    }
