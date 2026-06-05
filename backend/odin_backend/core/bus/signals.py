"""Unified signals — universal event format for kernel processing."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field

from odin_backend.models.event import Event, EventType


class SignalSource(StrEnum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"


class SignalOrigin(StrEnum):
    """Signal origin — controls kernel eligibility and recursion isolation."""

    EXTERNAL = "external"
    INTERNAL_RUNTIME = "internal_runtime"
    KERNEL_INTERNAL = "kernel_internal"
    STABILITY_INTERNAL = "stability_internal"
    WATCHER_INTERNAL = "watcher_internal"
    SYSTEM_HEALTH = "system_health"
    MEMORY_INTERNAL = "memory_internal"


class SignalKind(StrEnum):
    MEMORY = "memory"
    WORKFLOW = "workflow"
    DESKTOP = "desktop"
    BROWSER = "browser"
    AGENT = "agent"
    COGNITION = "cognition"
    TOOL = "tool"
    SECURITY = "security"
    VOICE = "voice"
    CONVERSATION = "conversation"
    SYSTEM = "system"
    RECOMMENDATION = "recommendation"
    TASK = "task"
    PERCEPTION = "perception"


class Signal(BaseModel):
    """
    Canonical signal envelope.

    Prompt 9 fields: id, timestamp, source, type, priority, payload,
    context_refs, requires_response.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "system"
    source_kind: SignalSource = SignalSource.SYSTEM
    origin: SignalOrigin = SignalOrigin.INTERNAL_RUNTIME
    type: str = "system.event"
    priority: int = Field(default=50, ge=0, le=100)
    payload: dict[str, Any] = Field(default_factory=dict)
    context_refs: list[str] = Field(default_factory=list)
    requires_response: bool = False

    # Extended routing (backward compatible)
    kind: SignalKind = SignalKind.SYSTEM
    name: str = "system.event"
    correlation_id: str | None = None
    workflow_id: str | None = None
    task_id: str | None = None
    priority_hint: float = 0.5

    @computed_field  # type: ignore[prop-decorator]
    @property
    def unified_type(self) -> str:
        return self.type or f"{self.kind.value}.{self.name}"

    @classmethod
    def from_event(cls, event: Event) -> "Signal":
        kind, name = _classify_event(event.type)
        hint = _priority_hint(event.type)
        source_kind = _source_kind(event)
        type_str = f"{kind.value}.{name}"
        refs: list[str] = []
        if event.workflow_id:
            refs.append(f"workflow:{event.workflow_id}")
        if event.task_id:
            refs.append(f"task:{event.task_id}")
        if event.correlation_id:
            refs.append(f"correlation:{event.correlation_id}")

        origin = origin_from_event(event)

        return cls(
            kind=kind,
            name=name,
            type=type_str,
            source=str(event.source),
            source_kind=source_kind,
            origin=origin,
            correlation_id=event.correlation_id,
            workflow_id=event.workflow_id,
            task_id=event.task_id,
            payload=event.payload,
            priority_hint=hint,
            priority=int(hint * 100),
            context_refs=refs,
            requires_response=_requires_response(event.type),
        )

    @classmethod
    def from_agent_message(cls, message: Any) -> "Signal":
        from odin_backend.models.agent_message import AgentMessage

        msg: AgentMessage = message
        priority = 90 if msg.requires_escalation else 60
        return cls(
            kind=SignalKind.AGENT,
            name=f"agent.{msg.type.value}",
            type=f"agent.{msg.type.value}",
            source=msg.from_agent,
            source_kind=SignalSource.AGENT,
            origin=SignalOrigin.EXTERNAL,
            task_id=msg.task_id or None,
            payload=msg.payload,
            priority=priority,
            priority_hint=priority / 100.0,
            context_refs=[f"task:{msg.task_id}"] if msg.task_id else [],
            requires_response=msg.type.value in ("request", "alert"),
        )


def _source_kind(event: Event) -> SignalSource:
    src = str(event.source).lower()
    if src in ("user", "human"):
        return SignalSource.USER
    if src in ("odin", "system", "kernel"):
        return SignalSource.SYSTEM
    if event.type.value.startswith("tool."):
        return SignalSource.TOOL
    try:
        from odin_backend.models.task import AgentId

        AgentId(src)
        return SignalSource.AGENT
    except ValueError:
        return SignalSource.AGENT if src not in ("system", "odin") else SignalSource.SYSTEM


