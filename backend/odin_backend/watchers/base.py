"""Base watcher — emit insights and recommendations only."""

import asyncio
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Any

from odin_backend.core.bus.publish import publish_external, publish_internal
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class BaseWatcher(ABC):
    agent_id: AgentId
    name: str
    interval_seconds: int = 300
    min_emit_interval_seconds: float = 60.0

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._task: asyncio.Task | None = None
        self._running = False
        self._last_emit: dict[str, float] = {}
        self._seen_hashes: dict[str, float] = {}
        self._dedupe_window = 300.0

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("watcher_started", watcher=self.name)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        while self._running:
            try:
                insights = await self.observe()
                for insight in insights:
                    await self._emit_insight(insight)
            except Exception as exc:
                logger.exception("watcher_error", watcher=self.name, error=str(exc))
            await asyncio.sleep(self.interval_seconds)

    @abstractmethod
    async def observe(self) -> list[dict[str, Any]]:
        ...

    def _should_emit(self, key: str, payload: dict[str, Any]) -> bool:
        now = time.monotonic()
        last = self._last_emit.get(key, 0.0)
        if now - last < self.min_emit_interval_seconds:
            return False
        digest = hashlib.sha256(repr(sorted(payload.items())).encode()).hexdigest()[:16]
        seen_at = self._seen_hashes.get(digest)
        if seen_at and now - seen_at < self._dedupe_window:
            return False
        self._last_emit[key] = now
        self._seen_hashes[digest] = now
        stale = [k for k, t in self._seen_hashes.items() if now - t > self._dedupe_window * 2]
        for k in stale:
            self._seen_hashes.pop(k, None)
        return True

    async def _emit_insight(self, insight: dict[str, Any]) -> None:
        key = f"{self.name}:insight"
        if not self._should_emit(key, insight):
            return
        await publish_internal(
            self._event_bus,
            Event(
                type=EventType.WATCHER_INSIGHT,
                source=self.agent_id,
                payload={"watcher": self.name, **insight},
            ),
        )
        recommendation = insight.get("recommendation")
        if recommendation and insight.get("cognitive_eligible"):
            rec_key = f"{self.name}:recommendation"
            rec_payload = {
                "watcher": self.name,
                "recommendation": recommendation,
                "requires_approval": True,
                "cognitive_eligible": True,
            }
            if not self._should_emit(rec_key, rec_payload):
                return
            await publish_external(
                self._event_bus,
                Event(
                    type=EventType.RECOMMENDATION_CREATED,
                    source=AgentId.ODIN,
                    payload=rec_payload,
                    metadata={"cognitive_eligible": True},
                ),
            )
