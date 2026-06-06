"""Native OS integration layer (Prompt 50)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.native_os.app_focus_tracker import track
from odin_backend.core.native_os.native_notification_runtime import NativeNotificationRuntime
from odin_backend.core.native_os.native_tray_runtime import NativeTrayRuntime
from odin_backend.core.native_os.window_manager_bridge import snapshot as window_snapshot


class NativeOSRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._notifications = NativeNotificationRuntime(app)
        self._tray = NativeTrayRuntime(app)
        self._focus = "odin"

    async def observe_desktop(self, *, window: str = "Odin") -> dict[str, Any]:
        if not getattr(self._app.settings, "native_os_enabled", False):
            return {"accepted": False, "reason": "native_os_disabled"}
        win = window_snapshot(title=window)
        focus = track(app=self._focus)
        self._emit("native_window_context_changed", {**win, **focus})
        if hasattr(self._app, "workspace_presence") and hasattr(self._app.workspace_presence, "observe"):
            await self._app.workspace_presence.observe(repo=window)
        return {"accepted": True, "window": win, "focus": focus, "local_first": True}

    async def window_state(self) -> dict[str, Any]:
        return {"accepted": True, **window_snapshot(title=self._focus)}

    async def show_tray(self) -> dict[str, Any]:
        return await self._tray.show()

    async def notify(self, *, title: str, body: str) -> dict[str, Any]:
        return await self._notifications.notify(title=title, body=body)

    def snapshot(self) -> dict[str, Any]:
        return {
            "focus": self._focus,
            "tray": self._tray.snapshot(),
            "notifications": self._notifications.snapshot(),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="native_os")
