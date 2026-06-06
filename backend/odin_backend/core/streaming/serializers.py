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
    if event.kind in (TraceEventKind.AGENT_SPAWNED, TraceEventKind.EXPERTISE_UPDATED, TraceEventKind.AGENT_REFLECTION_GENERATED):
        channels.append("agents:runtime")
        channels.append("society:runtime")
    if event.kind in (TraceEventKind.DELEGATION_CREATED, TraceEventKind.COLLABORATION_FORMED, TraceEventKind.CONSENSUS_REACHED):
        channels.append("collaboration:runtime")
        channels.append("society:runtime")
    if event.kind in (TraceEventKind.DEBATE_STARTED, TraceEventKind.REASONING_SHARED):
        channels.append("dialogues:runtime")
    if event.kind in (TraceEventKind.OBJECTIVE_ASSIGNED, TraceEventKind.CONTINUITY_RESTORED):
        channels.append("objectives:runtime")
        channels.append("society:runtime")
    if event.kind == TraceEventKind.DEBATE_STARTED:
        channels.append("society:runtime")
    if event.kind in (
        TraceEventKind.FEDERATION_NODE_CONNECTED,
        TraceEventKind.FEDERATION_NODE_DISCONNECTED,
        TraceEventKind.REMOTE_REASONING_REQUESTED,
        TraceEventKind.REMOTE_REASONING_COMPLETED,
    ):
        channels.append("federation:runtime")
    if event.kind in (
        TraceEventKind.WORLD_STATE_CHANGED,
        TraceEventKind.SIMULATION_PROJECTED,
        TraceEventKind.PREDICTION_UPDATED,
    ):
        channels.append("world:runtime")
        channels.append("simulation:runtime")
    if event.kind == TraceEventKind.STRATEGY_GENERATED:
        channels.append("strategy:runtime")
    if event.kind in (
        TraceEventKind.TRUST_SCORE_CHANGED,
        TraceEventKind.GOVERNANCE_VIOLATION,
        TraceEventKind.NODE_QUARANTINED,
    ):
        channels.append("governance:runtime")
        channels.append("federation:runtime")
    if event.kind == TraceEventKind.KNOWLEDGE_SHARED:
        channels.append("federation:runtime")
    if event.kind == TraceEventKind.CONTINUITY_RESTORED:
        channels.append("continuity:runtime")
    if event.kind == TraceEventKind.MEMORY_CONSOLIDATED:
        channels.append("continuity:runtime")
    if event.kind in (TraceEventKind.POLICY_OPTIMIZED, TraceEventKind.ROUTING_OPTIMIZED, TraceEventKind.EVOLUTION_CYCLE_COMPLETED):
        channels.append("evolution:runtime")
    if event.kind == TraceEventKind.COGNITION_BUDGET_UPDATED:
        channels.append("economy:runtime")
    if event.kind in (TraceEventKind.META_ANALYSIS_GENERATED, TraceEventKind.HALLUCINATION_DETECTED):
        channels.append("meta:runtime")
    if event.kind == TraceEventKind.OPERATOR_PATTERN_LEARNED:
        channels.append("continuity:runtime")
    if event.kind == TraceEventKind.WORKLOAD_REBALANCED:
        channels.append("optimization:runtime")
    if event.kind == TraceEventKind.MEMORY_INDEXED:
        channels.append("memory:runtime")
    if event.kind == TraceEventKind.TASK_DELEGATED:
        channels.append("agents:runtime")
    if event.kind == TraceEventKind.VOICE_TURN_COMPLETED:
        channels.append("voice:runtime")
    if event.kind in (TraceEventKind.BENCHMARK_COMPLETED, TraceEventKind.REGRESSION_DETECTED):
        channels.append("evaluation:runtime")
    if event.kind == TraceEventKind.RESOURCE_OPTIMIZED:
        channels.append("resources:runtime")
    if event.kind == TraceEventKind.DAEMON_STARTED:
        channels.append("daemon:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_RECOVERED,
        TraceEventKind.DEGRADED_MODE_ENABLED,
        TraceEventKind.WATCHDOG_TRIGGERED,
        TraceEventKind.RUNTIME_REPAIRED,
    ):
        channels.append("stability:runtime")
    if event.kind == TraceEventKind.DAEMON_RESTORED:
        channels.append("daemon:runtime")
        channels.append("recovery:runtime")
    if event.kind in (TraceEventKind.AUTOMATION_VERIFIED, TraceEventKind.ACTION_RETRY_GENERATED):
        channels.append("automation:runtime")
    if event.kind == TraceEventKind.EXECUTION_SALVAGED:
        channels.append("healing:runtime")
    if event.kind == TraceEventKind.MEMORY_COMPACTED:
        channels.append("memory:runtime")
    if event.kind == TraceEventKind.WORKSPACE_RESTORED:
        channels.append("recovery:runtime")
    if event.kind in (TraceEventKind.PROJECT_CONTEXT_RESTORED, TraceEventKind.CODING_SESSION_RESUMED):
        channels.append("projects:runtime")
    if event.kind == TraceEventKind.REPOSITORY_INDEXED:
        channels.append("repositories:runtime")
    if event.kind == TraceEventKind.WORKSPACE_LINKED:
        channels.append("workspace:runtime")
    if event.kind == TraceEventKind.SEMANTIC_SEARCH_COMPLETED:
        channels.append("search:runtime")
    if event.kind in (TraceEventKind.PRODUCTIVITY_PATTERN_DETECTED, TraceEventKind.FOCUS_SESSION_STARTED):
        channels.append("productivity:runtime")
    if event.kind == TraceEventKind.BRIEFING_GENERATED:
        channels.append("workspace:runtime")
    if event.kind == TraceEventKind.KNOWLEDGE_CLUSTER_CREATED:
        channels.append("workspace:runtime")
    if event.kind == TraceEventKind.RETRIEVAL_OPTIMIZED:
        channels.append("storage:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_PROFILE_CHANGED,
        TraceEventKind.DEPLOYMENT_VALIDATED,
        TraceEventKind.SNAPSHOT_RESTORED,
    ):
        channels.append("deployment:runtime")
    if event.kind in (
        TraceEventKind.STARTUP_OPTIMIZED,
        TraceEventKind.MEMORY_PRESSURE_DETECTED,
        TraceEventKind.MODEL_SWAPPED,
    ):
        channels.append("performance:runtime")
    if event.kind in (
        TraceEventKind.DAEMON_RESTARTED,
        TraceEventKind.RECOVERY_COMPLETED,
    ):
        channels.append("diagnostics:runtime")
    if event.kind == TraceEventKind.PRIVACY_FILTER_TRIGGERED:
        channels.append("privacy:runtime")
    if event.kind == TraceEventKind.COMMAND_EXECUTED:
        channels.append("activity:runtime")
    if event.kind in (
        TraceEventKind.REASONING_QUALITY_SCORED,
        TraceEventKind.HALLUCINATION_RISK_DETECTED,
    ):
        channels.append("intelligence:runtime")
    if event.kind == TraceEventKind.REASONING_QUALITY_SCORED:
        channels.append("reasoning:runtime")
    if event.kind in (TraceEventKind.RETRIEVAL_RANKED, TraceEventKind.MEMORY_STITCHED):
        channels.append("retrieval:runtime")
    if event.kind == TraceEventKind.CODE_PATCH_GENERATED:
        channels.append("copilot:runtime")
        channels.append("debugging:runtime")
    if event.kind in (
        TraceEventKind.DELEGATION_OPTIMIZED,
        TraceEventKind.RETRY_STRATEGY_SELECTED,
    ):
        channels.append("intelligence:runtime")
    if event.kind == TraceEventKind.OPERATOR_INTENT_INFERRED:
        channels.append("intelligence:runtime")
        channels.append("activity:runtime")
    if event.kind == TraceEventKind.MODEL_ROUTE_SELECTED:
        channels.append("reasoning:runtime")
    if event.kind == TraceEventKind.SYNTHESIS_VALIDATED:
        channels.append("intelligence:runtime")
    if event.kind in (
        TraceEventKind.BUG_LOCALIZED,
        TraceEventKind.DEBUGGING_STRATEGY_SELECTED,
    ):
        channels.append("debugging:runtime")
    if event.kind in (
        TraceEventKind.PATCH_GENERATED,
        TraceEventKind.PATCH_VALIDATED,
        TraceEventKind.ROLLBACK_PREPARED,
    ):
        channels.append("patches:runtime")
    if event.kind in (
        TraceEventKind.REGRESSION_DETECTED,
    ):
        channels.append("testing:runtime")
        channels.append("debugging:runtime")
    if event.kind in (
        TraceEventKind.REPOSITORY_GRAPH_UPDATED,
        TraceEventKind.ARCHITECTURE_DRIFT_DETECTED,
    ):
        channels.append("repositories:runtime")
        channels.append("engineering:runtime")
    if event.kind in (
        TraceEventKind.ENGINEERING_GOAL_CREATED,
        TraceEventKind.IMPLEMENTATION_BLOCKED,
    ):
        channels.append("engineering:runtime")
    if event.kind in (
        TraceEventKind.ACTIVE_CONTEXT_UPDATED,
        TraceEventKind.LIVE_CONTEXT_FUSED,
    ):
        channels.append("context:runtime")
        channels.append("workstation:runtime")
    if event.kind == TraceEventKind.WORKFLOW_PREDICTED:
        channels.append("workflow:runtime")
    if event.kind == TraceEventKind.COGNITION_TICK_COMPLETED:
        channels.append("cognition:runtime")
    if event.kind == TraceEventKind.EXECUTION_SUPERVISED:
        channels.append("workstation:runtime")
    if event.kind == TraceEventKind.INTERRUPTION_DETECTED:
        channels.append("context:runtime")
    if event.kind in (
        TraceEventKind.CONTINUITY_RESTORED_LIVE,
        TraceEventKind.UNFINISHED_WORK_DETECTED,
    ):
        channels.append("continuity:runtime")
    if event.kind == TraceEventKind.REALTIME_ASSISTANCE_GENERATED:
        channels.append("live-copilot:runtime")
    if event.kind == TraceEventKind.WORKSPACE_ATTENTION_SHIFTED:
        channels.append("workstation:runtime")
    if event.kind in (
        TraceEventKind.THOUGHT_GENERATED,
        TraceEventKind.REASONING_STREAM_UPDATED,
    ):
        channels.append("cognition-live:runtime")
        channels.append("thought-stream:runtime")
    if event.kind in (
        TraceEventKind.PRESENCE_SHIFTED,
        TraceEventKind.EMOTIONAL_STATE_UPDATED,
    ):
        channels.append("presence:runtime")
    if event.kind == TraceEventKind.ATTENTION_FOCUS_CHANGED:
        channels.append("overlay:runtime")
    if event.kind == TraceEventKind.CONVERSATION_THREAD_RESTORED:
        channels.append("conversation:runtime")
    if event.kind == TraceEventKind.LIVE_OVERLAY_RENDERED:
        channels.append("overlay:runtime")
    if event.kind in (
        TraceEventKind.IMPROVEMENT_PROPOSED,
        TraceEventKind.ARCHITECTURE_REFLECTION_GENERATED,
    ):
        channels.append("self-development:runtime")
    if event.kind == TraceEventKind.WORKSPACE_ATTENTION_CHANGED:
        channels.append("workstation:runtime")
        channels.append("presence:runtime")
    if event.kind in (
        TraceEventKind.IMPROVEMENT_CYCLE_STARTED,
        TraceEventKind.BOTTLENECK_DETECTED,
        TraceEventKind.UPGRADE_PROPOSED,
        TraceEventKind.EVOLUTION_LEARNING_UPDATED,
    ):
        channels.append("evolution:runtime")
    if event.kind in (
        TraceEventKind.BENCHMARK_COMPLETED,
        TraceEventKind.REGRESSION_DETECTED,
    ):
        channels.append("benchmarks:runtime")
    if event.kind == TraceEventKind.REGRESSION_DETECTED:
        channels.append("regressions:runtime")
    if event.kind in (
        TraceEventKind.PATCH_GENERATED,
        TraceEventKind.PATCH_VALIDATED,
        TraceEventKind.ROLLBACK_TRIGGERED,
    ):
        channels.append("patches:runtime")
    if event.kind == TraceEventKind.UPGRADE_PROPOSED:
        channels.append("upgrades:runtime")
    if event.kind == TraceEventKind.OPTIMIZATION_APPLIED:
        channels.append("evolution:runtime")
        channels.append("upgrades:runtime")
    if event.kind in (
        TraceEventKind.COGNITIVE_SURFACE_RENDERED,
        TraceEventKind.WORKSPACE_FOCUS_CHANGED,
    ):
        channels.append("shell:runtime")
    if event.kind == TraceEventKind.IMMERSIVE_MODE_CHANGED:
        channels.append("immersive:runtime")
    if event.kind in (
        TraceEventKind.REASONING_STREAM_UPDATED,
        TraceEventKind.LIVE_PATCH_SUGGESTED,
    ):
        channels.append("reasoning-streams:runtime")
    if event.kind == TraceEventKind.LIVE_ENGINEERING_DETECTED:
        channels.append("live-engineering:runtime")
    if event.kind in (
        TraceEventKind.DAEMON_ATTENTION_SHIFTED,
        TraceEventKind.PERSISTENT_PRESENCE_UPDATED,
        TraceEventKind.OPERATOR_INTERRUPT_RECEIVED,
    ):
        channels.append("daemon:runtime")
    if event.kind == TraceEventKind.CONVERSATIONAL_CONTEXT_RESTORED:
        channels.append("conversational-os:runtime")
    if event.kind in (
        TraceEventKind.COGNITION_CHECKPOINT_CREATED,
        TraceEventKind.SESSION_REHYDRATED,
    ):
        channels.append("cognition:continuity")
    if event.kind == TraceEventKind.WORKSPACE_CONTEXT_RESTORED:
        channels.append("workspace:presence")
    if event.kind == TraceEventKind.MEMORY_THREAD_ACTIVATED:
        channels.append("memory-threads:runtime")
    if event.kind == TraceEventKind.COGNITIVE_SURFACE_UPDATED:
        channels.append("cognitive-surface:runtime")
    if event.kind in (
        TraceEventKind.FOCUS_STATE_CHANGED,
        TraceEventKind.INTERRUPTION_CLASSIFIED,
        TraceEventKind.ADAPTIVE_PRESENCE_UPDATED,
    ):
        channels.append("live-environment:runtime")
    if event.kind == TraceEventKind.WORKFLOW_PREDICTION_GENERATED:
        channels.append("cognition:continuity")
    if event.kind == TraceEventKind.UNFINISHED_WORK_DETECTED:
        channels.append("cognition:continuity")
    if event.kind == TraceEventKind.DESKTOP_SESSION_RESTORED:
        channels.append("desktop:runtime")
    if event.kind in (
        TraceEventKind.CONVERSATION_WORKSPACE_OPENED,
        TraceEventKind.LIVE_REASONING_RENDERED,
    ):
        channels.append("workspace-ui:runtime")
        channels.append("thought-stream:runtime")
    if event.kind in (
        TraceEventKind.VISUALIZATION_SYNCED,
        TraceEventKind.LIVE_REASONING_RENDERED,
    ):
        channels.append("visualization:runtime")
        channels.append("cognition-live:runtime")
        channels.append("reasoning-streams:runtime")
    if event.kind in (
        TraceEventKind.WORKSPACE_REHYDRATED,
        TraceEventKind.OPERATOR_FOCUS_SHIFTED,
        TraceEventKind.EVOLUTION_REVIEW_OPENED,
    ):
        channels.append("operator-experience:runtime")
    if event.kind == TraceEventKind.OVERLAY_ATTACHED:
        channels.append("overlay:runtime")
        channels.append("desktop:runtime")
    if event.kind == TraceEventKind.VOICE_INTERRUPT_DETECTED:
        channels.append("voice:runtime")
        channels.append("desktop:runtime")
    if event.kind == TraceEventKind.MEMORY_SURFACE_RENDERED:
        channels.append("memory-threads:runtime")
        channels.append("visualization:runtime")
    if event.kind == TraceEventKind.EVOLUTION_REVIEW_OPENED:
        channels.append("evolution:runtime")
        channels.append("self-development:runtime")
    if event.kind == TraceEventKind.WORKSPACE_FOCUS_CHANGED:
        channels.append("workspace:runtime")
        channels.append("workspace-ui:runtime")
    if event.kind == TraceEventKind.COGNITIVE_TRANSITION_RENDERED:
        channels.append("workspace:runtime")
        channels.append("visualization:runtime")
    if event.kind in (
        TraceEventKind.REASONING_BRANCH_RENDERED,
        TraceEventKind.LIVE_REASONING_RENDERED,
    ):
        channels.append("reasoning-live:runtime")
        channels.append("reasoning-streams:runtime")
    if event.kind in (
        TraceEventKind.CONVERSATION_MEMORY_RECALLED,
        TraceEventKind.LIVE_PRESENCE_UPDATED,
    ):
        channels.append("presence-live:runtime")
        channels.append("conversational-os:runtime")
    if event.kind in (
        TraceEventKind.UPGRADE_REVIEW_OPENED,
        TraceEventKind.ROLLBACK_SIMULATED,
    ):
        channels.append("evolution-review:runtime")
        channels.append("evolution:runtime")
    if event.kind in (
        TraceEventKind.DAEMON_ATTENTION_SHIFTED,
        TraceEventKind.UNFINISHED_TASK_RESURFACED,
    ):
        channels.append("daemon-cognition:runtime")
        channels.append("daemon:runtime")
    if event.kind == TraceEventKind.OPERATOR_FOCUS_DEGRADED:
        channels.append("productivity:runtime")
        channels.append("live-environment:runtime")
    if event.kind in (
        TraceEventKind.ENGINEERING_GOAL_DETECTED,
        TraceEventKind.ENGINEERING_SESSION_RESTORED,
        TraceEventKind.IMPLEMENTATION_STAGE_ADVANCED,
    ):
        channels.append("engineering-live:runtime")
    if event.kind in (
        TraceEventKind.LIVE_ENGINEERING_DETECTED,
        TraceEventKind.LIVE_PATCH_SUGGESTED,
    ):
        channels.append("engineering-live:runtime")
    if event.kind in (
        TraceEventKind.DEBUG_CLUSTER_CREATED,
        TraceEventKind.REGRESSION_RISK_DETECTED,
        TraceEventKind.PATCH_HYPOTHESIS_GENERATED,
    ):
        channels.append("debugging-live:runtime")
    if event.kind == TraceEventKind.ENGINEERING_SESSION_RESTORED:
        channels.append("project-memory:runtime")
    if event.kind in (
        TraceEventKind.ARCHITECTURE_DEBATE_STARTED,
        TraceEventKind.REVIEW_CONSENSUS_REACHED,
    ):
        channels.append("engineering-society:runtime")
        channels.append("society:runtime")
    if event.kind == TraceEventKind.SANDBOX_VALIDATION_COMPLETED:
        channels.append("sandbox:runtime")
    if event.kind == TraceEventKind.OVERNIGHT_ANALYSIS_COMPLETED:
        channels.append("repo-watch:runtime")
        channels.append("daemon-cognition:runtime")
    if event.kind in (
        TraceEventKind.KERNEL_ATTENTION_SHIFTED,
        TraceEventKind.COGNITIVE_TICK_EXECUTED,
        TraceEventKind.CROSS_RUNTIME_SYNC_COMPLETED,
    ):
        channels.append("kernel:runtime")
        channels.append("cognitive-orchestration:runtime")
    if event.kind == TraceEventKind.MEMORY_FABRIC_LINKED:
        channels.append("memory-fabric:runtime")
        channels.append("memory-threads:runtime")
    if event.kind in (
        TraceEventKind.ENVIRONMENT_CONTEXT_DETECTED,
        TraceEventKind.WORKFLOW_PREDICTION_GENERATED,
    ):
        channels.append("environment:runtime")
        channels.append("live-environment:runtime")
    if event.kind in (
        TraceEventKind.THOUGHT_STREAM_COMPRESSED,
        TraceEventKind.REASONING_BRANCH_RENDERED,
    ):
        channels.append("cognitive-streams:runtime")
    if event.kind == TraceEventKind.PRESENCE_FAMILIARITY_UPDATED:
        channels.append("presence-personal:runtime")
        channels.append("presence-live:runtime")
    if event.kind == TraceEventKind.ASSISTANCE_INTERVENTION_GENERATED:
        channels.append("assistance:runtime")
    if event.kind == TraceEventKind.OVERNIGHT_REFLECTION_COMPLETED:
        channels.append("cognitive-orchestration:runtime")
        channels.append("daemon-cognition:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_PRIORITY_SHIFTED,
        TraceEventKind.ADAPTIVE_SCALING_APPLIED,
        TraceEventKind.BACKGROUND_OPTIMIZATION_COMPLETED,
    ):
        channels.append("adaptive-runtime:runtime")
    if event.kind == TraceEventKind.COGNITION_LOAD_BALANCED:
        channels.append("load-balancer:runtime")
        channels.append("adaptive-runtime:runtime")
    if event.kind in (
        TraceEventKind.WORKSPACE_PREDICTION_GENERATED,
        TraceEventKind.WORKFLOW_RESUMED,
    ):
        channels.append("workspace-autonomy:runtime")
    if event.kind in (
        TraceEventKind.ENGINEERING_UPGRADE_PROPOSED,
        TraceEventKind.TECHNICAL_DEBT_DETECTED,
    ):
        channels.append("engineering-evolution:runtime")
    if event.kind in (
        TraceEventKind.COGNITIVE_FATIGUE_DETECTED,
        TraceEventKind.ADAPTIVE_ASSISTANCE_ADJUSTED,
        TraceEventKind.ATTENTION_HEATMAP_UPDATED,
    ):
        channels.append("operator-intelligence:runtime")
    if event.kind in (
        TraceEventKind.DEFERRED_REASONING_RESTORED,
        TraceEventKind.OVERNIGHT_CYCLE_COMPLETED,
        TraceEventKind.LOW_POWER_TRANSITION,
        TraceEventKind.COGNITIVE_RESUME_COMPLETED,
        TraceEventKind.OVERNIGHT_OPTIMIZATION_COMPLETED,
    ):
        channels.append("daemon-v2:runtime")
        channels.append("daemon-cognition:runtime")
    if event.kind == TraceEventKind.NATIVE_WINDOW_CONTEXT_CHANGED:
        channels.append("native-os:runtime")
        channels.append("desktop-v2:runtime")
    if event.kind in (
        TraceEventKind.AUTONOMOUS_GOAL_RESUMED,
        TraceEventKind.LONG_HORIZON_PLAN_UPDATED,
        TraceEventKind.PERSISTENT_REASONING_RESTORED,
        TraceEventKind.AUTONOMOUS_TICK_EXECUTED,
    ):
        channels.append("autonomous-loop-v2:runtime")
    if event.kind in (
        TraceEventKind.ENGINEERING_REGRESSION_FORECASTED,
        TraceEventKind.MULTI_REPO_REASONING_COMPLETED,
    ):
        channels.append("engineering-evolution-v2:runtime")
    if event.kind in (
        TraceEventKind.SEMANTIC_MEMORY_LINKED,
        TraceEventKind.CONTEXT_REHYDRATED,
    ):
        channels.append("memory-fabric-v2:runtime")
    if event.kind in (
        TraceEventKind.DEEP_FOCUS_SESSION_STARTED,
        TraceEventKind.BURNOUT_RISK_DETECTED,
        TraceEventKind.ADAPTIVE_WORKFLOW_GENERATED,
    ):
        channels.append("productivity-v3:runtime")
    if event.kind in (
        TraceEventKind.COGNITIVE_HEARTBEAT_EXECUTED,
        TraceEventKind.CONTINUOUS_REASONING_UPDATED,
    ):
        channels.append("realtime-cognition:runtime")
        channels.append("desktop-v3:runtime")
    if event.kind == TraceEventKind.ATTENTION_FLOW_UPDATED:
        channels.append("realtime-cognition:runtime")
    if event.kind in (
        TraceEventKind.WORKSPACE_ATTENTION_SHIFTED,
        TraceEventKind.MULTI_PROJECT_CONTEXT_LINKED,
    ):
        channels.append("workspace-coordination:runtime")
    if event.kind in (
        TraceEventKind.ARCHITECTURE_FORECAST_GENERATED,
        TraceEventKind.RELIABILITY_RISK_DETECTED,
        TraceEventKind.ENGINEERING_VALIDATION_PLANNED,
    ):
        channels.append("engineering-infrastructure:runtime")
    if event.kind == TraceEventKind.PREDICTIVE_MEMORY_RESURFACED:
        channels.append("memory-intelligence:runtime")
    if event.kind in (
        TraceEventKind.OPERATOR_FOCUS_FORECASTED,
        TraceEventKind.COGNITIVE_LOAD_FORECASTED,
        TraceEventKind.WORKFLOW_OPTIMIZATION_GENERATED,
    ):
        channels.append("operator-intelligence-v4:runtime")
    if event.kind in (
        TraceEventKind.COGNITION_TICK_STARTED,
        TraceEventKind.COGNITION_TICK_COMPLETED,
        TraceEventKind.GLOBAL_CONTEXT_REBUILT,
    ):
        channels.append("unified-core:runtime")
        channels.append("desktop-v3:runtime")
    if event.kind in (
        TraceEventKind.ATTENTION_SHIFT_DETECTED,
        TraceEventKind.FOCUS_HEATMAP_UPDATED,
    ):
        channels.append("attention:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_LOAD_REBALANCED,
        TraceEventKind.DEFERRED_TASK_RESTORED,
    ):
        channels.append("scheduler:runtime")
    if event.kind in (
        TraceEventKind.PERSISTENT_AGENT_RESTORED,
        TraceEventKind.PERSISTENT_AGENT_ASSIGNED,
    ):
        channels.append("persistent-agents:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_OVERLAP_DETECTED,
        TraceEventKind.RUNTIME_CONFLICT_RESOLVED,
    ):
        channels.append("runtime-coordination:runtime")
    if event.kind == TraceEventKind.COGNITIVE_STATE_UPDATED:
        channels.append("cognitive-state:runtime")
    if event.kind in (
        TraceEventKind.OVERNIGHT_CYCLE_STARTED,
        TraceEventKind.OVERNIGHT_CYCLE_COMPLETED,
        TraceEventKind.IDLE_REASONING_EXECUTED,
    ):
        channels.append("overnight:runtime")
    if event.kind in (
        TraceEventKind.REASONING_CHAIN_DEFERRED,
        TraceEventKind.REASONING_CHAIN_RESTORED,
    ):
        channels.append("deferred-reasoning:runtime")
    if event.kind in (
        TraceEventKind.CONTINUITY_FORECAST_GENERATED,
        TraceEventKind.ABANDONED_WORK_DETECTED,
    ):
        channels.append("continuity-forecast:runtime")
    if event.kind == TraceEventKind.MORNING_BRIEFING_GENERATED:
        channels.append("morning-briefing:runtime")
    if event.kind in (
        TraceEventKind.MEMORY_THREADS_COMPACTED,
        TraceEventKind.RUNTIME_STATE_STABILIZED,
    ):
        channels.append("maintenance:runtime")
    if event.kind in (
        TraceEventKind.IDLE_ENGINEERING_ANALYSIS_COMPLETED,
        TraceEventKind.REGRESSION_RISK_SIMULATED,
    ):
        channels.append("idle-engineering:runtime")
    if event.kind in (
        TraceEventKind.DESKTOP_RUNTIME_INITIALIZED,
        TraceEventKind.NATIVE_NOTIFICATION_DISPATCHED,
    ):
        channels.append("native-desktop:runtime")
    if event.kind in (
        TraceEventKind.WORKSPACE_TRANSITION_DETECTED,
        TraceEventKind.ACTIVE_WINDOW_CLASSIFIED,
    ):
        channels.append("window-awareness:runtime")
    if event.kind in (
        TraceEventKind.OVERLAY_CONTEXT_UPDATED,
        TraceEventKind.OVERLAY_SUPPRESSED,
    ):
        channels.append("live-overlays-v2:runtime")
    if event.kind in (
        TraceEventKind.WORKSPACE_SESSION_SAVED,
        TraceEventKind.WORKSPACE_SESSION_RESTORED,
    ):
        channels.append("workspace-sessions:runtime")
    if event.kind in (
        TraceEventKind.FOCUS_SESSION_STARTED,
        TraceEventKind.FOCUS_BREAKDOWN_DETECTED,
    ):
        channels.append("operator-focus:runtime")
    if event.kind in (
        TraceEventKind.DESKTOP_ATTENTION_REBALANCED,
        TraceEventKind.WORKSPACE_SALIENCE_UPDATED,
    ):
        channels.append("desktop-attention:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_COORDINATION_STARTED,
        TraceEventKind.RUNTIME_COORDINATION_RESTORED,
    ):
        channels.append("autonomous-coordination:runtime")
    if event.kind in (
        TraceEventKind.OBJECTIVE_TREE_CREATED,
        TraceEventKind.OBJECTIVE_PROGRESS_UPDATED,
        TraceEventKind.STALLED_OBJECTIVE_DETECTED,
    ):
        channels.append("objective-management:runtime")
    if event.kind in (
        TraceEventKind.CONTEXT_SURFACES_SYNCHRONIZED,
        TraceEventKind.CONTEXT_DIVERGENCE_DETECTED,
    ):
        channels.append("context-sync:runtime")
    if event.kind in (
        TraceEventKind.MISSION_RESUME_CHAIN_BUILT,
        TraceEventKind.WORKFLOW_INTERRUPTION_DETECTED,
    ):
        channels.append("mission-continuity:runtime")
    if event.kind in (
        TraceEventKind.COGNITIVE_PLAN_GENERATED,
        TraceEventKind.REASONING_BUDGET_REBALANCED,
    ):
        channels.append("cognitive-planning:runtime")
    if event.kind == TraceEventKind.OPERATOR_ALIGNMENT_UPDATED:
        channels.append("operator-alignment:runtime")
    if event.kind in (
        TraceEventKind.ORCHESTRATION_STATE_STREAMED,
        TraceEventKind.RUNTIME_INSTABILITY_DETECTED,
    ):
        channels.append("live-orchestration:runtime")
    if event.kind in (
        TraceEventKind.OBJECTIVE_STREAM_UPDATED,
        TraceEventKind.OBJECTIVE_STAGNATION_DETECTED,
    ):
        channels.append("objective-streams:runtime")
    if event.kind == TraceEventKind.MISSION_GRAPH_LINKED:
        channels.append("mission-graph:runtime")
    if event.kind in (
        TraceEventKind.COORDINATION_PRESSURE_UPDATED,
        TraceEventKind.RUNTIME_STREAM_MULTIPLEXED,
    ):
        channels.append("realtime-coordination:runtime")
    if event.kind in (
        TraceEventKind.OPERATOR_BRIEF_GENERATED,
        TraceEventKind.OPERATIONAL_PRESSURE_FORECASTED,
    ):
        channels.append("operator-awareness:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_CONSTELLATION_RENDERED,
        TraceEventKind.OBJECTIVE_RIVER_RENDERED,
        TraceEventKind.COGNITIVE_VISUAL_DENSITY_COMPRESSED,
    ):
        channels.append("visual-layers:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_PIPELINE_INITIALIZED,
        TraceEventKind.EXECUTION_STAGE_CHECKPOINTED,
        TraceEventKind.EXECUTION_STAGE_ROLLED_BACK,
        TraceEventKind.EXECUTION_HEALTH_UPDATED,
    ):
        channels.append("execution-system:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_QUEUE_REBALANCED,
        TraceEventKind.EXECUTION_BLOCKER_DETECTED,
    ):
        channels.append("task-orchestration:runtime")
    if event.kind in (
        TraceEventKind.AGENT_COLLABORATION_STARTED,
        TraceEventKind.CONSENSUS_SCORE_UPDATED,
    ):
        channels.append("agent-collaboration:runtime")
    if event.kind == TraceEventKind.WORKSPACE_OPERATION_RECOVERED:
        channels.append("workspace-operations:runtime")
    if event.kind == TraceEventKind.EXECUTION_CHAIN_PERSISTED:
        channels.append("execution-memory:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_VISIBILITY_STREAMED,
        TraceEventKind.EXECUTION_PRESSURE_UPDATED,
    ):
        channels.append("execution-visibility:runtime")
    if event.kind in (
        TraceEventKind.DISTRIBUTED_EXECUTION_FEDERATED,
        TraceEventKind.DISTRIBUTED_PIPELINE_SYNCHRONIZED,
    ):
        channels.append("distributed-execution:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_DAG_GENERATED,
        TraceEventKind.ROLLBACK_GRAPH_GENERATED,
    ):
        channels.append("execution-graph:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_FAILURE_FORECASTED,
        TraceEventKind.RECOVERY_PATH_SIMULATED,
    ):
        channels.append("predictive-recovery:runtime")
    if event.kind in (
        TraceEventKind.WORKSPACE_CONTEXTS_SYNCHRONIZED,
        TraceEventKind.WORKSPACE_DEPENDENCY_PRESSURE_UPDATED,
    ):
        channels.append("cross-workspace:runtime")
    if event.kind in (
        TraceEventKind.OPERATOR_INTERVENTION_FORECASTED,
        TraceEventKind.OPERATOR_OVERLOAD_DETECTED,
    ):
        channels.append("intervention-intelligence:runtime")
    if event.kind in (
        TraceEventKind.AUTONOMOUS_WORKFLOW_CONTINUED,
        TraceEventKind.WORKFLOW_STATE_CHECKPOINTED,
    ):
        channels.append("autonomous-workflows:runtime")
    if event.kind in (
        TraceEventKind.GOVERNANCE_CYCLE_INITIALIZED,
        TraceEventKind.GOVERNANCE_PRESSURE_REBALANCED,
    ):
        channels.append("predictive-governance:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_INSTABILITY_DETECTED,
        TraceEventKind.RUNTIME_STABILIZATION_APPLIED,
    ):
        channels.append("runtime-stabilization:runtime")
    if event.kind in (
        TraceEventKind.COGNITIVE_RISK_FORECASTED,
        TraceEventKind.FAILURE_CHAIN_SIMULATED,
        TraceEventKind.GOVERNANCE_DRIFT_DETECTED,
    ):
        channels.append("cognitive-risk:runtime")
    if event.kind in (
        TraceEventKind.OPERATOR_TRUST_UPDATED,
        TraceEventKind.SUPERVISION_INTEGRITY_EVALUATED,
    ):
        channels.append("trust-surfaces:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_CONFIDENCE_ESTIMATED,
        TraceEventKind.WORKFLOW_COMPLETION_FORECASTED,
    ):
        channels.append("execution-confidence:runtime")
    if event.kind == TraceEventKind.GOVERNANCE_SURFACE_RENDERED:
        channels.append("governance-visualization:runtime")
    if event.kind in (
        TraceEventKind.COMMAND_CENTER_INITIALIZED,
        TraceEventKind.RUNTIME_LAYERS_SYNCHRONIZED,
        TraceEventKind.GLOBAL_OPERATIONAL_HEALTH_UPDATED,
    ):
        channels.append("unified-command:runtime")
    if event.kind in (
        TraceEventKind.MISSION_PHASE_TRANSITIONED,
        TraceEventKind.OBJECTIVE_GRAPH_SYNCHRONIZED,
    ):
        channels.append("mission-command:runtime")
    if event.kind in (
        TraceEventKind.COGNITION_STREAMS_MULTIPLEXED,
        TraceEventKind.RUNTIME_STREAMS_COMPRESSED,
    ):
        channels.append("cognitive-multiplexing:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_CONTEXTS_FUSED,
        TraceEventKind.CROSS_RUNTIME_PRESSURE_STABILIZED,
    ):
        channels.append("runtime-fusion:runtime")
    if event.kind in (
        TraceEventKind.COMMAND_SURFACE_RENDERED,
        TraceEventKind.OPERATIONAL_OVERLAY_UPDATED,
    ):
        channels.append("operator-command-surfaces:runtime")
    if event.kind in (
        TraceEventKind.COGNITION_TIMELINE_APPENDED,
        TraceEventKind.COGNITION_WINDOW_REPLAYED,
    ):
        channels.append("live-cognition-timeline:runtime")
    if event.kind in (
        TraceEventKind.OPERATIONAL_FAILURE_FORECASTED,
        TraceEventKind.RECOVERY_PATHS_SIMULATED,
        TraceEventKind.RECOVERY_PROBABILITY_ESTIMATED,
    ):
        channels.append("predictive-recovery-v2:runtime")
    if event.kind in (
        TraceEventKind.RECOVERY_CYCLE_INITIALIZED,
        TraceEventKind.RECOVERY_PHASE_TRANSITIONED,
    ):
        channels.append("recovery-orchestration:runtime")
    if event.kind in (
        TraceEventKind.ROLLBACK_GRAPH_GENERATED,
        TraceEventKind.ROLLBACK_CONFIDENCE_ESTIMATED,
        TraceEventKind.EXECUTION_WINDOW_REPLAYED,
    ):
        channels.append("rollback-intelligence:runtime")
    if event.kind in (
        TraceEventKind.MISSION_CONTINUITY_RESTORED,
        TraceEventKind.WORKSPACE_CONTEXT_REBUILT,
    ):
        channels.append("continuity-recovery:runtime")
    if event.kind in (
        TraceEventKind.STABILITY_LOOP_INITIALIZED,
        TraceEventKind.INSTABILITY_CASCADE_SUPPRESSED,
        TraceEventKind.RECOVERY_DENSITY_THROTTLED,
    ):
        channels.append("stability-loops:runtime")
    if event.kind in (
        TraceEventKind.OPERATOR_VETO_REQUESTED,
        TraceEventKind.RECOVERY_CHAIN_AUTHORIZED,
        TraceEventKind.RECOVERY_PATH_VETOED,
    ):
        channels.append("operator-veto:runtime")
    if event.kind == TraceEventKind.COLLABORATIVE_COGNITION_INITIALIZED:
        channels.append("collaborative-cognition:runtime")
    if event.kind in (
        TraceEventKind.OPERATOR_SESSION_CREATED,
        TraceEventKind.OPERATOR_SESSION_RESTORED,
    ):
        channels.append("operator-sessions:runtime")
    if event.kind in (
        TraceEventKind.SHARED_MISSION_CREATED,
        TraceEventKind.MISSION_CONTROL_TRANSFERRED,
    ):
        channels.append("shared-mission-control:runtime")
    if event.kind in (
        TraceEventKind.DELEGATION_CHAIN_CREATED,
        TraceEventKind.DELEGATION_AUTHORITY_VALIDATED,
    ):
        channels.append("delegation-engine:runtime")
    if event.kind in (
        TraceEventKind.TEAM_ATTENTION_REBALANCED,
        TraceEventKind.TEAM_PRESSURE_UPDATED,
        TraceEventKind.CROSS_OPERATOR_NOISE_SUPPRESSED,
    ):
        channels.append("team-coordination:runtime")
    if event.kind in (
        TraceEventKind.COLLABORATIVE_RECOVERY_REQUESTED,
        TraceEventKind.SHARED_RECOVERY_AUTHORIZED,
        TraceEventKind.COLLABORATIVE_ROLLBACK_GENERATED,
        TraceEventKind.SHARED_CONTINUITY_RESTORED,
    ):
        channels.append("collaborative-recovery:runtime")
    if event.kind in (
        TraceEventKind.ROLLBACK_ANIMATION_INITIALIZED,
        TraceEventKind.ROLLBACK_DAG_ANIMATED,
        TraceEventKind.EXECUTION_CHAIN_REPLAYED,
        TraceEventKind.ROLLBACK_RENDER_STABILIZED,
    ):
        channels.append("rollback-animation:runtime")
    if event.kind in (
        TraceEventKind.CAUSALITY_GRAPH_GENERATED,
        TraceEventKind.FAILURE_CHAIN_TRACED,
        TraceEventKind.RUNTIME_DEPENDENCY_MAPPED,
        TraceEventKind.REASONING_PATH_RECONSTRUCTED,
    ):
        channels.append("causality-mapping:runtime")
    if event.kind in (
        TraceEventKind.REPLAY_WINDOW_INITIALIZED,
        TraceEventKind.COGNITION_TIMELINE_REPLAYED,
        TraceEventKind.REPLAY_STATE_CHECKPOINTED,
        TraceEventKind.REPLAY_DENSITY_THROTTLED,
    ):
        channels.append("replay-orchestration:runtime")
    if event.kind in (
        TraceEventKind.RUNTIME_PRESSURE_PROPAGATED,
        TraceEventKind.PRESSURE_DIFFUSION_SIMULATED,
        TraceEventKind.EXECUTION_CONGESTION_DETECTED,
        TraceEventKind.PRESSURE_SURFACES_REBALANCED,
    ):
        channels.append("pressure-propagation:runtime")
    if event.kind in (
        TraceEventKind.OPERATIONAL_TIMELINE_RENDERED,
        TraceEventKind.TIMELINE_WINDOW_COMPRESSED,
        TraceEventKind.TIMELINE_LAYERS_SYNCHRONIZED,
        TraceEventKind.TIMELINE_OVERLAY_GENERATED,
    ):
        channels.append("timeline-visualization:runtime")
    if event.kind in (
        TraceEventKind.EXECUTION_STATE_RECONSTRUCTED,
        TraceEventKind.WORKSPACE_SEQUENCE_REBUILT,
        TraceEventKind.COGNITION_WINDOW_RESTORED,
        TraceEventKind.EXECUTION_RESTORE_SIMULATED,
    ):
        channels.append("execution-reconstruction:runtime")
    if event.kind == TraceEventKind.MODEL_LOADED:
        channels.append("models:runtime")
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
