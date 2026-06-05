"""Stream heartbeat and periodic health broadcasts."""

from __future__ import annotations

import asyncio
from typing import Any

from odin_backend.core.streaming.serializers import StreamEnvelope, StreamEventKind
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class StreamHeartbeat:
    def __init__(self, bus: Any, *, interval_seconds: float = 15.0) -> None:
        self._bus = bus
        self._interval = interval_seconds
        self._task: asyncio.Task | None = None
        self._app: Any | None = None

    async def start(self, app: Any) -> None:
        if self._task:
            return
        self._app = app
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._interval)
                await self._emit_heartbeat()
                if self._app:
                    await self._emit_health()
                    await self._emit_bottlenecks()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning("stream_heartbeat_error", error=str(exc))

    async def _emit_heartbeat(self) -> None:
        envelope = StreamEnvelope(
            event_type=StreamEventKind.HEARTBEAT,
            channel="runtime",
            message="ping",
            payload={"connections": self._bus.stats.total_connections},
        )
        await self._bus.publish(envelope)

    async def _emit_health(self) -> None:
        from odin_backend.core.missions.health import assess_orchestration_health

        orch = assess_orchestration_health(self._app)
        envelope = StreamEnvelope(
            event_type=StreamEventKind.HEALTH_CHANGED,
            channel="runtime",
            message=f"orchestration {orch.status}",
            payload=orch.model_dump(),
        )
        await self._bus.publish(envelope)

    async def _emit_bottlenecks(self) -> None:
        from odin_backend.core.observability.introspection import detect_bottlenecks

        bottlenecks = detect_bottlenecks(self._app)
        for b in bottlenecks[:5]:
            envelope = StreamEnvelope(
                event_type=StreamEventKind.BOTTLENECK_DETECTED,
                channel="runtime",
                mission_id=b.mission_id,
                message=b.reason,
                payload=b.model_dump(),
            )
            await self._bus.publish(envelope)
