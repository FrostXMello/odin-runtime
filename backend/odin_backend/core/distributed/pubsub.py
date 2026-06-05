"""Distributed pub/sub for cross-worker events."""

from __future__ import annotations

import json
from typing import Any, Callable, Awaitable

from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class DistributedPubSub:
    """Redis-backed event fanout for worker ↔ control plane."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._redis = None
        self._channel = settings.redis_pubsub_channel

    async def connect(self) -> None:
        if self._settings.queue_backend != "redis":
            return
        import redis.asyncio as aioredis

        self._redis = aioredis.from_url(self._settings.redis_url, decode_responses=True)
        await self._redis.ping()

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if not self._redis:
            return
        msg = json.dumps({"event_type": event_type, "payload": payload})
        await self._redis.publish(self._channel, msg)

    async def subscribe(self, handler: Callable[[str, dict[str, Any]], Awaitable[None]]) -> None:
        if not self._redis:
            return
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._channel)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                data = json.loads(message["data"])
                await handler(data.get("event_type", ""), data.get("payload") or {})
            except Exception as exc:
                logger.warning("pubsub_handler_error", error=str(exc))
