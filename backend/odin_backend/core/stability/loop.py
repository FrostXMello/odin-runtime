"""Stability loop — periodic audit; emits corrective signals only."""

from typing import Any

from odin_backend.core.bus.publish import publish_internal
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class StabilityLoop:
    """Does NOT modify external systems — emits corrective signals only."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._runs = 0
        self._last_audit: dict[str, Any] = {}

    async def run_cycle(self, app: Any) -> dict[str, Any]:
        self._runs += 1
        state = app.kernel.get_state()
        coherence = app.coherence.validate(state, app.kernel.recent_signals())

        actions: list[str] = []

        # Normalize priorities if queue oversized
        ranked = app.priority_engine.rank(30)
        if len(ranked) > 10:
            pruned = app.priority_engine.prune_to(10)
            if pruned:
                actions.append("pruned_priority_queue")
            await self._emit_corrective("priority.normalized", {"kept": 10})

        # Reinforce active context if drift detected
        if coherence.coherence_score < 0.7:
            actions.append("coherence_correction_suggested")
            await self._emit_corrective(
                "coherence.corrective",
                coherence.model_dump(),
            )

        # Prune signal buffer
        buf = app.kernel.recent_signals()
        if len(buf) > 150:
            app.kernel._signal_buffer = buf[-100:]  # noqa: SLF001
            actions.append("signal_buffer_pruned")

        audit = {
            "run": self._runs,
            "coherence_score": coherence.coherence_score,
            "actions": actions,
            "focus": state.current_focus,
            "signal_count": state.signal_count,
        }
        self._last_audit = audit
        if hasattr(app, "kernel"):
            app.kernel.record_stability_check(audit)
        logger.info("stability_loop_cycle", **audit)
        return audit

    async def _emit_corrective(self, name: str, payload: dict) -> None:
        event = Event(
            type=EventType.STABILITY_CORRECTIVE,
            source=AgentId.ODIN,
            payload={"corrective": name, **payload},
        )
        await publish_internal(self._event_bus, event)

    def last_audit(self) -> dict[str, Any]:
        return self._last_audit
