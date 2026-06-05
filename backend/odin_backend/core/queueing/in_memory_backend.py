"""In-memory queue backend — backward compatible / tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.queue_models import QueueItem, QueueItemStatus


class InMemoryQueueBackend(QueueBackend):
    def __init__(self) -> None:
        self._items: dict[str, QueueItem] = {}
        self._dedup: dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._fence_counter = 0

    async def connect(self) -> None:
        return

    async def disconnect(self) -> None:
        return

    async def enqueue(self, item: QueueItem) -> QueueItem:
        async with self._lock:
            if item.dedup_key:
                existing = self._dedup.get(item.dedup_key)
                if existing:
                    cur = self._items.get(existing)
                    if cur and cur.status in (
                        QueueItemStatus.PENDING,
                        QueueItemStatus.VISIBLE,
                        QueueItemStatus.LEASED,
                    ):
                        return cur
            item.status = QueueItemStatus.VISIBLE if item.visible_at <= datetime.now(timezone.utc) else QueueItemStatus.PENDING
            self._items[item.queue_item_id] = item
            if item.dedup_key:
                self._dedup[item.dedup_key] = item.queue_item_id
            return item

    async def dequeue(
        self,
        worker_id: str,
        *,
        limit: int = 1,
        lease_seconds: float = 60.0,
    ) -> list[QueueItem]:
        now = datetime.now(timezone.utc)
        lease_until = now + timedelta(seconds=lease_seconds)
        out: list[QueueItem] = []
        async with self._lock:
            candidates = sorted(
                [
                    i
                    for i in self._items.values()
                    if i.status in (QueueItemStatus.PENDING, QueueItemStatus.VISIBLE)
                    and i.visible_at <= now
                ],
                key=lambda x: (-x.priority, x.created_at),
            )
            for item in candidates[:limit]:
                self._fence_counter += 1
                item.status = QueueItemStatus.LEASED
                item.worker_id = worker_id
                item.lease_expiry = lease_until
                item.fencing_token = self._fence_counter
                item.lease_epoch += 1
                self._items[item.queue_item_id] = item
                out.append(item.model_copy(deep=True))
        return out

    def _fence_valid(self, item: QueueItem, fencing_token: int | None) -> bool:
        if fencing_token is None:
            return True
        return item.fencing_token == fencing_token

    async def ack(self, queue_item_id: str, worker_id: str, *, fencing_token: int | None = None) -> bool:
        async with self._lock:
            item = self._items.get(queue_item_id)
            if not item or item.worker_id != worker_id:
                return False
            if not self._fence_valid(item, fencing_token):
                return False
            item.status = QueueItemStatus.ACKED
            if item.dedup_key:
                self._dedup.pop(item.dedup_key, None)
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
        async with self._lock:
            item = self._items.get(queue_item_id)
            if not item or (item.worker_id and item.worker_id != worker_id):
                return False
            if not self._fence_valid(item, fencing_token):
                return False
            item.retry_count += 1
            item.worker_id = None
            item.lease_expiry = None
            item.fencing_token = None
            item.status = QueueItemStatus.VISIBLE
            item.visible_at = datetime.now(timezone.utc) + timedelta(seconds=requeue_delay)
            item.payload["nack_reason"] = reason
            return True

    async def renew_lease(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        lease_seconds: float,
        fencing_token: int | None = None,
    ) -> bool:
        async with self._lock:
            item = self._items.get(queue_item_id)
            if not item or item.worker_id != worker_id or item.status != QueueItemStatus.LEASED:
                return False
            if not self._fence_valid(item, fencing_token):
                return False
            item.lease_expiry = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
            return True

    async def requeue_expired(self) -> int:
        now = datetime.now(timezone.utc)
        count = 0
        async with self._lock:
            for item in self._items.values():
                if item.status != QueueItemStatus.LEASED or not item.lease_expiry:
                    continue
                if item.lease_expiry <= now:
                    item.status = QueueItemStatus.VISIBLE
                    item.worker_id = None
                    item.lease_expiry = None
                    item.fencing_token = None
                    item.retry_count += 1
                    count += 1
        return count

    async def stats(self) -> dict[str, Any]:
        async with self._lock:
            by_status: dict[str, int] = {}
            for item in self._items.values():
                by_status[item.status.value] = by_status.get(item.status.value, 0) + 1
            return {"total": len(self._items), "by_status": by_status}

    async def get(self, queue_item_id: str) -> QueueItem | None:
        async with self._lock:
            item = self._items.get(queue_item_id)
            return item.model_copy(deep=True) if item else None