def _requires_response(event_type: EventType) -> bool:
    return event_type in {
        EventType.PERMISSION_REQUESTED,
        EventType.SECURITY_ESCALATION,
        EventType.AGENT_COLLABORATION,
    }


def _classify_event(event_type: EventType) -> tuple[SignalKind, str]:
    mapping: dict[EventType, tuple[SignalKind, str]] = {
        EventType.TASK_CREATED: (SignalKind.TASK, "task.created"),
        EventType.TASK_STARTED: (SignalKind.TASK, "task.started"),
        EventType.TASK_COMPLETED: (SignalKind.TASK, "task.completed"),
        EventType.TASK_FAILED: (SignalKind.TASK, "task.failed"),
        EventType.TASK_CANCELLED: (SignalKind.TASK, "task.cancelled"),
        EventType.MEMORY_UPDATED: (SignalKind.MEMORY, "memory.updated"),
        EventType.MEMORY_RETRIEVED: (SignalKind.MEMORY, "memory.retrieved"),
        EventType.MEMORY_CONSOLIDATED: (SignalKind.MEMORY, "memory.consolidated"),
        EventType.MEMORY_EVOLUTION_UPDATED: (SignalKind.MEMORY, "memory.evolution"),
        EventType.WORKFLOW_CREATED: (SignalKind.WORKFLOW, "workflow.created"),
        EventType.WORKFLOW_TRIGGERED: (SignalKind.WORKFLOW, "workflow.started"),
        EventType.WORKFLOW_STEP_STARTED: (SignalKind.WORKFLOW, "workflow.step_started"),
        EventType.WORKFLOW_COMPLETED: (SignalKind.WORKFLOW, "workflow.completed"),
        EventType.WORKFLOW_FAILED: (SignalKind.WORKFLOW, "workflow.failed"),
        EventType.DESKTOP_RUNTIME_EVENT: (SignalKind.DESKTOP, "desktop.focus.changed"),
        EventType.CONTEXT_ENGINE_UPDATED: (SignalKind.DESKTOP, "desktop.context.updated"),
        EventType.CONTEXT_UPDATED: (SignalKind.DESKTOP, "desktop.context.updated"),
        EventType.BROWSER_SESSION_UPDATED: (SignalKind.BROWSER, "browser.context.updated"),
        EventType.AGENT_COLLABORATION: (SignalKind.AGENT, "agent.request"),
        EventType.AGENT_HEARTBEAT: (SignalKind.AGENT, "agent.heartbeat"),
        EventType.COGNITION_PROGRESS: (SignalKind.COGNITION, "cognition.shift"),
        EventType.COGNITIVE_STREAM_ENTRY: (SignalKind.COGNITION, "cognition.shift"),
        EventType.LIVE_COGNITION_UPDATED: (SignalKind.COGNITION, "cognition.shift"),
        EventType.TOOL_EXECUTED: (SignalKind.TOOL, "tool.executed"),
        EventType.TOOL_DENIED: (SignalKind.TOOL, "tool.denied"),
        EventType.TOOL_FAILED: (SignalKind.TOOL, "tool.failed"),
        EventType.PERMISSION_REQUESTED: (SignalKind.SECURITY, "security.permission"),
        EventType.PERMISSION_DENIED: (SignalKind.SECURITY, "security.denied"),
        EventType.POLICY_DENIED: (SignalKind.SECURITY, "security.policy_denied"),
        EventType.SECURITY_ESCALATION: (SignalKind.SECURITY, "security.escalation"),
        EventType.VOICE_SESSION_STARTED: (SignalKind.VOICE, "voice.session"),
        EventType.VOICE_CHUNK: (SignalKind.VOICE, "voice.chunk"),
        EventType.CONVERSATION_MESSAGE: (SignalKind.CONVERSATION, "conversation.message"),
        EventType.RECOMMENDATION_CREATED: (SignalKind.RECOMMENDATION, "recommendation.created"),
        EventType.KERNEL_STATE_UPDATED: (SignalKind.SYSTEM, "kernel.state_updated"),
        EventType.GOVERNOR_DECISION: (SignalKind.SYSTEM, "governor.decision"),
        EventType.AGENT_MESSAGE_RECEIVED: (SignalKind.AGENT, "agent.message"),
        EventType.CONSCIOUS_LOOP_TICK: (SignalKind.SYSTEM, "conscious.tick"),
        EventType.CONSCIOUS_LOOP_ESCALATION: (SignalKind.SYSTEM, "conscious.escalation"),
        EventType.LIVE_CYCLE_COMPLETED: (SignalKind.SYSTEM, "live.cycle.completed"),
        EventType.LIVE_CYCLE_ESCALATION: (SignalKind.SYSTEM, "live.cycle.escalation"),
        EventType.PERCEPTION_EVENT: (SignalKind.PERCEPTION, "perception.event"),
        EventType.EXECUTION_RESULT: (SignalKind.PERCEPTION, "execution.result"),
        EventType.ENVIRONMENT_CHANGE: (SignalKind.PERCEPTION, "environment.change"),
        EventType.MISSION_FEEDBACK: (SignalKind.PERCEPTION, "mission.feedback"),
        EventType.FAILURE_DETECTED: (SignalKind.PERCEPTION, "failure.detected"),
        EventType.GOAL_DRIFT: (SignalKind.PERCEPTION, "goal.drift"),
        EventType.RESOURCE_WARNING: (SignalKind.PERCEPTION, "resource.warning"),
    }
    return mapping.get(event_type, (SignalKind.SYSTEM, event_type.value))


