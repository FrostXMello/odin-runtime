"""Execution-aware orchestration health."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.missions.lifecycle import DISPATCHABLE_MISSION_STATES, migrate_legacy_state


class OrchestrationHealthReport(BaseModel):
    status: str = "healthy"  # healthy | degraded | critical
    execution_throughput: float = 0.0
    completion_rate: float = 0.0
    stuck_mission_count: int = 0
    duplicate_suppression_count: int = 0
    active_execution_count: int = 0
    retry_frequency: float = 0.0
    escalation_rate: float = 0.0
    worker_responsive: bool = True
    queue_depth: int = 0
    pickup_latency_ms: float = 0.0
    worker_utilization: float = 0.0
    zero_throughput: bool = False
    duplicate_loop_detected: bool = False
    warnings: list[str] = Field(default_factory=list)


def assess_orchestration_health(app: Any) -> OrchestrationHealthReport:
    manager = app.mission_manager
    dispatcher = getattr(app, "mission_dispatcher", None)
    dedup = getattr(manager, "deduplicator", None)
    runtime_metrics = app.mission_runtime.metrics

    active_missions = list(manager._active.values())  # noqa: SLF001
    dispatchable = 0
    stuck = 0
    for m in active_missions:
        st = migrate_legacy_state(m.current_state)
        if st in DISPATCHABLE_MISSION_STATES:
            dispatchable += 1
        pending = len([t for t in m.active_tasks if t.status in ("pending", "ready")])
        if pending > 0 and st in DISPATCHABLE_MISSION_STATES:
            age = (m.updated_at.timestamp())
            import time

            if time.time() - age > app.settings.mission_stuck_task_seconds:
                stuck += 1

    waves = int(runtime_metrics.get("waves_executed", 0))
    completed = int(runtime_metrics.get("tasks_completed", 0))
    failed = int(runtime_metrics.get("tasks_failed", 0))
    retries = int(runtime_metrics.get("retries", 0))
    escalations = int(runtime_metrics.get("escalations", 0))

    throughput = float(completed) / max(1.0, waves) if waves else 0.0
    total_tasks = completed + failed
    completion_rate = completed / max(1, total_tasks) if total_tasks else 0.0
    retry_freq = retries / max(1, total_tasks) if total_tasks else 0.0
    esc_rate = escalations / max(1, len(active_missions)) if active_missions else 0.0

    dup_count = 0
    if dedup:
        dup_count = dedup.metrics.get("duplicate_suppressed_count", 0) + dedup.metrics.get(
            "duplicate_detected_count", 0
        )

    d_metrics = dispatcher.metrics if dispatcher else {}
    queue_depth = int(d_metrics.get("queue_depth", 0))
    pickup_ms = float(d_metrics.get("avg_pickup_latency_ms", 0))
    worker_util = float(d_metrics.get("worker_utilization", 0))
    last_tick = d_metrics.get("last_tick_at")
    worker_responsive = last_tick is not None

    zero_throughput = dispatchable > 0 and waves == 0 and completed == 0
    duplicate_loop = dup_count > 10 and dispatchable > 5

    report = OrchestrationHealthReport(
        execution_throughput=round(throughput, 4),
        completion_rate=round(completion_rate, 4),
        stuck_mission_count=stuck,
        duplicate_suppression_count=dup_count,
        active_execution_count=dispatchable,
        retry_frequency=round(retry_freq, 4),
        escalation_rate=round(esc_rate, 4),
        worker_responsive=worker_responsive,
        queue_depth=queue_depth,
        pickup_latency_ms=pickup_ms,
        worker_utilization=worker_util,
        zero_throughput=zero_throughput,
        duplicate_loop_detected=duplicate_loop,
    )

    if zero_throughput or stuck >= 3 or duplicate_loop:
        report.status = "critical"
        if zero_throughput:
            report.warnings.append("execution throughput zero with dispatchable missions")
        if stuck >= 3:
            report.warnings.append(f"{stuck} missions appear stuck")
        if duplicate_loop:
            report.warnings.append("duplicate mission loop detected")
    elif stuck > 0 or queue_depth > 20 or completion_rate < 0.3:
        report.status = "degraded"
        if stuck:
            report.warnings.append("stuck missions present")
        if queue_depth > 20:
            report.warnings.append("dispatcher queue depth high")

    return report
