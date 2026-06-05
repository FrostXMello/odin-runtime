"""Causal tracer — structured events with async context propagation."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager, contextmanager
from uuid import uuid4
from typing import Any, AsyncIterator, Iterator

from odin_backend.core.observability.context import (
    CausalTraceContext,
    bind_context,
    current_context,
    ensure_context,
    reset_context,
)
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.observability.store import CausalEventStore
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_EVENT_LOG_MAP = {
    TraceEventKind.MISSION_CREATED: "mission_created",
    TraceEventKind.MISSION_DISPATCHED: "mission_dispatched",
    TraceEventKind.TASK_ASSIGNED: "task_assigned",
    TraceEventKind.TASK_STARTED: "task_started",
    TraceEventKind.TASK_COMPLETED: "task_completed",
    TraceEventKind.TASK_FAILED: "task_failed",
    TraceEventKind.RETRY_TRIGGERED: "retry_triggered",
    TraceEventKind.ESCALATION_TRIGGERED: "escalation_triggered",
    TraceEventKind.POLICY_BLOCKED: "policy_blocked",
    TraceEventKind.MEMORY_MUTATED: "memory_mutated",
    TraceEventKind.SIGNAL_PROPAGATED: "signal_propagated",
    TraceEventKind.EXECUTION_ALLOCATED: "execution_allocated",
    TraceEventKind.EXECUTION_STARTED: "execution_started",
    TraceEventKind.EXECUTION_PROGRESS: "execution_progress",
    TraceEventKind.EXECUTION_STDOUT: "execution_stdout",
    TraceEventKind.EXECUTION_STDERR: "execution_stderr",
    TraceEventKind.EXECUTION_COMPLETED: "execution_completed",
    TraceEventKind.EXECUTION_FAILED: "execution_failed",
    TraceEventKind.EXECUTION_CANCELLED: "execution_cancelled",
    TraceEventKind.EXECUTION_TIMEOUT: "execution_timeout",
    TraceEventKind.EXECUTION_RETRY: "execution_retry",
    TraceEventKind.EXECUTION_ROLLBACK: "execution_rollback",
    TraceEventKind.EXECUTION_SUBMITTED_ASYNC: "execution_submitted_async",
    TraceEventKind.EXECUTION_CALLBACK_RECEIVED: "execution_callback_received",
    TraceEventKind.DEPENDENCY_RELEASED: "dependency_released",
    TraceEventKind.MISSION_RESUMED: "mission_resumed",
    TraceEventKind.GRAPH_RECONCILED: "graph_reconciled",
    TraceEventKind.RUNTIME_LOCK_WAIT: "runtime_lock_wait",
    TraceEventKind.RUNTIME_LOCK_ACQUIRED: "runtime_lock_acquired",
    TraceEventKind.ASYNC_WAVE_DISPATCHED: "async_wave_dispatched",
    TraceEventKind.QUEUE_ENQUEUED: "queue_enqueued",
    TraceEventKind.QUEUE_RESTORED: "queue_restored",
    TraceEventKind.LEASE_RECOVERED: "lease_recovered",
    TraceEventKind.EXECUTION_RECOVERED: "execution_recovered",
    TraceEventKind.ORPHAN_DETECTED: "orphan_detected",
    TraceEventKind.TASK_REQUEUED: "task_requeued",
    TraceEventKind.DEADLETTERED: "deadlettered",
    TraceEventKind.REPLAY_SUPPRESSED: "replay_suppressed",
    TraceEventKind.ROUTING_DECISION: "routing_decision",
    TraceEventKind.WORKER_DISCONNECTED: "worker_disconnected",
    TraceEventKind.LEASE_FENCED: "lease_fenced",
    TraceEventKind.DISTRIBUTED_REQUEUE: "distributed_requeue",
    TraceEventKind.TOPOLOGY_RECOVERED: "topology_recovered",
    TraceEventKind.PLANNER_REASONING: "planner_reasoning",
    TraceEventKind.CONTRACT_GENERATED: "contract_generated",
    TraceEventKind.CAPABILITY_INFERRED: "capability_inferred",
    TraceEventKind.CONFIDENCE_UPDATED: "confidence_updated",
    TraceEventKind.REPLAN_GENERATED: "replan_generated",
    TraceEventKind.VALIDATION_FAILED: "validation_failed",
    TraceEventKind.STRATEGY_SELECTED: "strategy_selected",
    TraceEventKind.MEMORY_REINFORCED: "memory_reinforced",
    TraceEventKind.STRATEGY_LEARNED: "strategy_learned",
    TraceEventKind.CONFIDENCE_RECALIBRATED: "confidence_recalibrated",
    TraceEventKind.FAILURE_PATTERN_DETECTED: "failure_pattern_detected",
    TraceEventKind.OPTIMIZATION_CYCLE_COMPLETED: "optimization_cycle_completed",
    TraceEventKind.PLANNER_IMPROVED: "planner_improved",
    TraceEventKind.EXECUTION_PROFILE_UPDATED: "execution_profile_updated",
}


class CausalTracer:
    def __init__(
        self,
        store: CausalEventStore | None = None,
        *,
        on_record: Any | None = None,
    ) -> None:
        self.store = store or CausalEventStore()
        self._on_record = on_record
        self._mission_traces: dict[str, str] = {}
        self._task_traces: dict[str, str] = {}

    def start_mission_trace(self, mission_id: str, *, objective: str = "") -> CausalTraceContext:
        ctx = CausalTraceContext(mission_id=mission_id)
        bind_context(ctx)
        self._mission_traces[mission_id] = ctx.trace_id
        self.record(
            TraceEventKind.MISSION_CREATED,
            message="mission created",
            payload={"objective_preview": objective[:200]},
            component="mission_manager",
        )
        return ctx

    def mission_context(self, mission_id: str) -> CausalTraceContext:
        trace_id = self._mission_traces.get(mission_id)
        if trace_id:
            events = self.store.get_trace_events(trace_id)
            if events:
                e = events[0]
                ctx = CausalTraceContext(
                    trace_id=e.trace_id,
                    span_id=str(uuid4()),
                    parent_span_id=e.span_id,
                    causal_chain_id=e.causal_chain_id,
                    mission_id=mission_id,
                )
                bind_context(ctx)
                return ctx
        return self.start_mission_trace(mission_id)

    def link_task(self, mission_id: str, task_id: str) -> CausalTraceContext:
        base = current_context()
        if base and base.mission_id == mission_id:
            ctx = base.child_span(task_id=task_id)
        else:
            ctx = self.mission_context(mission_id).child_span(task_id=task_id)
        bind_context(ctx)
        self._task_traces[task_id] = ctx.trace_id
        return ctx

    def record(
        self,
        kind: TraceEventKind,
        *,
        message: str = "",
        payload: dict[str, Any] | None = None,
        component: str = "runtime",
        duration_ms: float | None = None,
        ctx: CausalTraceContext | None = None,
    ) -> TraceEvent:
        ctx = ctx or current_context() or CausalTraceContext()
        event = TraceEvent.from_context(
            kind,
            ctx,
            component=component,
            message=message,
            payload=payload or {},
            duration_ms=duration_ms,
        )
        self.store.append(event)
        if self._on_record:
            try:
                self._on_record(event)
            except Exception as exc:
                logger.warning("trace_record_callback_failed", error=str(exc))
        log_name = _EVENT_LOG_MAP.get(kind, kind.value)
        logger.info(
            log_name,
            trace_id=event.trace_id,
            span_id=event.span_id,
            causal_chain_id=event.causal_chain_id,
            mission_id=event.mission_id,
            task_id=event.task_id,
            component=component,
            message=message,
            **{k: v for k, v in (payload or {}).items() if k in ("reason", "tool", "state", "action")},
        )
        return event

    @contextmanager
    def span(
        self,
        name: str,
        *,
        kind: TraceEventKind = TraceEventKind.AGENT_ACTION,
        component: str = "runtime",
        **ctx_kwargs: Any,
    ) -> Iterator[CausalTraceContext]:
        parent = current_context()
        if parent:
            ctx = parent.child_span(**{k: v for k, v in ctx_kwargs.items() if v is not None})
        else:
            ctx = CausalTraceContext(**{k: v for k, v in ctx_kwargs.items() if v is not None})
        token = bind_context(ctx)
        t0 = time.monotonic()
        try:
            yield ctx
        finally:
            ms = (time.monotonic() - t0) * 1000
            self.record(kind, message=name, component=component, duration_ms=ms, ctx=ctx)
            reset_context(token)

    @asynccontextmanager
    async def async_span(
        self,
        name: str,
        *,
        kind: TraceEventKind = TraceEventKind.AGENT_ACTION,
        component: str = "runtime",
        **ctx_kwargs: Any,
    ) -> AsyncIterator[CausalTraceContext]:
        with self.span(name, kind=kind, component=component, **ctx_kwargs) as ctx:
            yield ctx

    def get_trace(self, trace_id: str) -> dict[str, Any]:
        events = self.store.get_trace_events(trace_id)
        if not events:
            return {}
        return {
            "trace_id": trace_id,
            "causal_chain_id": events[0].causal_chain_id,
            "event_count": len(events),
            "started_at": events[0].timestamp.isoformat(),
            "ended_at": events[-1].timestamp.isoformat(),
            "events": [e.model_dump(mode="json") for e in events],
        }
