"""Queue transport factory — sqlite | redis | nats | memory."""

from __future__ import annotations

from odin_backend.config import Settings
from odin_backend.core.queueing.in_memory_backend import InMemoryQueueBackend
from odin_backend.core.queueing.queue_backend import QueueBackend
from odin_backend.core.queueing.sqlite_backend import SQLiteQueueBackend
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


def create_queue_backend(settings: Settings) -> QueueBackend:
    backend_type = (settings.queue_backend or "sqlite").lower()

    if not settings.queue_persist_enabled:
        logger.info("queue_backend_selected", backend="memory")
        return InMemoryQueueBackend()

    if backend_type == "memory":
        logger.info("queue_backend_selected", backend="memory")
        return InMemoryQueueBackend()

    if backend_type == "redis":
        from odin_backend.core.distributed.redis_backend import RedisQueueBackend

        logger.info("queue_backend_selected", backend="redis")
        return RedisQueueBackend(settings)

    if backend_type == "nats":
        from odin_backend.core.distributed.nats_backend import NATSQueueBackend

        logger.info("queue_backend_selected", backend="nats")
        return NATSQueueBackend(settings)

    logger.info("queue_backend_selected", backend="sqlite")
    return SQLiteQueueBackend(settings)
