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
    PERCEPTION_UPDATED = "perception_updated"
    WORKSPACE_DETECTED = "workspace_detected"
    SCREEN_PARSED = "screen_parsed"
    VOICE_SESSION_STARTED = "voice_session_started"
    COPILOT_SUGGESTION_GENERATED = "copilot_suggestion_generated"
    APPROVAL_REQUESTED = "approval_requested"
    WORKSPACE_PATTERN_LEARNED = "workspace_pattern_learned"
    PROACTIVE_ASSISTANCE_TRIGGERED = "proactive_assistance_triggered"
    COLLABORATION_FEEDBACK_RECEIVED = "collaboration_feedback_received"
    ACTION_PROPOSED = "action_proposed"
    ACTION_APPROVED = "action_approved"
    ACTION_EXECUTED = "action_executed"
    ACTION_REVERTED = "action_reverted"
    WORKFLOW_RECORDED = "workflow_recorded"
    MACRO_GENERATED = "macro_generated"
    BROWSER_NAVIGATION = "browser_navigation"
    AUTOMATION_INTERRUPTED = "automation_interrupted"
    DESTRUCTIVE_ACTION_BLOCKED = "destructive_action_blocked"
    OVERLAY_RENDERED = "overlay_rendered"
    KNOWLEDGE_CREATED = "knowledge_created"
    BELIEF_UPDATED = "belief_updated"
    SOURCE_VERIFIED = "source_verified"
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"
    TREND_DETECTED = "trend_detected"
    HYPOTHESIS_GENERATED = "hypothesis_generated"
    WORLD_MODEL_UPDATED = "world_model_updated"
    STALE_KNOWLEDGE_DETECTED = "stale_knowledge_detected"
    AGENT_SPAWNED = "agent_spawned"
    EXPERTISE_UPDATED = "expertise_updated"
    DELEGATION_CREATED = "delegation_created"
    DEBATE_STARTED = "debate_started"
    CONSENSUS_REACHED = "consensus_reached"
    COLLABORATION_FORMED = "collaboration_formed"
    OBJECTIVE_ASSIGNED = "objective_assigned"
    CONTINUITY_RESTORED = "continuity_restored"
    REASONING_SHARED = "reasoning_shared"
    AGENT_REFLECTION_GENERATED = "agent_reflection_generated"
    FEDERATION_NODE_CONNECTED = "federation_node_connected"
    FEDERATION_NODE_DISCONNECTED = "federation_node_disconnected"
    REMOTE_REASONING_REQUESTED = "remote_reasoning_requested"
    REMOTE_REASONING_COMPLETED = "remote_reasoning_completed"
    STRATEGY_GENERATED = "strategy_generated"
    SIMULATION_PROJECTED = "simulation_projected"
    PREDICTION_UPDATED = "prediction_updated"
    WORLD_STATE_CHANGED = "world_state_changed"
    TRUST_SCORE_CHANGED = "trust_score_changed"
    GOVERNANCE_VIOLATION = "governance_violation"
    NODE_QUARANTINED = "node_quarantined"
    KNOWLEDGE_SHARED = "knowledge_shared"
    MEMORY_CONSOLIDATED = "memory_consolidated"
    POLICY_OPTIMIZED = "policy_optimized"
    ROUTING_OPTIMIZED = "routing_optimized"
    COGNITION_BUDGET_UPDATED = "cognition_budget_updated"
    META_ANALYSIS_GENERATED = "meta_analysis_generated"
    HALLUCINATION_DETECTED = "hallucination_detected"
    OPERATOR_PATTERN_LEARNED = "operator_pattern_learned"
    WORKLOAD_REBALANCED = "workload_rebalanced"
    EVOLUTION_CYCLE_COMPLETED = "evolution_cycle_completed"
    MEMORY_INDEXED = "memory_indexed"
    TASK_DELEGATED = "task_delegated"
    VOICE_TURN_COMPLETED = "voice_turn_completed"
    BENCHMARK_COMPLETED = "benchmark_completed"
    REGRESSION_DETECTED = "regression_detected"
    RESOURCE_OPTIMIZED = "resource_optimized"
    DAEMON_STARTED = "daemon_started"
    RUNTIME_RECOVERED = "runtime_recovered"
    DEGRADED_MODE_ENABLED = "degraded_mode_enabled"
    DAEMON_RESTORED = "daemon_restored"
    AUTOMATION_VERIFIED = "automation_verified"
    ACTION_RETRY_GENERATED = "action_retry_generated"
    EXECUTION_SALVAGED = "execution_salvaged"
    MEMORY_COMPACTED = "memory_compacted"
    WATCHDOG_TRIGGERED = "watchdog_triggered"
    RUNTIME_REPAIRED = "runtime_repaired"
    WORKSPACE_RESTORED = "workspace_restored"
    PROJECT_CONTEXT_RESTORED = "project_context_restored"
    REPOSITORY_INDEXED = "repository_indexed"
    WORKSPACE_LINKED = "workspace_linked"
    SEMANTIC_SEARCH_COMPLETED = "semantic_search_completed"
    PRODUCTIVITY_PATTERN_DETECTED = "productivity_pattern_detected"
    FOCUS_SESSION_STARTED = "focus_session_started"
    BRIEFING_GENERATED = "briefing_generated"
    CODING_SESSION_RESUMED = "coding_session_resumed"
    KNOWLEDGE_CLUSTER_CREATED = "knowledge_cluster_created"
    RETRIEVAL_OPTIMIZED = "retrieval_optimized"
    RUNTIME_PROFILE_CHANGED = "runtime_profile_changed"
    STARTUP_OPTIMIZED = "startup_optimized"
    DAEMON_RESTARTED = "daemon_restarted"
    MEMORY_PRESSURE_DETECTED = "memory_pressure_detected"
    MODEL_SWAPPED = "model_swapped"
    RECOVERY_COMPLETED = "recovery_completed"
    SNAPSHOT_RESTORED = "snapshot_restored"
    DEPLOYMENT_VALIDATED = "deployment_validated"
    COMMAND_EXECUTED = "command_executed"
    PRIVACY_FILTER_TRIGGERED = "privacy_filter_triggered"


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