_KERNEL_INTERNAL: frozenset[EventType] = frozenset(
    {
        EventType.KERNEL_STATE_UPDATED,
        EventType.GOVERNOR_DECISION,
        EventType.SIGNAL_RECEIVED,
        EventType.TASK_GRAPH_UPDATED,
        EventType.EXECUTION_PIPELINE_STEP,
        EventType.COHERENCE_UPDATED,
        EventType.SNAPSHOT_CREATED,
        EventType.MEMORY_REFINED,
    }
)

_STABILITY_INTERNAL: frozenset[EventType] = frozenset({EventType.STABILITY_CORRECTIVE})

_WATCHER_INTERNAL: frozenset[EventType] = frozenset({EventType.WATCHER_INSIGHT})

_SYSTEM_HEALTH: frozenset[EventType] = frozenset(
    {
        EventType.RUNTIME_HEARTBEAT,
        EventType.RUNTIME_SERVICE_STARTED,
        EventType.RUNTIME_SERVICE_FAILED,
        EventType.RUNTIME_RECOVERY,
        EventType.AGENT_HEARTBEAT,
        EventType.SYSTEM_STARTED,
        EventType.SYSTEM_SHUTDOWN,
        EventType.AGENT_REGISTERED,
        EventType.AGENT_FAILED,
        EventType.RESILIENCE_RECOVERY,
    }
)

_MEMORY_INTERNAL: frozenset[EventType] = frozenset(
    {
        EventType.MEMORY_UPDATED,
        EventType.MEMORY_RETRIEVED,
        EventType.MEMORY_CONSOLIDATED,
        EventType.MEMORY_EVOLUTION_UPDATED,
        EventType.KNOWLEDGE_GRAPH_UPDATED,
    }
)

_INTERNAL_RUNTIME: frozenset[EventType] = frozenset(
    {
        EventType.COGNITION_PROGRESS,
        EventType.COGNITIVE_STREAM_ENTRY,
        EventType.LIVE_COGNITION_UPDATED,
        EventType.CONSCIOUS_LOOP_TICK,
        EventType.CONSCIOUS_LOOP_ESCALATION,
        EventType.LIVE_CYCLE_COMPLETED,
        EventType.LIVE_CYCLE_ESCALATION,
        EventType.REASONING_STARTED,
        EventType.REASONING_COMPLETED,
        EventType.COMPUTE_UPDATED,
        EventType.LOCAL_MODEL_UPDATED,
        EventType.EXECUTION_INTELLIGENCE_UPDATED,
        EventType.WORKSPACE_INTELLIGENCE_UPDATED,
        EventType.DESKTOP_SEMANTICS_UPDATED,
        EventType.CONTEXT_ENGINE_UPDATED,
        EventType.CONTEXT_UPDATED,
        EventType.PERCEPTION_EVENT,
        EventType.EXECUTION_RESULT,
        EventType.ENVIRONMENT_CHANGE,
        EventType.MISSION_FEEDBACK,
        EventType.FAILURE_DETECTED,
        EventType.GOAL_DRIFT,
        EventType.RESOURCE_WARNING,
    }
)

