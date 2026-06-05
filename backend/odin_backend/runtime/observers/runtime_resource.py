"""Runtime resource / health observer."""

from typing import Any

from odin_backend.models.perception import PerceptionRecord
from odin_backend.runtime.observers.base import BaseRuntimeObserver


class RuntimeResourceObserver(BaseRuntimeObserver):
    name = "runtime_resource"
    interval_seconds = 15.0

    def __init__(self, perception_engine: Any, app: Any) -> None:
        super().__init__(perception_engine)
        self._app = app

    async def poll(self) -> list[PerceptionRecord]:
        from odin_backend.core.perception.observers import EnvironmentObserver

        snap = self._app.perception.environment_awareness(self._app)
        return [EnvironmentObserver().observe_environment(snap)]
