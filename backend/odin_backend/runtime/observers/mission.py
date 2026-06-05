"""Mission execution observer."""

from typing import Any

from odin_backend.models.perception import PerceptionRecord
from odin_backend.runtime.observers.base import BaseRuntimeObserver


class MissionExecutionObserver(BaseRuntimeObserver):
    name = "mission_execution"
    interval_seconds = 8.0

    def __init__(self, perception_engine: Any, app: Any) -> None:
        super().__init__(perception_engine)
        self._app = app

    async def poll(self) -> list[PerceptionRecord]:
        from odin_backend.core.perception.observers import StateInterpreter

        records: list[PerceptionRecord] = []
        interpreter = StateInterpreter()
        missions = await self._app.mission_manager.list_active_missions()
        for m in missions[:5]:
            failed = len([t for t in m.blocked_tasks])
            records.append(
                interpreter.interpret_mission_progress(
                    m.mission_id,
                    m.current_state.value,
                    pending=len(m.active_tasks),
                    failed=failed,
                )
            )
        return records
