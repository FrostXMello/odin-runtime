"""Persistent daemon mode orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.daemon.persistent_sessions import DaemonSessions
from odin_backend.core.daemon.startup_manager import StartupManager
from odin_backend.core.daemon.tray_runtime import TrayRuntime
from odin_backend.core.daemon.wake_scheduler import WakeScheduler


class DaemonRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._startup = StartupManager()
        self._tray = TrayRuntime()
        self._sessions = DaemonSessions()
        self._wake = WakeScheduler()
        self._idle = False

    async def start(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daemon_mode_enabled", False):
            return {"accepted": False, "reason": "daemon_mode_disabled"}
        started = self._startup.mark_started()
        if hasattr(self._app, "continuity_runtime"):
            await self._app.continuity_runtime.connect()
        if hasattr(self._app, "agent_execution"):
            resumed = await self._app.agent_execution.resume_pending()
            started["tasks_resumed"] = len(resumed)
        self._emit("daemon_started", started)
        return {"accepted": True, **started}

    async def enter_idle(self) -> dict[str, Any]:
        self._idle = True
        if hasattr(self._app, "background_cognition"):
            await self._app.background_cognition.run_cycle()
        return {"idle": True}

    def snapshot(self) -> dict[str, Any]:
        return {
            "started_at": self._startup._started_at,
            "recoveries": self._startup._recoveries,
            "sessions": self._sessions.count(),
            "idle": self._idle,
            "tray_visible": self._tray._visible,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="daemon")
