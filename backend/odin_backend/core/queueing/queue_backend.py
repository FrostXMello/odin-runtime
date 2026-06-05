"""Abstract persistent queue backend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from odin_backend.core.queueing.queue_models import QueueItem


class QueueBackend(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def enqueue(self, item: QueueItem) -> QueueItem:
        """Insert item; suppress duplicate when dedup_key matches active item."""

    @abstractmethod
    async def dequeue(
        self,
        worker_id: str,
        *,
        limit: int = 1,
        lease_seconds: float = 60.0,
    ) -> list[QueueItem]:
        """Claim visible items with lease."""

    @abstractmethod
    async def ack(self, queue_item_id: str, worker_id: str, *, fencing_token: int | None = None) -> bool: ...

    @abstractmethod
    async def nack(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        requeue_delay: float = 0.0,
        reason: str = "nack",
        fencing_token: int | None = None,
    ) -> bool: ...

    @abstractmethod
    async def renew_lease(
        self,
        queue_item_id: str,
        worker_id: str,
        *,
        lease_seconds: float,
        fencing_token: int | None = None,
    ) -> bool: ...

    @abstractmethod
    async def requeue_expired(self) -> int: ...

    @abstractmethod
    async def stats(self) -> dict[str, Any]: ...

    @abstractmethod
    async def get(self, queue_item_id: str) -> QueueItem | None: ...