_EXTERNAL: frozenset[EventType] = frozenset(
    {
        EventType.CONVERSATION_MESSAGE,
        EventType.CONVERSATION_STARTED,
        EventType.CONVERSATION_OBJECTIVE_UPDATED,
        EventType.TASK_CREATED,
        EventType.TASK_STARTED,
        EventType.TASK_COMPLETED,
        EventType.TASK_FAILED,
        EventType.TASK_CANCELLED,
        EventType.WORKFLOW_CREATED,
        EventType.WORKFLOW_TRIGGERED,
        EventType.WORKFLOW_STEP_STARTED,
        EventType.WORKFLOW_STEP_COMPLETED,
        EventType.WORKFLOW_COMPLETED,
        EventType.WORKFLOW_FAILED,
        EventType.WORKFLOW_PAUSED,
        EventType.WORKFLOW_RESUMED,
        EventType.PERMISSION_REQUESTED,
        EventType.PERMISSION_GRANTED,
        EventType.PERMISSION_DENIED,
        EventType.SECURITY_ESCALATION,
        EventType.SECURITY_ALERT,
        EventType.POLICY_DENIED,
        EventType.AGENT_COLLABORATION,
        EventType.AGENT_MESSAGE_RECEIVED,
        EventType.TOOL_EXECUTED,
        EventType.TOOL_DENIED,
        EventType.TOOL_FAILED,
        EventType.VOICE_SESSION_STARTED,
        EventType.VOICE_CHUNK,
        EventType.VOICE_PARTIAL_TRANSCRIPT,
        EventType.VOICE_INTERRUPTED,
        EventType.BROWSER_SESSION_UPDATED,
        EventType.DESKTOP_RUNTIME_EVENT,
        EventType.SANDBOX_EXECUTION,
        EventType.REFLECTION_COMPLETED,
    }
)


def origin_from_event(event: Event) -> SignalOrigin:
    """Classify event origin for kernel routing."""
    override = event.metadata.get("signal_origin")
    if override:
        try:
            return SignalOrigin(str(override))
        except ValueError:
            pass
    if event.type in _KERNEL_INTERNAL:
        return SignalOrigin.KERNEL_INTERNAL
    if event.type in _STABILITY_INTERNAL:
        return SignalOrigin.STABILITY_INTERNAL
    if event.type in _WATCHER_INTERNAL:
        return SignalOrigin.WATCHER_INTERNAL
    if event.type in _SYSTEM_HEALTH:
        return SignalOrigin.SYSTEM_HEALTH
    if event.type in _MEMORY_INTERNAL:
        return SignalOrigin.MEMORY_INTERNAL
    if event.type in _INTERNAL_RUNTIME:
        return SignalOrigin.INTERNAL_RUNTIME
    if event.type in _EXTERNAL:
        return SignalOrigin.EXTERNAL
    if event.type == EventType.RECOMMENDATION_CREATED:
        if event.payload.get("cognitive_eligible") or event.payload.get("requires_approval"):
            return SignalOrigin.EXTERNAL
        return SignalOrigin.WATCHER_INTERNAL
    return SignalOrigin.INTERNAL_RUNTIME


def is_kernel_eligible(origin: SignalOrigin, *, watcher_approved: bool = False) -> bool:
    """Only external and approved watcher signals enter full cognitive pipeline."""
    if origin == SignalOrigin.EXTERNAL:
        return True
    if origin == SignalOrigin.WATCHER_INTERNAL and watcher_approved:
        return True
    return False


def _priority_hint(event_type: EventType) -> float:
    high = {
        EventType.WORKFLOW_FAILED,
        EventType.SECURITY_ALERT,
        EventType.SECURITY_ESCALATION,
        EventType.PERMISSION_DENIED,
        EventType.POLICY_DENIED,
        EventType.TOOL_FAILED,
        EventType.RUNTIME_SERVICE_FAILED,
        EventType.TASK_FAILED,
    }
    medium = {
        EventType.WORKFLOW_STEP_STARTED,
        EventType.PERMISSION_REQUESTED,
        EventType.RECOMMENDATION_CREATED,
        EventType.DESKTOP_RUNTIME_EVENT,
        EventType.TASK_STARTED,
    }
    if event_type in high:
        return 0.95
    if event_type in medium:
        return 0.7
    return 0.4
