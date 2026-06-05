"""Wire-format serializers for real-time stream events."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.core.observability.events import TraceEvent, TraceEventKind


class StreamEventKind(StrEnum):
    """Public stream event types (superset of trace + runtime)."""

    MISSION_CREATED = "mission_created"
    MISSION_STATE_CHANGED = "mission_state_changed"
    MISSION_DISPATCHED = "mission_dispatched"
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    RETRY_TRIGGERED = "retry_triggered"
    ESCALATION_TRIGGERED = "escalation_triggered"
    SIGNAL_PROPAGATED = "signal_propagated"
    SIGNAL_SUPPRESSED = "signal_suppressed"
    MEMORY_MUTATED = "memory_mutated"
    POLICY_BLOCKED = "policy_blocked"
    HEALTH_CHANGED = "health_changed"
    BOTTLENECK_DETECTED = "bottleneck_detected"
    DUPLICATE_SUPPRESSED = "duplicate_suppressed"
    HEARTBEAT = "heartbeat"
    CONNECTED = "connected"
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
    AUTONOMY_CYCLE_STARTED = "autonomy_cycle_started"
    AUTONOMY_OBJECTIVE_GENERATED = "autonomy_objective_generated"
    AUTONOMY_PAUSED = "autonomy_paused"
    OBJECTIVE_COMPLETED = "objective_completed"
    OBJECTIVE_DEFERRED = "objective_deferred"
    RESEARCH_ITERATION = "research_iteration"
    IDENTITY_UPDATED = "identity_updated"
    SAFETY_INTERVENTION = "safety_intervention"
    LOOP_DETECTED = "loop_detected"
    ENVIRONMENT_ALERT = "environment_alert"


class StreamEnvelope(BaseModel):
    """Typed envelope sent over WebSocket."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: StreamEventKind
    channel: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trace_id: str | None = None
    span_id: str | None = None
    parent_span_id: str | None = None
    causal_chain_id: str | None = None
    mission_id: str | None = None
    task_id: str | None = None
    workflow_id: str | None = None
    agent_id: str | None = None
    execution_id: str | None = None
    component: str = "runtime"
    message: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float | None = None

    def model_dump_json_line(self) -> str:
        return self.model_dump(mode="json")


def trace_kind_to_stream(kind: TraceEventKind) -> StreamEventKind:
    try:
        return StreamEventKind(kind.value)
    except ValueError:
        return StreamEventKind.SIGNAL_PROPAGATED


def envelope_from_trace(event: TraceEvent, *, channel: str | None = None) -> StreamEnvelope:
    ch = channel or resolve_channels_for_trace(event)[0]
    return StreamEnvelope(
        event_type=trace_kind_to_stream(event.kind),
        channel=ch,
        timestamp=event.timestamp.isoformat(),
        trace_id=event.trace_id,
        span_id=event.span_id,
        parent_span_id=event.parent_span_id,
        causal_chain_id=event.causal_chain_id,
        mission_id=event.mission_id,
        task_id=event.task_id,
        workflow_id=event.workflow_id,
        agent_id=event.agent_id,
        component=event.component,
        message=event.message,
        payload=event.payload,
        latency_ms=event.duration_ms,
    )


