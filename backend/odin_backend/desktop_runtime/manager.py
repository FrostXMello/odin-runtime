"""DesktopRuntimeManager — live desktop state ingestion."""

from typing import Any

from odin_backend.config import Settings
from odin_backend.context_engine.engine import ContextEngine
from odin_backend.desktop_runtime.events import DesktopContextEvent, DesktopEventType
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class DesktopRuntimeManager:
    """Collects, normalizes, and publishes live desktop context."""

    def __init__(
        self,
        settings: Settings,
        event_bus: EventBus,
        context_engine: ContextEngine,
    ) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._context_engine = context_engine
        self._enabled = settings.desktop_collector_enabled
        self._last_state: dict[str, Any] = {}
        self._event_log: list[DesktopContextEvent] = []

    @property
    def enabled(self) -> bool:
        return self._enabled and self._settings.context_awareness_enabled

    async def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if enabled:
            await self._context_engine.set_enabled(True)

    def get_state(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "last_state": self._last_state,
            "recent_events": [e.model_dump(mode="json") for e in self._event_log[-20:]],
            "explainable": self.explain_sources(),
        }

    def explain_sources(self) -> dict[str, Any]:
        collectors = {e.collector for e in self._event_log[-50:]}
        return {
            "collectors_active": list(collectors) or ["none"],
            "opt_in": self.enabled,
            "disableable": True,
            "event_count": len(self._event_log),
        }

    async def ingest_snapshot(self, snapshot: dict[str, Any], *, collector: str = "electron_bridge") -> dict[str, Any]:
        """Ingest full desktop snapshot from Electron context bridge."""
        if not self.enabled:
            return {"accepted": False, "reason": "Desktop collector disabled (opt-in)"}

        self._last_state = snapshot
        explain = {
            "collector": collector,
            "captured_fields": list(snapshot.keys()),
            "transparent": True,
        }

        # Normalize and emit granular events
        if snapshot.get("active_window"):
            await self._emit_event(
                DesktopEventType.WINDOW_FOCUSED,
                snapshot["active_window"],
                collector=collector,
                explain=explain,
            )

        if snapshot.get("vscode"):
            await self._emit_event(
                DesktopEventType.VSCODE_WORKSPACE,
                snapshot["vscode"],
                collector=collector,
                explain=explain,
            )

        if snapshot.get("browser_tabs"):
            await self._emit_event(
                DesktopEventType.BROWSER_CONTEXT,
                {"tabs": snapshot["browser_tabs"]},
                collector=collector,
                explain=explain,
            )

        if snapshot.get("terminals"):
            await self._emit_event(
                DesktopEventType.TERMINAL_UPDATED,
                {"sessions": snapshot["terminals"]},
                collector=collector,
                explain=explain,
            )

        if snapshot.get("clipboard_preview"):
            await self._emit_event(
                DesktopEventType.CLIPBOARD_CHANGED,
                {"preview": snapshot["clipboard_preview"][:200]},
                collector=collector,
                explain=explain,
            )

        # Update context engine
        await self._context_engine.update_environment(
            application=snapshot.get("active_app"),
            window=snapshot.get("active_window", {}).get("title") if isinstance(snapshot.get("active_window"), dict) else None,
            tabs=snapshot.get("browser_tabs"),
            terminal_cwd=(snapshot.get("terminals") or [{}])[0].get("cwd") if snapshot.get("terminals") else None,
            terminal_output=(snapshot.get("terminals") or [{}])[0].get("output_preview") if snapshot.get("terminals") else None,
            repository=snapshot.get("vscode", {}).get("workspace") if isinstance(snapshot.get("vscode"), dict) else None,
            project=snapshot.get("project", "PROJECT_ODIN"),
        )

        return {"accepted": True, "explainable": explain}

    async def ingest_event(
        self,
        event_type: DesktopEventType,
        payload: dict[str, Any],
        *,
        collector: str = "api_ingest",
    ) -> DesktopContextEvent:
        return await self._emit_event(event_type, payload, collector=collector)

    async def _emit_event(
        self,
        event_type: DesktopEventType,
        payload: dict[str, Any],
        *,
        collector: str,
        explain: dict[str, Any] | None = None,
    ) -> DesktopContextEvent:
        evt = DesktopContextEvent(
            event_type=event_type,
            collector=collector,
            payload=payload,
            explainable=explain or {"collector": collector},
        )
        self._event_log.append(evt)
        if len(self._event_log) > 500:
            self._event_log = self._event_log[-500:]

        await self._event_bus.publish(
            Event(
                type=EventType.DESKTOP_RUNTIME_EVENT,
                source=AgentId.ODIN,
                payload={
                    "event_type": event_type.value,
                    **evt.model_dump(mode="json"),
                },
            )
        )
        return evt
