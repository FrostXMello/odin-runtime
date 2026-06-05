"""Global async event broadcaster with per-channel fan-out."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from odin_backend.core.streaming.serializers import StreamEnvelope, resolve_channels_for_envelope
from odin_backend.core.streaming.subscriptions import ChannelSpec, channel_matches, SubscriptionStats
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

MAX_QUEUE = 512


class StreamingEventBus:
    """In-process pub/sub — local-first, no Redis."""

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[StreamEnvelope | None]]] = defaultdict(list)
        self._lock = asyncio.Lock()
        self.stats = SubscriptionStats()

    async def subscribe(self, channel: str) -> asyncio.Queue[StreamEnvelope | None]:
        q: asyncio.Queue[StreamEnvelope | None] = asyncio.Queue(maxsize=MAX_QUEUE)
        async with self._lock:
            self._queues[channel].append(q)
            self.stats.total_connections = sum(len(v) for v in self._queues.values())
            self.stats.channels[channel] = len(self._queues[channel])
        logger.info("stream_subscribed", channel=channel)
        return q

    async def unsubscribe(self, channel: str, queue: asyncio.Queue[StreamEnvelope | None]) -> None:
        async with self._lock:
            subs = self._queues.get(channel, [])
            if queue in subs:
                subs.remove(queue)
            self.stats.total_connections = sum(len(v) for v in self._queues.values())

    async def publish(self, envelope: StreamEnvelope) -> int:
        targets = resolve_channels_for_envelope(envelope)
        delivered = 0
        async with self._lock:
            snapshot = dict(self._queues)
        for sub_channel, queues in snapshot.items():
            spec = ChannelSpec.parse(sub_channel)
            if not channel_matches(spec, targets):
                continue
            for q in queues:
                try:
                    q.put_nowait(envelope)
                    delivered += 1
                except asyncio.QueueFull:
                    self.stats.dropped += 1
        self.stats.events_published += 1
        self.stats.events_delivered += delivered
        return delivered

    def publish_nowait(self, envelope: StreamEnvelope) -> None:
        """Schedule publish on the running event loop (safe from sync code)."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(envelope))
        except RuntimeError:
            logger.debug("stream_publish_skipped_no_loop", event_type=envelope.event_type)

    async def publish_dict(self, event_type: str, *, channel: str = "runtime", **fields: Any) -> None:
        from odin_backend.core.streaming.serializers import StreamEventKind

        try:
            kind = StreamEventKind(event_type)
        except ValueError:
            return
        payload = fields.pop("payload", {}) or {}
        envelope = StreamEnvelope(
            event_type=kind,
            channel=channel,
            message=fields.pop("message", ""),
            component=fields.pop("component", "runtime"),
            mission_id=fields.pop("mission_id", None),
            task_id=fields.pop("task_id", None),
            trace_id=fields.pop("trace_id", None),
            causal_chain_id=fields.pop("causal_chain_id", None),
            payload={**payload, **fields},
        )
        await self.publish(envelope)
