"""Real-time cognitive event streaming for ODIN reasoning."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from odin_backend.core.bus.publish import publish_internal
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.trace import TraceContext
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class CognitionStream:
    """Streams ODIN's reasoning and execution progress to the event bus."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._buffer: list[dict[str, Any]] = []

    async def emit(
        self,
        message: str,
        *,
        stage: str,
        trace: TraceContext | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        entry = {
            "id": str(uuid4()),
            "message": message,
            "stage": stage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace.trace_id if trace else None,
            "workflow_id": trace.workflow_id if trace else None,
            **(payload or {}),
        }
        self._buffer.append(entry)
        if len(self._buffer) > 500:
            self._buffer = self._buffer[-500:]

        await publish_internal(
            self._event_bus,
            Event(
                type=EventType.COGNITION_PROGRESS,
                source=AgentId.ODIN,
                correlation_id=trace.correlation_id if trace else None,
                workflow_id=trace.workflow_id if trace else None,
                task_id=trace.task_id if trace else None,
                metadata={"trace_id": trace.trace_id if trace else None},
                payload=entry,
            )
        )
        logger.debug("cognition_emit", stage=stage, message=message)

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(self._buffer[-limit:]))
