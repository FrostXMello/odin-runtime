"""Redis Pub/Sub event bus implementation."""

import asyncio
import json
from collections import defaultdict
from collections.abc import Awaitable, Callable

import redis.asyncio as aioredis

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus, EventHandler
from odin_backend.models.event import Event, EventType
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RedisEventBus(EventBus):
    """Production event bus using Redis Pub/Sub."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._redis: aioredis.Redis | None = None
        self._pubsub: aioredis.client.PubSub | None = None
        self._handlers: dict[EventType | None, list[EventHandler]] = defaultdict(list)
        self._listener_task: asyncio.Task[None] | None = None
        self._running = False
        self._connected = False
        self._logged_disconnected_publish = False

    @property
    def connected(self) -> bool:
        return self._connected and self._redis is not None

    async def connect(self) -> None:
        if not self._settings.redis_enabled or self._settings.event_bus_mode.lower() == "local":
            logger.info("event_bus_running_in_local_noop_mode", backend="redis_skipped")
            return
        try:
            self._redis = aioredis.from_url(
                self._settings.redis_url,
                decode_responses=True,
            )
            await self._redis.ping()
            self._pubsub = self._redis.pubsub()
            await self._pubsub.subscribe(self._settings.redis_event_channel)
            self._running = True
            self._connected = True
            self._listener_task = asyncio.create_task(self._listen())
            logger.info("redis_event_bus_connected", channel=self._settings.redis_event_channel)
        except Exception as exc:
            self._redis = None
            self._pubsub = None
            self._running = False
            self._connected = False
            logger.warning(
                "redis_not_connected_events_will_be_dropped",
                error=str(exc),
            )

    async def disconnect(self) -> None:
        self._running = False
        self._connected = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.unsubscribe(self._settings.redis_event_channel)
            await self._pubsub.aclose()
        if self._redis:
            await self._redis.aclose()
        self._redis = None
        self._pubsub = None
        self._handlers.clear()
        logger.info("redis_event_bus_disconnected")

    async def publish(self, event: Event) -> None:
        if not self.connected:
            if not self._logged_disconnected_publish:
                logger.warning(
                    "redis_not_connected_events_will_be_dropped",
                    mode=self._settings.event_bus_mode,
                )
                self._logged_disconnected_publish = True
            await self._dispatch_local(event)
            return
        payload = json.dumps(event.to_bus_message())
        await self._redis.publish(self._settings.redis_event_channel, payload)
        await self._dispatch_local(event)

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def subscribe_all(self, handler: EventHandler) -> None:
        self._handlers[None].append(handler)

    async def _listen(self) -> None:
        assert self._pubsub is not None
        while self._running:
            try:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                if message and message.get("type") == "message":
                    data = json.loads(message["data"])
                    event = Event.model_validate(data)
                    await self._dispatch_local(event)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("redis_event_bus_listen_error", error=str(exc))
                await asyncio.sleep(1)

    async def _dispatch_local(self, event: Event) -> None:
        handlers = list(self._handlers.get(event.type, [])) + list(self._handlers.get(None, []))
        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                logger.exception(
                    "event_handler_failed",
                    event_type=event.type,
                    event_id=event.id,
                    error=str(exc),
                )
