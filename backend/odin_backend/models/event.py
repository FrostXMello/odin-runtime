"""Event domain schemas — event-driven communication."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.models.task import AgentId


class EventType(StrEnum):
    """Canonical system events."""

    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"

    MEMORY_UPDATED = "memory.updated"
    MEMORY_RETRIEVED = "memory.retrieved"

    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_TRIGGERED = "workflow.triggered"
    WORKFLOW_STEP_STARTED = "workflow.step_started"
    WORKFLOW_STEP_COMPLETED = "workflow.step_completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    REASONING_STARTED = "reasoning.started"
    REASONING_COMPLETED = "reasoning.completed"

    TOOL_FAILED = "tool.failed"

    AGENT_REGISTERED = "agent.registered"
    AGENT_HEARTBEAT = "agent.heartbeat"
    AGENT_FAILED = "agent.failed"

    TOOL_EXECUTED = "tool.executed"
    TOOL_DENIED = "tool.denied"

    SECURITY_ALERT = "security.alert"
    PERMISSION_REQUESTED = "permission.requested"
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_DENIED = "permission.denied"

    SYSTEM_STARTED = "system.started"
    SYSTEM_SHUTDOWN = "system.shutdown"

    # Cognition streaming
    COGNITION_PROGRESS = "cognition.progress"

    # Runtime
    RUNTIME_HEARTBEAT = "runtime.heartbeat"
    RUNTIME_SERVICE_STARTED = "runtime.service_started"
    RUNTIME_SERVICE_FAILED = "runtime.service_failed"
    RUNTIME_RECOVERY = "runtime.recovery"

    # Watchers (monitor only — no dangerous execution)
    WATCHER_INSIGHT = "watcher.insight"
    RECOMMENDATION_CREATED = "recommendation.created"

    # Browser / context / voice
    BROWSER_SESSION_UPDATED = "browser.session_updated"
    CONTEXT_UPDATED = "context.updated"
    VOICE_SESSION_STARTED = "voice.session_started"
    VOICE_CHUNK = "voice.chunk"
    VOICE_PARTIAL_TRANSCRIPT = "voice.partial_transcript"
    VOICE_INTERRUPTED = "voice.interrupted"

    # Conversation
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_MESSAGE = "conversation.message"
    CONVERSATION_OBJECTIVE_UPDATED = "conversation.objective_updated"

    # Workflows — long-running
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_CHECKPOINT = "workflow.checkpoint"

    # Reflection
    REFLECTION_COMPLETED = "reflection.completed"

    # Sandbox
    SANDBOX_EXECUTION = "sandbox.execution"

    # Knowledge graph
    KNOWLEDGE_GRAPH_UPDATED = "knowledge_graph.updated"

    # Milestone 5 — ambient cognitive layer
    CONTEXT_ENGINE_UPDATED = "context_engine.updated"
    DESKTOP_SEMANTICS_UPDATED = "desktop.semantics_updated"
    EXECUTION_INTELLIGENCE_UPDATED = "execution_intelligence.updated"
    AGENT_COLLABORATION = "agent.collaboration"
    COGNITIVE_STREAM_ENTRY = "cognitive_stream.entry"
    MEMORY_CONSOLIDATED = "memory.consolidated"
    LOCAL_MODEL_UPDATED = "local_model.updated"
    POLICY_DENIED = "policy.denied"

    # Milestone 6 — persistent operating environment
    DESKTOP_RUNTIME_EVENT = "desktop.runtime.event"
    WORKSPACE_INTELLIGENCE_UPDATED = "workspace.intelligence_updated"
    LIVE_COGNITION_UPDATED = "live.cognition.updated"
    RESILIENCE_RECOVERY = "resilience.recovery"
    MEMORY_EVOLUTION_UPDATED = "memory.evolution.updated"
    COMPUTE_UPDATED = "compute.updated"
    SECURITY_ESCALATION = "security.escalation"

    # Cognitive kernel (Milestone 7)
    KERNEL_STATE_UPDATED = "kernel.state_updated"
    GOVERNOR_DECISION = "governor.decision"
    SIGNAL_RECEIVED = "signal.received"

    # Milestone 8 — cognitive stability
    COHERENCE_UPDATED = "coherence.updated"
    STABILITY_CORRECTIVE = "stability.corrective"
    MEMORY_REFINED = "memory.refined"
    SNAPSHOT_CREATED = "snapshot.created"

    # Milestone 9 — data architecture & agent protocol
    AGENT_MESSAGE_RECEIVED = "agent.message.received"
    TASK_GRAPH_UPDATED = "task_graph.updated"
    EXECUTION_PIPELINE_STEP = "execution.pipeline.step"

    # Milestone 10 — runtime conscious loop
    CONSCIOUS_LOOP_TICK = "conscious.loop.tick"
    CONSCIOUS_LOOP_ESCALATION = "conscious.loop.escalation"

    # Milestone 11 — live runtime
    LIVE_CYCLE_COMPLETED = "live.cycle.completed"
    LIVE_CYCLE_ESCALATION = "live.cycle.escalation"

    # Milestone 15 — active perception
    PERCEPTION_EVENT = "perception.event"
    EXECUTION_RESULT = "execution.result"
    ENVIRONMENT_CHANGE = "environment.change"
    MISSION_FEEDBACK = "mission.feedback"
    FAILURE_DETECTED = "failure.detected"
    GOAL_DRIFT = "goal.drift"
    RESOURCE_WARNING = "resource.warning"


class Event(BaseModel):
    """Immutable event envelope."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    source: AgentId | str = AgentId.ODIN
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None
    task_id: str | None = None
    workflow_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_bus_message(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
