"""WebSocket connection lifecycle and message pump."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from odin_backend.core.streaming.event_bus import StreamingEventBus
from odin_backend.core.streaming.serializers import StreamEnvelope, StreamEventKind
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    def __init__(self, bus: StreamingEventBus) -> None:
        self._bus = bus

    async def handle(
        self,
        websocket: WebSocket,
        channel: str,
        *,
        replay_recent: list[StreamEnvelope] | None = None,
    ) -> None:
        await websocket.accept()
        queue = await self._bus.subscribe(channel)
        try:
            connected = StreamEnvelope(
                event_type=StreamEventKind.CONNECTED,
                channel=channel,
                message="subscribed",
                payload={"channel": channel},
            )
            await websocket.send_text(connected.model_dump_json())

            if replay_recent:
                for env in replay_recent[-30:]:
                    await websocket.send_text(env.model_dump_json())

            pump = asyncio.create_task(self._pump_out(websocket, queue))
            try:
                while True:
                    raw = await websocket.receive_text()
                    if raw.strip().lower() in ("ping", '{"type":"ping"}'):
                        pong = StreamEnvelope(
                            event_type=StreamEventKind.HEARTBEAT,
                            channel=channel,
                            message="pong",
                        )
                        await websocket.send_text(pong.model_dump_json())
            except WebSocketDisconnect:
                pass
            finally:
                pump.cancel()
                try:
                    await pump
                except asyncio.CancelledError:
                    pass
        finally:
            await self._bus.unsubscribe(channel, queue)

    async def _pump_out(
        self,
        websocket: WebSocket,
        queue: asyncio.Queue[StreamEnvelope | None],
    ) -> None:
        while True:
            envelope = await queue.get()
            if envelope is None:
                break
            await websocket.send_text(envelope.model_dump_json())
