"""Native cognitive desktop shell orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.native_shell.command_palette import palette
from odin_backend.core.native_shell.desktop_shell import shell_state
from odin_backend.core.native_shell.dock_runtime import dock
from odin_backend.core.native_shell.quick_actions import quick
from odin_backend.core.native_shell.runtime_presence import presence
from odin_backend.core.native_shell.session_bar import bar
from odin_backend.core.native_shell.workspace_surface import surface


class NativeShellRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._shell = shell_state()
        self._notifications: list[dict] = []

    async def activate(self, *, workspace: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_shell_enabled", False):
            return {"accepted": False, "reason": "native_shell_disabled"}
        ws = workspace or {}
        surf = surface(app=ws.get("active_app", "desktop"), title=ws.get("title", ""))
        pal = palette(query="", workspace=ws)
        missions = 0
        if hasattr(self._app, "mission_manager"):
            missions = len(getattr(self._app.mission_manager, "_missions", {}) or {})
        self._emit("cognitive_surface_rendered", {"platform": self._shell["platform"]})
        self._emit("persistent_presence_updated", presence(energy=0.6))
        self._emit("workspace_focus_changed", {"app": surf["app"]})
        return {
            "accepted": True,
            "shell": self._shell,
            "surface": surf,
            "palette": pal,
            "dock": dock(),
            "session_bar": bar(missions=missions),
            "presence": presence(),
        }

    async def command(self, *, query: str, workspace: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_shell_enabled", False):
            return {"accepted": False, "reason": "native_shell_disabled"}
        return {"accepted": True, "palette": palette(query=query, workspace=workspace)}

    async def quick_action(self, *, action: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_shell_enabled", False):
            return {"accepted": False, "reason": "native_shell_disabled"}
        return {"accepted": True, **quick(action)}

    async def notify(self, *, title: str, body: str) -> dict[str, Any]:
        n = {"title": title[:80], "body": body[:200], "local_only": True}
        self._notifications.append(n)
        return {"accepted": True, "notification": n}

    def snapshot(self) -> dict[str, Any]:
        return {"shell": self._shell, "notifications": len(self._notifications)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="native_shell")
