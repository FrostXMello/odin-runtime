"""Root-cause analysis for runtime failures and stalls."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.missions.health import assess_orchestration_health
from odin_backend.core.missions.lifecycle import DISPATCHABLE_MISSION_STATES, migrate_legacy_state
from odin_backend.core.observability.store import CausalEventStore
from odin_backend.core.observability.events import TraceEventKind
from odin_backend.models.mission import MissionLifecycle
from odin_backend.models.task_graph import TaskNodeStatus


class RootCauseFinding(BaseModel):
    issue: str
    probable_cause: str
    affected_components: list[str] = Field(default_factory=list)
    recommended_action: str
    severity: str = "medium"  # low | medium | high | critical
    evidence: dict[str, Any] = Field(default_factory=dict)


class RuntimeDiagnosticsReport(BaseModel):
    generated_at: str
    status: str
    findings: list[RootCauseFinding] = Field(default_factory=list)
    summary: str = ""
    issue_count: int = 0


def analyze_runtime(app: Any) -> RuntimeDiagnosticsReport:
    from datetime import datetime, timezone

    findings: list[RootCauseFinding] = []
    manager = app.mission_manager
    orch = assess_orchestration_health(app)
    store: CausalEventStore = app.observability.tracer.store

    active = list(manager._active.values())  # noqa: SLF001
    dispatchable = [
        m for m in active if migrate_legacy_state(m.current_state) in DISPATCHABLE_MISSION_STATES
    ]

    if orch.zero_throughput and orch.active_execution_count > 0:
        findings.append(
            RootCauseFinding(
                issue="zero_execution_throughput",
                probable_cause="Dispatcher not running, approval gates, or all missions blocked",
                affected_components=["execution_dispatcher", "mission_runtime"],
                recommended_action="Enable mission_dispatch_enabled; check approval_required missions",
                severity="critical",
                evidence={"dispatchable": len(dispatchable)},
            )
        )

    if orch.duplicate_loop_detected:
        findings.append(
            RootCauseFinding(
                issue="duplicate_mission_loop",
                probable_cause="Upstream signal or API repeatedly creating identical missions",
                affected_components=["mission_manager", "deduplicator"],
                recommended_action="Fix signal source; verify dedup fingerprint on create",
                severity="medium",
                evidence={"duplicate_suppression_count": orch.duplicate_suppression_count},
            )
        )

    failed_missions = [
        m.mission_id
        for m in active
        if migrate_legacy_state(m.current_state) == MissionLifecycle.FAILED
    ]
    if failed_missions:
        findings.append(
            RootCauseFinding(
                issue="mission_failed",
                probable_cause="One or more missions reached a terminal failed state",
                affected_components=["mission_runtime", "task_graph"],
                recommended_action="Inspect failed mission timelines; retry or cancel as needed",
                severity="critical",
                evidence={"mission_ids": failed_missions[:10]},
            )
        )

    for m in active:
        if migrate_legacy_state(m.current_state) != MissionLifecycle.BLOCKED:
            continue
        recovery_attempts = _count_mission_kind(
            store, m.mission_id, TraceEventKind.RETRY_TRIGGERED, window=100
        )
        if recovery_attempts > 2:
            findings.append(
                RootCauseFinding(
                    issue="mission_blocked_persistent",
                    probable_cause="Mission blocked after repeated recovery attempts",
                    affected_components=["mission_runtime", "recovery"],
                    recommended_action="Escalate or cancel the mission; inspect root blocker",
                    severity="critical",
                    evidence={"mission_id": m.mission_id, "recovery_attempts": recovery_attempts},
                )
            )

    stuck_missions = []
    for m in dispatchable:
        executing = [
            n
            for n in m.task_graph.nodes.values()
            if n.status in (TaskNodeStatus.EXECUTING, TaskNodeStatus.ASSIGNED, TaskNodeStatus.RUNNING)
        ]
        pending = [n for n in m.task_graph.nodes.values() if n.status in (TaskNodeStatus.PENDING, TaskNodeStatus.READY)]
        if pending and not executing and not m.task_graph.ready_nodes():
            stuck_missions.append(m.mission_id)

    if stuck_missions:
        findings.append(
            RootCauseFinding(
                issue="stalled_missions",
                probable_cause="Dependency deadlock or blocked upstream tasks",
                affected_components=["task_graph", "mission_runtime"],
                recommended_action="Inspect task dependencies; resume or cancel blocked missions",
                severity="high" if len(stuck_missions) >= 3 else "medium",
                evidence={"mission_ids": stuck_missions[:10]},
            )
        )

    retry_storm = _count_recent_kind(store, TraceEventKind.RETRY_TRIGGERED, window=50)
    if retry_storm >= 10:
        findings.append(
            RootCauseFinding(
                issue="retry_storm",
                probable_cause="Repeated task failures triggering replan/retry loop",
                affected_components=["mission_runtime", "feedback", "confidence"],
                recommended_action="Escalate mission; reduce concurrency; inspect tool failures",
                severity="medium",
                evidence={"retry_events": retry_storm},
            )
        )

    policy_blocks = _count_recent_kind(store, TraceEventKind.POLICY_BLOCKED, window=50)
    if policy_blocks >= 3:
        findings.append(
            RootCauseFinding(
                issue="policy_bottleneck",
                probable_cause="Dangerous objectives or restricted tools awaiting approval",
                affected_components=["execution_policy", "mission_manager"],
                recommended_action="Approve missions explicitly or adjust objectives",
                severity="low",
                evidence={"policy_blocks": policy_blocks},
            )
        )

    queue_depth = int(getattr(app.mission_dispatcher, "metrics", {}).get("queue_depth", 0))
    if queue_depth > 30:
        findings.append(
            RootCauseFinding(
                issue="queue_starvation",
                probable_cause="Dispatcher saturation or slow wave execution",
                affected_components=["mission_scheduler", "execution_dispatcher"],
                recommended_action="Increase mission_max_concurrent_missions or reduce cooldown",
                severity="low",
                evidence={"queue_depth": queue_depth},
            )
        )

    planner_loops = _detect_planner_recursion(store)
    if planner_loops:
        findings.append(
            RootCauseFinding(
                issue="recursive_planning_loop",
                probable_cause="Replan triggered faster than task completion",
                affected_components=["mission_planner", "mission_runtime"],
                recommended_action="Cap replans; fix failing tasks before replan",
                severity="high",
                evidence={"missions": planner_loops[:5]},
            )
        )

    critical_findings = [f for f in findings if f.severity == "critical"]
    issue_count = len(critical_findings)

    status = "healthy"
    if critical_findings:
        status = "critical"
    elif any(f.severity in ("high", "medium") for f in findings):
        status = "degraded"

    summary = (
        "No issues detected"
        if issue_count == 0
        else f"{issue_count} critical issue(s) detected"
    )
    return RuntimeDiagnosticsReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        status=status,
        findings=findings,
        summary=summary,
        issue_count=issue_count,
    )


def _count_recent_kind(store: CausalEventStore, kind: TraceEventKind, *, window: int) -> int:
    return sum(1 for e in store.recent(window) if e.kind == kind)


def _count_mission_kind(
    store: CausalEventStore, mission_id: str, kind: TraceEventKind, *, window: int
) -> int:
    return sum(1 for e in store.recent(window) if e.kind == kind and e.mission_id == mission_id)


def _detect_planner_recursion(store: CausalEventStore) -> list[str]:
    from collections import Counter

    c: Counter[str] = Counter()
    for e in store.recent(200):
        if e.kind == TraceEventKind.RETRY_TRIGGERED and e.mission_id:
            c[e.mission_id] += 1
    return [mid for mid, n in c.items() if n >= 5]
