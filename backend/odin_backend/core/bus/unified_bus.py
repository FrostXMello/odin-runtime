"""Signal unification bus — origin isolation and recursion-safe routing."""

import asyncio
from typing import TYPE_CHECKING, Any

from odin_backend.core.bus.signals import (
    Signal,
    SignalOrigin,
    is_kernel_eligible,
    origin_from_event,
)
from odin_backend.core.runtime.recursion_guard import (
    RecursionGuard,
    RecursionGuardDecision,
)
from odin_backend.events.bus import EventBus, EventHandler
from odin_backend.models.event import Event, EventType
from odin_backend.monitoring.logging import get_logger

if TYPE_CHECKING:
    from odin_backend.core.kernel.kernel import OdinCognitiveKernel

logger = get_logger(__name__)


class SignalUnificationBus(EventBus):
    """
    Single event backbone with kernel lock, origin isolation, and recursion guard.

    Internal runtime events bypass cognitive kernel processing and publish directly
    to the inner bus. External and approved watcher signals traverse the kernel.
    """

    def __init__(self, inner: EventBus, *, max_pending: int = 500) -> None:
        self._inner = inner
        self._kernel: OdinCognitiveKernel | None = None
        self._kernel_lock = asyncio.Lock()
        self._max_pending = max_pending
        self._in_flight = 0
        self._kernel_in_flight = 0
        self._blocked_types: set[EventType] = set()
        self._kernel_enabled = True
        self._recursion_guard = RecursionGuard()
        self._total_published = 0
        self._kernel_processed = 0
        self._internal_bypassed = 0
        self._observability: Any | None = None

    def set_observability(self, hub: Any) -> None:
        self._observability = hub

    def set_kernel(self, kernel: "OdinCognitiveKernel") -> None:
        self._kernel = kernel

    def set_kernel_enabled(self, enabled: bool) -> None:
        self._kernel_enabled = enabled

    @property
    def inner(self) -> EventBus:
        return self._inner

    @property
    def in_flight(self) -> int:
        return self._in_flight

    @property
    def kernel_in_flight(self) -> int:
        return self._kernel_in_flight

    @property
    def recursion_guard(self) -> RecursionGuard:
        return self._recursion_guard

    def runtime_metrics(self) -> dict[str, Any]:
        guard = self._recursion_guard.metrics
        return {
            "recursion_events_detected": guard.recursion_events_detected,
            "suppressed_signal_count": guard.suppressed_signal_count,
            "runtime_loop_health": guard.runtime_loop_health,
            "active_signal_chains": guard.active_signal_chains,
            "kernel_processing_rate": guard.kernel_processing_rate,
            "total_published": self._total_published,
            "kernel_processed": self._kernel_processed,
            "internal_bypassed": self._internal_bypassed,
            "in_flight": self._in_flight,
            "kernel_in_flight": self._kernel_in_flight,
            "suppressed_loops": guard.suppressed_loops,
            "active_chains": guard.active_chains,
        }

    def block_event_type(self, event_type: EventType) -> None:
        self._blocked_types.add(event_type)

    def unblock_event_type(self, event_type: EventType) -> None:
        self._blocked_types.discard(event_type)

    async def connect(self) -> None:
        await self._inner.connect()

    async def disconnect(self) -> None:
        await self._inner.disconnect()

    async def _safe_inner_publish(self, event: Event) -> None:
        """Never crash routing when inner bus (e.g. Redis) is unavailable."""
        try:
            await self._inner.publish(event)
        except RuntimeError as exc:
            if "not connected" in str(exc).lower():
                if not getattr(self, "_logged_inner_disconnected", False):
                    logger.warning(
                        "inner_event_bus_not_connected_events_dropped",
                        inner=type(self._inner).__name__,
                    )
                    self._logged_inner_disconnected = True
                return
            raise

    async def publish(self, event: Event) -> None:
        """Auto-classify origin and route."""
        await self._route(event, origin=None, fast=False)

    async def publish_external(self, event: Event) -> None:
        """Force external origin — full cognitive pipeline."""
        meta = dict(event.metadata)
        meta["signal_origin"] = SignalOrigin.EXTERNAL.value
        await self._route(event.model_copy(update={"metadata": meta}), origin=SignalOrigin.EXTERNAL, fast=False)

    async def publish_internal(self, event: Event) -> None:
        """Bypass kernel — inner bus only."""
        await self._route(event, origin=None, fast=False, force_bypass=True)

    async def publish_fast(self, event: Event) -> None:
        """High-priority external-eligible path."""
        await self._route(event, origin=None, fast=True)

    async def publish_fast_internal(self, event: Event) -> None:
        """High-priority internal bypass."""
        await self._route(event, origin=None, fast=True, force_bypass=True)

    async def _route(
        self,
        event: Event,
        *,
        origin: SignalOrigin | None,
        fast: bool,
        force_bypass: bool = False,
    ) -> None:
        if event.type in self._blocked_types:
            return
        if self._in_flight >= self._max_pending:
            logger.warning("signal_backpressure", in_flight=self._in_flight)
            return

        signal = Signal.from_event(event)
        if origin is not None:
            signal = signal.model_copy(update={"origin": origin})

        resolved_origin = signal.origin
        watcher_approved = bool(
            event.payload.get("cognitive_eligible")
            or event.metadata.get("cognitive_eligible")
        )
        eligible = is_kernel_eligible(resolved_origin, watcher_approved=watcher_approved)
        bypass = force_bypass or not eligible

        if fast and not bypass and signal.priority < 80:
            signal = signal.model_copy(update={"priority": 80})

        self._total_published += 1
        self._in_flight += 1
        t_route = __import__("time").monotonic()
        try:
            if bypass:
                self._internal_bypassed += 1
                await self._safe_inner_publish(event)
                self._record_signal(
                    signal,
                    suppressed=False,
                    bypass=True,
                    latency_ms=(__import__("time").monotonic() - t_route) * 1000,
                )
                return

            guard_result = self._recursion_guard.evaluate(signal, eligible_for_kernel=True)
            if guard_result.decision == RecursionGuardDecision.SUPPRESS:
                self._record_signal(signal, suppressed=True, latency_ms=(__import__("time").monotonic() - t_route) * 1000)
                return
            if guard_result.decision == RecursionGuardDecision.ESCALATE:
                logger.error(
                    "recursive_signal_escalation",
                    chain_key=guard_result.chain_key,
                    trace=guard_result.trace[-5:],
                )
                return

            await self._process_through_kernel(signal)
            self._kernel_processed += 1
            self._recursion_guard.record_kernel_processed()
            await self._safe_inner_publish(event)
            self._record_signal(
                signal,
                suppressed=False,
                bypass=bypass,
                latency_ms=(__import__("time").monotonic() - t_route) * 1000,
            )
        finally:
            self._in_flight = max(0, self._in_flight - 1)

    def _record_signal(
        self,
        signal: Any,
        *,
        suppressed: bool = False,
        bypass: bool = False,
        latency_ms: float = 0.0,
    ) -> None:
        if not self._observability:
            return
        from odin_backend.core.observability.events import TraceEventKind

        sid = getattr(signal, "id", None) or getattr(signal, "name", str(signal.type))
        dest = "kernel" if not bypass else "inner_bus"
        self._observability.signal_graph.record_signal(
            signal_id=str(sid),
            signal_type=str(getattr(signal, "type", signal.name)),
            source=str(signal.source),
            destination=dest,
            suppressed=suppressed,
            metadata={"origin": signal.origin.value if hasattr(signal, "origin") else ""},
            latency_ms=latency_ms,
        )
        kind = TraceEventKind.SIGNAL_SUPPRESSED if suppressed else TraceEventKind.SIGNAL_PROPAGATED
        self._observability.tracer.record(
            kind,
            message=str(signal.name),
            payload={"destination": dest, "origin": getattr(signal.origin, "value", "")},
            component="signal_bus",
        )
        self._observability.metrics.record_signal_latency(latency_ms)

    async def _process_through_kernel(self, signal: Signal) -> None:
        if not self._kernel or not self._kernel_enabled:
            return
        self._recursion_guard.enter_kernel(signal)
        self._kernel_in_flight += 1
        try:
            async with self._kernel_lock:
                try:
                    await self._kernel.process_signal(signal)
                except Exception as exc:
                    logger.warning("kernel_signal_processing_failed", error=str(exc))
        finally:
            self._recursion_guard.exit_kernel()
            self._kernel_in_flight = max(0, self._kernel_in_flight - 1)

    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        await self._inner.subscribe(event_type, handler)

    async def subscribe_all(self, handler: EventHandler) -> None:
        await self._inner.subscribe_all(handler)


def mark_external(event: Event) -> Event:
    """Tag event metadata for external cognitive processing."""
    meta = dict(event.metadata)
    meta["signal_origin"] = SignalOrigin.EXTERNAL.value
    return event.model_copy(update={"metadata": meta})
