"""Runtime observer manager."""

from typing import Any

from odin_backend.runtime.observers.filesystem import FilesystemObserver
from odin_backend.runtime.observers.mission import MissionExecutionObserver
from odin_backend.runtime.observers.runtime_resource import RuntimeResourceObserver
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RuntimeObserverManager:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._observers = [
            FilesystemObserver(app.perception),
            RuntimeResourceObserver(app.perception, app),
            MissionExecutionObserver(app.perception, app),
        ]

    async def start_all(self) -> None:
        if not self._app.settings.runtime_observers_enabled:
            return
        for obs in self._observers:
            await obs.start()
        logger.info("runtime_observers_started", count=len(self._observers))

    async def stop_all(self) -> None:
        for obs in self._observers:
            await obs.stop()
