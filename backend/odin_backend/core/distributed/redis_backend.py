"""Redis distributed queue backend."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import redis.asyncio as aioredis

from odin_backend.config import Settings
from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.queue_models import QueueItem, QueueItemStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_READY_KEY = "odin:mq:ready"
_ITEM_PREFIX = "odin:mq:item:"
_DEDUP_PREFIX = "odin:mq:dedup:"
_LEASE_PREFIX = "odin:mq:lease:"
_FENCE_KEY = "odin:mq:fence:counter"


class RedisQueueBackend(QueueBackend):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._redis: aioredis.Redis | None = None
        self._max_retries = settings.queue_max_retries
        self._ready_key = settings.redis_mission_queue_key or _READY_KEY

    async def connect(self) -> None:
        self._redis = aioredis.from_url(self._settings.redis_url, decode_responses=True)
        await self._redis.ping()
        logger.info("redis_queue_connected", url=self._settings.redis_url)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def _r(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("RedisQueueBackend not connected")
        return self._redis

    async def _next_fence(self) -> int:
        return int(await self._r().incr(_FENCE_KEY))

    def _item_key(self, qid: str) -> str:
        return f"{_ITEM_PREFIX}{qid}"

    async def _save_item(self, item: QueueItem) -> None:
        await self._r().set(self._item_key(item.queue_item_id), item.model_dump_json())

    async def _load_item(self, qid: str) -> QueueItem | None:
        raw = await self._r().get(self._item_key(qid))
        if not raw:
            return None
        return QueueItem.model_validate_json(raw)

    async def enqueue(self, item: QueueItem) -> QueueItem:
        r = self._r()
        if item.dedup_key:
            existing = await r.get(f"{_DEDUP_PREFIX}{item.dedup_key}")
            if existing:
                loaded = await self._load_item(existing)
                if loaded and loaded.status in (
                    QueueItemStatus.PENDING,
                    QueueItemStatus.VISIBLE,
                    QueueItemStatus.LEASED,
                ):
                    return loaded

        now = datetime.now(timezone.utc)
        if item.visible_at <= now:
            item.status = QueueItemStatus.VISIBLE
        else:
            item.status = QueueItemStatus.PENDING

        await self._save_item(item)
        if item.dedup_key:
            await r.set(f"{_DEDUP_PREFIX}{item.dedup_key}", item.queue_item_id)

        score = item.priority * 1_000_000_000_000 + int(item.visible_at.timestamp() * 1000)
        await r.zadd(self._ready_key, {item.queue_item_id: score})
        return item

    async def dequeue(
        self,
        worker_id: str,
        *,
        limit: int = 1,
        lease_seconds: float = 60.0,
    ) -> list[QueueItem]:
        r = self._r()
        now = datetime.now(timezone.utc)
        now_ms = int(now.timestamp() * 1000)
        out: list[QueueItem] = []

        candidates = await r.zrangebyscore(self._ready_key, "-inf", now_ms, start=0, num=limit * 3)
        for qid in candidates:
            if len(out) >= limit:
                break
            item = await self._load_item(qid)
            if not item or item.status not in (QueueItemStatus.PENDING, QueueItemStatus.VISIBLE):
                await r.zrem(self._ready_key, qid)
                continue
            if item.visible_at > now:
                continue

            removed = await r.zrem(self._ready_key, qid)
            if not removed:
                continue

            fence = await self._next_fence()
            item.status = QueueItemStatus.LEASED
            item.worker_id = worker_id
            item.fencing_token = fence
            item.lease_epoch = item.lease_epoch + 1
            item.lease_expiry = now + timedelta(seconds=lease_seconds)
            await self._save_item(item)
            await r.setex(
                f"{_LEASE_PREFIX}{qid}",
                int(lease_seconds) + 5,
                json.dumps({"worker_id": worker_id, "fence": fence, "epoch": item.lease_epoch}),
            )
            out.append(item.model_copy(deep=True))
        return out

    async def _validate_lease(self, queue_item_id: str, worker_id: str, fence: int | None = None) -> bool:
        item = await self._load_item(queue_item_id)
        if not item or item.worker_id != worker_id:
            return False
        if fence is not None and item.fencing_token != fence:
            return False
        return item.status == QueueItemStatus.LEASED

    async def ack(self, queue_item_id: str, worker_id: str, *, fencing_token: int | None = None) -> bool:
        item = await self._load_item(queue_item_id)
        if not item or not await self._validate_lease(queue_item_id, worker_id, fence=fencing_token or item.fencing_token):
            return False
        item.status = QueueItemStatus.ACKED
        await self._save_item(item)
        if item.dedup_key:
            await self._r().delete(f"{_DEDUP_PREFIX}{item.dedup_key}")
        await self._r().delete(f"{_LEASE_PREFIX}{queue_item_id}")
        return True

    async def nack(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        requeue_delay: float = 0.0,
        reason: str = "nack",
        fencing_token: int | None = None,
    ) -> bool:
        item = await self._load_item(queue_item_id)
        if not item:
            return False
        fence = fencing_token if fencing_token is not None else item.fencing_token
        if not await self._validate_lease(queue_item_id, worker_id, fence=fence):
            return False

        item.retry_count += 1
        if item.retry_count >= self._max_retries:
            item.status = QueueItemStatus.DEADLETTER
            await self._save_item(item)
            await self._r().delete(f"{_LEASE_PREFIX}{queue_item_id}")
            return False

        visible = datetime.now(timezone.utc) + timedelta(seconds=requeue_delay)
        item.status = QueueItemStatus.VISIBLE
        item.worker_id = None
        item.lease_expiry = None
        item.visible_at = visible
        item.payload["nack_reason"] = reason
        await self._save_item(item)
        await self._r().delete(f"{_LEASE_PREFIX}{queue_item_id}")
        score = item.priority * 1_000_000_000_000 + int(visible.timestamp() * 1000)
        await self._r().zadd(self._ready_key, {queue_item_id: score})
        return True

    async def renew_lease(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        lease_seconds: float,
        fencing_token: int | None = None,
    ) -> bool:
        item = await self._load_item(queue_item_id)
        if not item:
            return False
        fence = fencing_token if fencing_token is not None else item.fencing_token
        if not await self._validate_lease(queue_item_id, worker_id, fence=fence):
            return False
        item.lease_expiry = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
        await self._save_item(item)
        await self._r().setex(
            f"{_LEASE_PREFIX}{queue_item_id}",
            int(lease_seconds) + 5,
            json.dumps({"worker_id": worker_id, "fence": item.fencing_token, "epoch": item.lease_epoch}),
        )
        return True

    async def requeue_expired(self) -> int:
        r = self._r()
        count = 0
        now = datetime.now(timezone.utc)
        async for key in r.scan_iter(match=f"{_LEASE_PREFIX}*"):
            qid = key.replace(_LEASE_PREFIX, "")
            item = await self._load_item(qid)
            if not item or item.status != QueueItemStatus.LEASED:
                await r.delete(key)
                continue
            if item.lease_expiry and item.lease_expiry <= now:
                item.status = QueueItemStatus.VISIBLE
                item.worker_id = None
                item.lease_expiry = None
                item.retry_count += 1
                await self._save_item(item)
                await r.delete(key)
                score = item.priority * 1_000_000_000_000 + int(now.timestamp() * 1000)
                await r.zadd(self._ready_key, {qid: score})
                count += 1
        return count

    async def stats(self) -> dict[str, Any]:
        r = self._r()
        depth = await r.zcard(self._ready_key)
        return {"total": depth, "by_status": {"ready": depth}, "transport": "redis"}

    async def get(self, queue_item_id: str) -> QueueItem | None:
        return await self._load_item(queue_item_id)

    async def health(self) -> dict[str, Any]:
        try:
            await self._r().ping()
            return {"status": "healthy", "transport": "redis"}
        except Exception as exc:
            return {"status": "degraded", "transport": "redis", "error": str(exc)}
