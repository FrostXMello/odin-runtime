"""Desktop monitor — local awareness with privacy controls."""

from __future__ import annotations

from typing import Any

from odin_backend.core.desktop.active_window import parse_active_window
from odin_backend.core.desktop.clipboard_memory import ClipboardMemory
from odin_backend.core.desktop.notification_listener import NotificationListener
from odin_backend.core.desktop.process_observer import ProcessObserver
from odin_backend.core.desktop.workspace_sessions import WorkspaceSessions


class DesktopMonitor:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._processes = ProcessObserver()
        self._clipboard = ClipboardMemory()
        self._notifications = NotificationListener()
        self._sessions = WorkspaceSessions()
        self._enabled = getattr(app.settings, "desktop_awareness_enabled", False)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    async def ingest_snapshot(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        if not self._enabled:
            return {"accepted": False, "reason": "desktop awareness disabled"}
        active = parse_active_window(snapshot)
        usage = self._processes.observe(snapshot)
        if snapshot.get("clipboard"):
            self._clipboard.record(str(snapshot["clipboard"]))
        if active.get("app"):
            self._sessions.begin_segment(label=str(active.get("app")))
            if hasattr(self._app, "workspace_memory"):
                await self._app.workspace_memory.record_pattern(
                    kind="app_session",
                    label=str(active.get("app")),
                    metadata={"title": active.get("title", "")},
                )
                self._emit("workspace_pattern_learned", {"app": active.get("app")})
        if hasattr(self._app, "multimodal_perception"):
            await self._app.multimodal_perception.update_from_desktop(snapshot)
        self._emit("workspace_detected", {"active": active})
        return {
            "accepted": True,
            "active_window": active,
            "process_usage": usage,
            "clipboard_entries": len(self._clipboard.recent()),
            "timeline": self._sessions.timeline(),
        }

    def snapshot(self) -> dict[str, Any]:
        legacy = {}
        if hasattr(self._app, "desktop_runtime"):
            legacy = self._app.desktop_runtime.get_state()
        return {
            "enabled": self._enabled,
            "active_window": parse_active_window(legacy.get("last_state", {})),
            "clipboard": self._clipboard.recent()[-5:],
            "notifications": self._notifications.recent()[-5:],
            "timeline": self._sessions.timeline(),
            "legacy_runtime": legacy,
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_monitor")