def resolve_channels_for_trace(event: TraceEvent) -> list[str]:
    channels = ["runtime"]
    if event.mission_id:
        channels.append(f"mission:{event.mission_id}")
    if event.task_id:
        channels.append(f"task:{event.task_id}")
    if event.trace_id:
        channels.append(f"trace:{event.trace_id}")
    if event.kind in (TraceEventKind.MEMORY_MUTATED,):
        channels.append("memory")
    if event.kind in (
        TraceEventKind.ROUTING_DECISION,
        TraceEventKind.WORKER_DISCONNECTED,
        TraceEventKind.TOPOLOGY_RECOVERED,
    ):
        channels.append("topology:runtime")
    if event.kind == TraceEventKind.ROUTING_DECISION:
        channels.append("routing:runtime")
    if event.kind == TraceEventKind.WORKER_DISCONNECTED:
        channels.append("workers:runtime")
    if event.kind in (
        TraceEventKind.PLANNER_REASONING,
        TraceEventKind.STRATEGY_SELECTED,
        TraceEventKind.REPLAN_GENERATED,
        TraceEventKind.CONFIDENCE_UPDATED,
    ):
        channels.append("planner:runtime")
    if event.mission_id and event.kind in (
        TraceEventKind.PLANNER_REASONING,
        TraceEventKind.CONTRACT_GENERATED,
        TraceEventKind.CAPABILITY_INFERRED,
        TraceEventKind.REPLAN_GENERATED,
        TraceEventKind.VALIDATION_FAILED,
    ):
        channels.append(f"reasoning:mission:{event.mission_id}")
    if event.kind in (TraceEventKind.CAPABILITY_INFERRED, TraceEventKind.CONTRACT_GENERATED):
        channels.append("tools:runtime")
    if event.kind in (
        TraceEventKind.MEMORY_REINFORCED,
        TraceEventKind.STRATEGY_LEARNED,
    ):
        channels.append("cognition:runtime")
    if event.kind in (
        TraceEventKind.PLANNER_IMPROVED,
        TraceEventKind.CONFIDENCE_RECALIBRATED,
        TraceEventKind.STRATEGY_LEARNED,
    ):
        channels.append("learning:runtime")
    if event.kind == TraceEventKind.OPTIMIZATION_CYCLE_COMPLETED:
        channels.append("optimization:runtime")
    if event.kind == TraceEventKind.FAILURE_PATTERN_DETECTED:
        channels.append("failures:runtime")
    if event.kind in (
        TraceEventKind.MODEL_LOADED,
        TraceEventKind.INFERENCE_STARTED,
        TraceEventKind.INFERENCE_COMPLETED,
    ):
        channels.append("models:runtime")
    if event.kind in (
        TraceEventKind.MEMORY_GROUNDED,
        TraceEventKind.REASONING_CHAIN_EXTENDED,
        TraceEventKind.CONTEXT_TRUNCATED,
    ):
        channels.append("reasoning:runtime")
        if event.mission_id:
            channels.append(f"reasoning:mission:{event.mission_id}")
    if event.kind in (
        TraceEventKind.REFLECTION_GENERATED,
        TraceEventKind.CONTRADICTION_DETECTED,
        TraceEventKind.HALLUCINATION_RISK,
    ):
        channels.append("reflection:runtime")
    if event.kind == TraceEventKind.REASONING_CHAIN_EXTENDED:
        channels.append("agents:runtime")
    if event.kind in (
        TraceEventKind.AUTONOMY_CYCLE_STARTED,
        TraceEventKind.AUTONOMY_OBJECTIVE_GENERATED,
        TraceEventKind.AUTONOMY_PAUSED,
    ):
        channels.append("autonomy:runtime")
    if event.kind in (TraceEventKind.OBJECTIVE_COMPLETED, TraceEventKind.OBJECTIVE_DEFERRED):
        channels.append("objectives:runtime")
    if event.kind == TraceEventKind.RESEARCH_ITERATION:
        channels.append("research:runtime")
    if event.kind == TraceEventKind.IDENTITY_UPDATED:
        channels.append("identity:runtime")
    if event.kind in (TraceEventKind.SAFETY_INTERVENTION, TraceEventKind.LOOP_DETECTED):
        channels.append("safety:runtime")
    if event.kind == TraceEventKind.ENVIRONMENT_ALERT:
        channels.append("autonomy:runtime")
    if event.kind in (TraceEventKind.PERCEPTION_UPDATED, TraceEventKind.SCREEN_PARSED):
        channels.append("perception:runtime")
    if event.kind == TraceEventKind.WORKSPACE_DETECTED:
        channels.append("desktop:runtime")
        channels.append("workspace:runtime")
    if event.kind == TraceEventKind.VOICE_SESSION_STARTED:
        channels.append("voice:runtime")
    if event.kind in (
        TraceEventKind.COPILOT_SUGGESTION_GENERATED,
        TraceEventKind.PROACTIVE_ASSISTANCE_TRIGGERED,
    ):
        channels.append("copilot:runtime")
    if event.kind == TraceEventKind.WORKSPACE_PATTERN_LEARNED:
        channels.append("workspace:runtime")
    if event.kind in (
        TraceEventKind.APPROVAL_REQUESTED,
        TraceEventKind.COLLABORATION_FEEDBACK_RECEIVED,
    ):
        channels.append("collaboration:runtime")
    if event.kind in (
        TraceEventKind.ACTION_PROPOSED,
        TraceEventKind.ACTION_APPROVED,
        TraceEventKind.ACTION_EXECUTED,
        TraceEventKind.ACTION_REVERTED,
        TraceEventKind.DESTRUCTIVE_ACTION_BLOCKED,
    ):
        channels.append("actions:runtime")
    if event.kind == TraceEventKind.AUTOMATION_INTERRUPTED:
        channels.append("automation:runtime")
        channels.append("supervision:runtime")
    if event.kind == TraceEventKind.BROWSER_NAVIGATION:
        channels.append("browser:runtime")
    if event.kind in (TraceEventKind.WORKFLOW_RECORDED, TraceEventKind.MACRO_GENERATED):
        channels.append("workflows:runtime")
    if event.kind == TraceEventKind.OVERLAY_RENDERED:
        channels.append("automation:runtime")
    if event.kind in (TraceEventKind.ACTION_APPROVED, TraceEventKind.AUTOMATION_INTERRUPTED):
        channels.append("supervision:runtime")
    if event.kind in (TraceEventKind.KNOWLEDGE_CREATED, TraceEventKind.STALE_KNOWLEDGE_DETECTED):
        channels.append("knowledge:runtime")
    if event.kind in (TraceEventKind.RESEARCH_STARTED, TraceEventKind.RESEARCH_COMPLETED, TraceEventKind.SOURCE_VERIFIED):
        channels.append("research:runtime")
    if event.kind in (TraceEventKind.BELIEF_UPDATED, TraceEventKind.CONTRADICTION_DETECTED):
        channels.append("beliefs:runtime")
    if event.kind in (TraceEventKind.WORLD_MODEL_UPDATED, TraceEventKind.HYPOTHESIS_GENERATED):
        channels.append("worldmodel:runtime")
    if event.kind == TraceEventKind.TREND_DETECTED:
        channels.append("trends:runtime")
    return channels


def resolve_channels_for_envelope(envelope: StreamEnvelope) -> list[str]:
    channels = ["runtime"]
    if envelope.mission_id:
        channels.append(f"mission:{envelope.mission_id}")
    if envelope.task_id:
        channels.append(f"task:{envelope.task_id}")
    if envelope.trace_id:
        channels.append(f"trace:{envelope.trace_id}")
    if envelope.event_type == StreamEventKind.MEMORY_MUTATED:
        channels.append("memory")
    if envelope.execution_id:
        channels.append(f"execution:{envelope.execution_id}")
    if envelope.channel and envelope.channel not in channels:
        channels.append(envelope.channel)
    return list(dict.fromkeys(channels))
