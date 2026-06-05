"""Bridge observability + lifecycle into streaming bus."""

from __future__ import annotations

from typing import Any

from odin_backend.core.observability.events import TraceEvent
from odin_backend.core.streaming.event_bus import StreamingEventBus
from odin_backend.core.streaming.serializers import (
    StreamEnvelope,
    StreamEventKind,
    envelope_from_trace,
)

_bridge: "StreamBridge | None" = None


class StreamBridge:
    def __init__(self, bus: StreamingEventBus) -> None:
        self.bus = bus

    def on_trace_recorded(self, event: TraceEvent) -> None:
        envelope = envelope_from_trace(event)
        self.bus.publish_nowait(envelope)

    def mission_state_changed(
        self,
        mission_id: str,
        *,
        from_state: str,
        to_state: str,
        reason: str = "",
        trace_id: str | None = None,
    ) -> None:
        envelope = StreamEnvelope(
            event_type=StreamEventKind.MISSION_STATE_CHANGED,
            channel=f"mission:{mission_id}",
            mission_id=mission_id,
            trace_id=trace_id,
            message=f"{from_state} -> {to_state}",
            payload={"from_state": from_state, "to_state": to_state, "reason": reason},
            component="lifecycle",
        )
        self.bus.publish_nowait(envelope)


def set_stream_bridge(bridge: StreamBridge | None) -> None:
    global _bridge
    _bridge = bridge


def get_stream_bridge() -> StreamBridge | None:
    return _bridge
