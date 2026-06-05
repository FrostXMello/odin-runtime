"""Unified observability hub — tracing, timelines, memory audit, signal graph."""

from __future__ import annotations

from typing import Any

from odin_backend.core.observability.diagnostics import RuntimeDiagnosticsReport, analyze_runtime
from odin_backend.core.observability.memory_audit import MemoryMutationAudit
from odin_backend.core.observability.metrics import ObservabilityMetrics
from odin_backend.core.observability.signal_graph import SignalLineageTracker
from odin_backend.core.observability.tracer import CausalTracer
from odin_backend.core.streaming.bridge import StreamBridge
from odin_backend.core.streaming.event_bus import StreamingEventBus
from odin_backend.monitoring.metrics import MetricsCollector


class ObservabilityHub:
    def __init__(
        self,
        metrics: MetricsCollector | None = None,
        *,
        stream_bus: StreamingEventBus | None = None,
    ) -> None:
        self.stream_bus = stream_bus or StreamingEventBus()
        self.stream_bridge = StreamBridge(self.stream_bus)
        self.tracer = CausalTracer(on_record=self.stream_bridge.on_trace_recorded)
        self.memory_audit = MemoryMutationAudit()
        self.signal_graph = SignalLineageTracker()
        self.metrics = ObservabilityMetrics(metrics)

    def analyze(self, app: Any) -> RuntimeDiagnosticsReport:
        return analyze_runtime(app)

    def introspection_snapshot(self, app: Any) -> dict[str, Any]:
        manager = app.mission_manager
        dispatcher = getattr(app, "mission_dispatcher", None)
        worker = app.mission_worker
        scheduler = worker.scheduler

        executing: list[dict] = []
        blocked: list[dict] = []
        pending: list[dict] = []
        policy_blocked: list[dict] = []
        retry_queue: list[str] = []

        for mission in list(manager._active.values()):  # noqa: SLF001
            from odin_backend.core.missions.lifecycle import migrate_legacy_state
            from odin_backend.models.mission import MissionLifecycle

            st = migrate_legacy_state(mission.current_state)
            if st == MissionLifecycle.APPROVAL_REQUIRED:
                policy_blocked.append(
                    {"mission_id": mission.mission_id, "objective": mission.objective[:80]}
                )
            for node in mission.task_graph.nodes.values():
                entry = {
                    "mission_id": mission.mission_id,
                    "task_id": node.id,
                    "goal": node.goal[:60],
                    "status": node.status.value,
                    "agent": node.assigned_agent,
                }
                if node.status.value in ("executing", "running", "assigned"):
                    executing.append(entry)
                elif node.status.value == "blocked":
                    blocked.append(entry)
                elif node.status.value in ("pending", "ready"):
                    pending.append(entry)

        d_metrics = dispatcher.metrics if dispatcher else {}
        return {
            "active_missions": manager.active_count(),
            "dispatchable_missions": manager.dispatchable_count(),
            "queue_depth": scheduler.backlog_depth(),
            "dispatcher": d_metrics,
            "executing_tasks": executing,
            "blocked_tasks": blocked,
            "pending_tasks": pending[:50],
            "policy_blocked_missions": policy_blocked,
            "retry_queue_size": len(getattr(scheduler, "_retry_queue", [])),
            "trace_store": self.tracer.store.stats(),
            "memory_mutations_recent": len(self.memory_audit.recent(10)),
        }
