"""Perception engine — central perception ingestion and emission."""

from typing import Any

from odin_backend.core.bus.publish import publish_internal
from odin_backend.core.perception.bridge import PerceptionMemoryBridge
from odin_backend.core.perception.observers import (
    EnvironmentObserver,
    ExecutionObserver,
    StateInterpreter,
)
from odin_backend.models.event import Event, EventType
from odin_backend.models.perception import PerceptionCategory, PerceptionRecord
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_CATEGORY_TO_EVENT: dict[PerceptionCategory, EventType] = {
    PerceptionCategory.PERCEPTION_EVENT: EventType.PERCEPTION_EVENT,
    PerceptionCategory.EXECUTION_RESULT: EventType.EXECUTION_RESULT,
    PerceptionCategory.ENVIRONMENT_CHANGE: EventType.ENVIRONMENT_CHANGE,
    PerceptionCategory.MISSION_FEEDBACK: EventType.MISSION_FEEDBACK,
    PerceptionCategory.FAILURE_DETECTED: EventType.FAILURE_DETECTED,
    PerceptionCategory.GOAL_DRIFT: EventType.GOAL_DRIFT,
    PerceptionCategory.RESOURCE_WARNING: EventType.RESOURCE_WARNING,
}


class PerceptionEngine:
    def __init__(
        self,
        event_bus: Any,
        memory_bridge: PerceptionMemoryBridge,
    ) -> None:
        self._bus = event_bus
        self._bridge = memory_bridge
        self._execution = ExecutionObserver()
        self._environment = EnvironmentObserver()
        self._interpreter = StateInterpreter()
        self._live: list[PerceptionRecord] = []
        self._max_live = 200

    @property
    def live_perceptions(self) -> list[PerceptionRecord]:
        return list(self._live[-50:])

    async def ingest(self, record: PerceptionRecord) -> PerceptionRecord:
        await self._bridge.ingest(record)
        self._live.append(record)
        if len(self._live) > self._max_live:
            self._live = self._live[-self._max_live :]
        await self._emit_event(record)
        return record

    async def ingest_execution(
        self,
        *,
        tool: str,
        success: bool,
        mission_id: str | None = None,
        task_id: str | None = None,
        output: dict | None = None,
    ) -> PerceptionRecord:
        record = self._execution.observe_execution(
            tool=tool,
            success=success,
            mission_id=mission_id,
            task_id=task_id,
            output=output,
        )
        return await self.ingest(record)

    async def ingest_environment(self, snapshot: dict[str, Any]) -> PerceptionRecord:
        record = self._environment.observe_environment(snapshot)
        return await self.ingest(record)

    async def ingest_mission_feedback(
        self,
        mission_id: str,
        state: str,
        *,
        pending: int = 0,
        failed: int = 0,
    ) -> PerceptionRecord:
        record = self._interpreter.interpret_mission_progress(
            mission_id, state, pending=pending, failed=failed
        )
        return await self.ingest(record)

    async def _emit_event(self, record: PerceptionRecord) -> None:
        event_type = _CATEGORY_TO_EVENT.get(record.category, EventType.PERCEPTION_EVENT)
        await publish_internal(
            self._bus,
            Event(
                type=event_type,
                source=AgentId.ODIN,
                workflow_id=record.mission_id,
                task_id=record.task_id,
                payload=record.model_dump(mode="json"),
            ),
        )

    def environment_awareness(self, app: Any) -> dict[str, Any]:
        state = app.kernel.get_state()
        return {
            "system_health": state.system_health,
            "runtime_loop_health": state.runtime_loop_health,
            "active_missions": len(state.active_missions),
            "live_perception_count": len(self._live),
        }
