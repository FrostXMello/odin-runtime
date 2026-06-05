"""Shared Redis client for queues and caching."""

import json
from typing import Any

import redis.asyncio as aioredis

from odin_backend.config import Settings
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RedisClient:
    """Low-level Redis operations for task queue and state."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._redis: aioredis.Redis | None = None

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis client not connected")
        return self._redis

    async def connect(self) -> None:
        self._redis = aioredis.from_url(self._settings.redis_url, decode_responses=True)
        await self._redis.ping()
        logger.info("redis_client_connected", url=self._settings.redis_url)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    async def enqueue_task(self, task_id: str, priority: int = 0) -> None:
        """Push task id to priority queue (lower score = higher priority)."""
        await self.redis.zadd(self._settings.redis_task_queue, {task_id: priority})

    async def dequeue_task(self) -> str | None:
        """Pop highest-priority task id."""
        result = await self.redis.zpopmin(self._settings.redis_task_queue, count=1)
        if not result:
            return None
        task_id, _ = result[0]
        return task_id

    async def store_task(self, task_id: str, data: dict[str, Any]) -> None:
        key = f"odin:task:{task_id}"
        await self.redis.set(key, json.dumps(data))

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        key = f"odin:task:{task_id}"
        raw = await self.redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def delete_task(self, task_id: str) -> None:
        await self.redis.delete(f"odin:task:{task_id}")

    async def set_agent_heartbeat(self, agent_id: str, payload: dict[str, Any]) -> None:
        key = f"odin:agent:heartbeat:{agent_id}"
        await self.redis.setex(key, 60, json.dumps(payload))
