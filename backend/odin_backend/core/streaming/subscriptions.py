"""Channel subscription matching for stream routing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChannelSpec:
    """Parsed subscription channel."""

    raw: str
    kind: str  # runtime | mission | task | trace | memory
    entity_id: str | None = None

    @classmethod
    def parse(cls, channel: str) -> ChannelSpec:
        if channel == "runtime" or channel == "*":
            return cls(raw=channel, kind="runtime")
        if channel == "memory":
            return cls(raw=channel, kind="memory")
        if ":" in channel:
            kind, eid = channel.split(":", 1)
            return cls(raw=channel, kind=kind, entity_id=eid)
        return cls(raw=channel, kind=channel)


def channel_matches(subscription: ChannelSpec, target_channels: list[str]) -> bool:
    if subscription.raw in ("*", "runtime"):
        return True
    for t in target_channels:
        if t == subscription.raw:
            return True
        spec = ChannelSpec.parse(t)
        if subscription.kind == spec.kind and subscription.entity_id == spec.entity_id:
            return True
        if subscription.kind == "runtime":
            return True
    return False


@dataclass
class SubscriptionStats:
    total_connections: int = 0
    channels: dict[str, int] = field(default_factory=dict)
    events_published: int = 0
    events_delivered: int = 0
    dropped: int = 0
