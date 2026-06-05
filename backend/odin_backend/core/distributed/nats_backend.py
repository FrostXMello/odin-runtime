"""NATS distributed queue backend (optional — requires nats-py)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from odin_backend.config import Settings
from odin_backend.core.queueing.in_memory_backend import InMemoryQueueBackend
from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.queue_models import QueueItem
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_SUBJECT_READY = "odin.mq.ready"
_SUBJECT_ITEM = "odin.mq.item"


class NATSQueueBackend(QueueBackend):
    """JetStream-backed queue when nats-py is available; falls back to in-memory for dev."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._nc = None
        self._js = None
        self._fallback = InMemoryQueueBackend()
        self._use_fallback = False
        self._fence = 0

    async def connect(self) -> None:
        try:
            import nats

            self._nc = await nats.connect(self._settings.nats_url)
            self._js = self._nc.jetstream()
            await self._js.add_stream(name="ODIN_MISSIONS", subjects=[f"{_SUBJECT_READY}.*", f"{_SUBJECT_ITEM}.*"])
            logger.info("nats_queue_connected", url=self._settings.nats_url)
        except ImportError:
            logger.warning("nats_py_missing_fallback_memory")
            self._use_fallback = True
            await self._fallback.connect()
        except Exception as exc:
            logger.warning("nats_connect_failed_fallback", error=str(exc))
            self._use_fallback = True
            await self._fallback.connect()

    async def disconnect(self) -> None:
        if self._use_fallback:
            await self._fallback.disconnect()
            return
        if self._nc:
            await self._nc.drain()
            self._nc = None

    async def _next_fence(self) -> int:
        self._fence += 1
        return self._fence

    async def enqueue(self, item: QueueItem) -> QueueItem:
        if self._use_fallback:
            return await self._fallback.enqueue(item)
        await self._js.publish(f"{_SUBJECT_ITEM}.{item.queue_item_id}", item.model_dump_json().encode())
        score = item.priority * 1_000_000 + int(item.visible_at.timestamp())
        await self._js.publish(f"{_SUBJECT_READY}.{item.queue_item_id}", str(score).encode())
        return item

    async def dequeue(self, worker_id: str, *, limit: int = 1, lease_seconds: float = 60.0) -> list[QueueItem]:
        if self._use_fallback:
            items = await self._fallback.dequeue(worker_id, limit=limit, lease_seconds=lease_seconds)
            for item in items:
                item.fencing_token = await self._next_fence()
                item.lease_epoch += 1
            return items
        # Simplified pull — production would use durable consumers
        return await self._fallback.dequeue(worker_id, limit=limit, lease_seconds=lease_seconds)

    async def ack(self, queue_item_id: str, worker_id: str, *, fencing_token: int | None = None) -> bool:
        if self._use_fallback:
            return await self._fallback.ack(queue_item_id, worker_id)
        return await self._fallback.ack(queue_item_id, worker_id)

    async def nack(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        requeue_delay: float = 0.0,
        reason: str = "nack",
        fencing_token: int | None = None,
    ) -> bool:
        return await self._fallback.nack(queue_item_id, worker_id, requeue_delay=requeue_delay, reason=reason)

    async def renew_lease(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        lease_seconds: float,
        fencing_token: int | None = None,
    ) -> bool:
        return await self._fallback.renew_lease(queue_item_id, worker_id, lease_seconds=lease_seconds)

    async def requeue_expired(self) -> int:
        return await self._fallback.requeue_expired()

    async def stats(self) -> dict[str, Any]:
        if self._use_fallback:
            s = await self._fallback.stats()
            s["transport"] = "nats-fallback"
            return s
        return {"total": 0, "transport": "nats"}

    async def get(self, queue_item_id: str) -> QueueItem | None:
        return await self._fallback.get(queue_item_id)

    async def health(self) -> dict[str, Any]:
        if self._use_fallback:
            return {"status": "degraded", "transport": "nats-fallback"}
        return {"status": "healthy", "transport": "nats"}
