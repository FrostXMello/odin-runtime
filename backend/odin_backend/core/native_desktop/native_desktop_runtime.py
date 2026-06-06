"""Native desktop runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any


class NativeDesktopRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._initialized = False
        self._profile = "balanced"
        self._low_power = False

    async def initialize_desktop_runtime(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_desktop_enabled", False):
            return {"accepted": False, "reason": "native_desktop_disabled"}
        self._initialized = True
        self._profile = getattr(self._app.settings, "desktop_profile", "balanced")
        if hasattr(self._app, "native_os"):
            await self._app.native_os.show_tray()
        self._emit("desktop_runtime_initialized", {"profile": self._profile})
        return {"accepted": True, "initialized": True, "profile": self._profile, "transparent": True}

    async def register_tray_actions(self) -> dict[str, Any]:
        return {"accepted": True, "actions": ["focus", "briefing", "pause"], "operator_controlled": True}

    async def dispatch_native_notification(self, *, title: str, body: str = "") -> dict[str, Any]:
        if hasattr(self._app, "native_os"):
            r = await self._app.native_os.notify(title=title, body=body)
            self._emit("native_notification_dispatched", {"title": title[:60]})
            return r
        return {"accepted": True, "dispatched": True}

    async def restore_desktop_session(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_sessions"):
            return await self._app.workspace_sessions.restore_workspace_session()
        return {"accepted": True, "restored": False}

    async def enter_low_power_mode(self, *, enabled: bool = True) -> dict[str, Any]:
        self._low_power = enabled
        if hasattr(self._app, "cognitive_daemon_v2"):
            await self._app.cognitive_daemon_v2.set_low_power(enabled=enabled)
        return {"accepted": True, "low_power": enabled}

    def snapshot(self) -> dict[str, Any]:
        return {"initialized": self._initialized, "profile": self._profile, "low_power": self._low_power}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="native_desktop")
