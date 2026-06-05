"""Aggregate voice, workflows, browser, desktop, memory, vision, conversation."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from odin_backend.cognition.stream import CognitionStream
from odin_backend.core.bus.publish import publish_internal
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId


class CognitiveSource(StrEnum):
    REASONING = "reasoning"
    WORKFLOW = "workflow"
    BROWSER = "browser"
    DESKTOP = "desktop"
    VOICE = "voice"
    MEMORY = "memory"
    VISION = "vision"
    CONVERSATION = "conversation"
    CONTEXT_SHIFT = "context_shift"
    RECOMMENDATION = "recommendation"
    COLLABORATION = "collaboration"


class UnifiedCognitiveStream:
    """Unified runtime cognition timeline."""

    def __init__(self, event_bus: EventBus, cognition: CognitionStream) -> None:
        self._event_bus = event_bus
        self._cognition = cognition
        self._timeline: list[dict[str, Any]] = []
        self._max_entries = 1000

    async def ingest(
        self,
        message: str,
        *,
        source: CognitiveSource,
        stage: str = "",
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        workflow_id: str | None = None,
    ) -> dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "message": message,
            "source": source.value,
            "stage": stage or source.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            **(payload or {}),
        }
        self._timeline.append(entry)
        if len(self._timeline) > self._max_entries:
            self._timeline = self._timeline[-self._max_entries :]

        await self._cognition.emit(message, stage=f"unified.{source.value}", payload=entry)
        await publish_internal(
            self._event_bus,
            Event(
                type=EventType.COGNITIVE_STREAM_ENTRY,
                source=AgentId.ODIN,
                correlation_id=correlation_id,
                workflow_id=workflow_id,
                payload=entry,
            )
        )
        return entry

    def timeline(self, limit: int = 100, source: str | None = None) -> list[dict[str, Any]]:
        items = self._timeline
        if source:
            items = [e for e in items if e.get("source") == source]
        return list(reversed(items[-limit:]))

    def active_reasoning_paths(self) -> list[dict[str, Any]]:
        """Recent reasoning/workflow entries."""
        return [
            e
            for e in reversed(self._timeline[-50:])
            if e.get("source") in (CognitiveSource.REASONING.value, CognitiveSource.WORKFLOW.value)
        ][:10]

    async def subscribe_event(self, event: Event) -> None:
        """Bridge system events into unified stream."""
        mapping: dict[EventType, tuple[CognitiveSource, str]] = {
            EventType.COGNITION_PROGRESS: (CognitiveSource.REASONING, "progress"),
            EventType.WORKFLOW_STEP_STARTED: (CognitiveSource.WORKFLOW, "step_started"),
            EventType.WORKFLOW_COMPLETED: (CognitiveSource.WORKFLOW, "completed"),
            EventType.BROWSER_SESSION_UPDATED: (CognitiveSource.BROWSER, "session"),
            EventType.CONTEXT_ENGINE_UPDATED: (CognitiveSource.CONTEXT_SHIFT, "context"),
            EventType.VOICE_CHUNK: (CognitiveSource.VOICE, "chunk"),
            EventType.CONVERSATION_MESSAGE: (CognitiveSource.CONVERSATION, "message"),
            EventType.RECOMMENDATION_CREATED: (CognitiveSource.RECOMMENDATION, "suggestion"),
            EventType.AGENT_COLLABORATION: (CognitiveSource.COLLABORATION, "collab"),
        }
        if event.type not in mapping:
            return
        src, stage = mapping[event.type]
        msg = event.payload.get("message") or event.type.value
        await self.ingest(
            str(msg)[:500],
            source=src,
            stage=stage,
            payload=event.payload,
            correlation_id=event.correlation_id,
            workflow_id=event.workflow_id,
        )
