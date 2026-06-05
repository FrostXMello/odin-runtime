"""Typed causal trace event schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.core.observability.context import CausalTraceContext


class TraceEventKind(StrEnum):
    MISSION_CREATED = "mission_created"
    MISSION_DISPATCHED = "mission_dispatched"
    MISSION_STATE_CHANGED = "mission_state_changed"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    RETRY_TRIGGERED = "retry_triggered"
    ESCALATION_TRIGGERED = "escalation_triggered"
    POLICY_BLOCKED = "policy_blocked"
    MEMORY_MUTATED = "memory_mutated"
    SIGNAL_PROPAGATED = "signal_propagated"
    SIGNAL_SUPPRESSED = "signal_suppressed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    AGENT_ACTION = "agent_action"
    DUPLICATE_SUPPRESSED = "duplicate_suppressed"
    EXECUTION_ALLOCATED = "execution_allocated"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_PROGRESS = "execution_progress"
    EXECUTION_STDOUT = "execution_stdout"
    EXECUTION_STDERR = "execution_stderr"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_CANCELLED = "execution_cancelled"
    EXECUTION_TIMEOUT = "execution_timeout"
    EXECUTION_RETRY = "execution_retry"
    EXECUTION_ROLLBACK = "execution_rollback"
    EXECUTION_SUBMITTED_ASYNC = "execution_submitted_async"
    EXECUTION_CALLBACK_RECEIVED = "execution_callback_received"
    DEPENDENCY_RELEASED = "dependency_released"
    MISSION_RESUMED = "mission_resumed"
    GRAPH_RECONCILED = "graph_reconciled"
    RUNTIME_LOCK_WAIT = "runtime_lock_wait"
    RUNTIME_LOCK_ACQUIRED = "runtime_lock_acquired"
    ASYNC_WAVE_DISPATCHED = "async_wave_dispatched"
    QUEUE_ENQUEUED = "queue_enqueued"
    QUEUE_RESTORED = "queue_restored"
    LEASE_RECOVERED = "lease_recovered"
    EXECUTION_RECOVERED = "execution_recovered"
    ORPHAN_DETECTED = "orphan_detected"
    TASK_REQUEUED = "task_requeued"
    DEADLETTERED = "deadlettered"
    REPLAY_SUPPRESSED = "replay_suppressed"
    ROUTING_DECISION = "routing_decision"
    WORKER_DISCONNECTED = "worker_disconnected"
    LEASE_FENCED = "lease_fenced"
    DISTRIBUTED_REQUEUE = "distributed_requeue"
    TOPOLOGY_RECOVERED = "topology_recovered"
    PLANNER_REASONING = "planner_reasoning"
    CONTRACT_GENERATED = "contract_generated"
    CAPABILITY_INFERRED = "capability_inferred"
    CONFIDENCE_UPDATED = "confidence_updated"
    REPLAN_GENERATED = "replan_generated"
    VALIDATION_FAILED = "validation_failed"
    STRATEGY_SELECTED = "strategy_selected"
    MEMORY_REINFORCED = "memory_reinforced"
    STRATEGY_LEARNED = "strategy_learned"
    CONFIDENCE_RECALIBRATED = "confidence_recalibrated"
    FAILURE_PATTERN_DETECTED = "failure_pattern_detected"
    OPTIMIZATION_CYCLE_COMPLETED = "optimization_cycle_completed"
    PLANNER_IMPROVED = "planner_improved"
    EXECUTION_PROFILE_UPDATED = "execution_profile_updated"
    MODEL_LOADED = "model_loaded"
    INFERENCE_STARTED = "inference_started"
    INFERENCE_COMPLETED = "inference_completed"
    MEMORY_GROUNDED = "memory_grounded"
    REFLECTION_GENERATED = "reflection_generated"
    CONTRADICTION_DETECTED = "contradiction_detected"
    HALLUCINATION_RISK = "hallucination_risk"
    REASONING_CHAIN_EXTENDED = "reasoning_chain_extended"
    CONTEXT_TRUNCATED = "context_truncated"


class TraceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    kind: TraceEventKind
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    causal_chain_id: str
    mission_id: str | None = None
    task_id: str | None = None
    workflow_id: str | None = None
    agent_id: str | None = None
    signal_id: str | None = None
    component: str = "runtime"
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    duration_ms: float | None = None

    @classmethod
    def from_context(
        cls,
        kind: TraceEventKind,
        ctx: CausalTraceContext,
        *,
        component: str = "runtime",
        message: str = "",
        payload: dict[str, Any] | None = None,
        duration_ms: float | None = None,
    ) -> TraceEvent:
        return cls(
            kind=kind,
            trace_id=ctx.trace_id,
            span_id=ctx.span_id,
            parent_span_id=ctx.parent_span_id,
            causal_chain_id=ctx.causal_chain_id,
            mission_id=ctx.mission_id,
            task_id=ctx.task_id,
            workflow_id=ctx.workflow_id,
            agent_id=ctx.agent_id,
            signal_id=ctx.signal_id,
            component=component,
            message=message,
            payload=payload or {},
            duration_ms=duration_ms,
        )
