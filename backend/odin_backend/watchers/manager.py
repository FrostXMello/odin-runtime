"""Watcher manager — background monitoring loops."""

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.monitoring.audit import AuditLogger
from odin_backend.watchers.fafnir_watcher import FafnirWatcher
from odin_backend.watchers.heimdall_watcher import HeimdallWatcher
from odin_backend.watchers.hugin_watcher import HuginWatcher
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WatcherManager:
    def __init__(self, settings: Settings, event_bus: EventBus, audit: AuditLogger) -> None:
        self._watchers = [
            HuginWatcher(event_bus, settings.watcher_hugin_interval_seconds),
            FafnirWatcher(event_bus, settings.watcher_fafnir_interval_seconds),
            HeimdallWatcher(event_bus, audit, settings.watcher_heimdall_interval_seconds),
        ]

    async def start_all(self) -> None:
        for w in self._watchers:
            await w.start()
        logger.info("watchers_started", count=len(self._watchers))

    async def stop_all(self) -> None:
        for w in self._watchers:
            await w.stop()
