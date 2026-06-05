"""Event publish helpers — route internal vs external signals safely."""

from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event


async def publish_internal(event_bus: EventBus, event: Event) -> None:
    """Publish without kernel cognitive processing."""
    from odin_backend.core.bus.unified_bus import SignalUnificationBus

    if isinstance(event_bus, SignalUnificationBus):
        await event_bus.publish_internal(event)
    else:
        await event_bus.publish(event)


async def publish_external(event_bus: EventBus, event: Event) -> None:
    """Publish through full kernel pipeline."""
    from odin_backend.core.bus.unified_bus import SignalUnificationBus

    if isinstance(event_bus, SignalUnificationBus):
        await event_bus.publish_external(event)
    else:
        await event_bus.publish(event)


async def publish_fast_internal(event_bus: EventBus, event: Event) -> None:
    """High-priority internal path — bypasses kernel."""
    from odin_backend.core.bus.unified_bus import SignalUnificationBus

    if isinstance(event_bus, SignalUnificationBus):
        await event_bus.publish_fast_internal(event)
    else:
        await event_bus.publish(event)
