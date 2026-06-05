"""Persistent daemon mode orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.daemon.adaptive_polling import poll_interval
from odin_backend.core.daemon.daemon_memory_compaction import compact_daemon_state
from odin_backend.core.daemon.heartbeat_persistence import HeartbeatPersistence
from odin_backend.core.daemon.idle_sleep_scheduler import should_wake, sleep_interval
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
        self._heartbeat = HeartbeatPersistence()
        self._idle = False
        self._uptime_s = 0.0

    async def start(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daemon_mode_enabled", False):
            return {"accepted": False, "reason": "daemon_mode_disabled"}
        started = self._startup.mark_started()
        if hasattr(self._app, "continuity_runtime"):
            await self._app.continuity_runtime.connect()
        if hasattr(self._app, "agent_execution"):
            resumed = await self._app.agent_execution.resume_pending()
            started["tasks_resumed"] = len(resumed)
        self._heartbeat.beat(component="daemon", uptime_s=self._uptime_s)
        self._emit("daemon_started", started)
        return {"accepted": True, **started}

    async def restore_session(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daemon_mode_enabled", False):
            return {"restored": False, "reason": "daemon_mode_disabled"}
        if hasattr(self._app, "continuity_runtime"):
            await self._app.continuity_runtime.connect()
        self._startup._recoveries += 1
        self._emit("daemon_restored", {"recoveries": self._startup._recoveries})
        return {"restored": True, "recoveries": self._startup._recoveries}

    async def enter_idle(self) -> dict[str, Any]:
        self._idle = True
        if hasattr(self._app, "background_cognition"):
            await self._app.background_cognition.run_cycle()
        compact = compact_daemon_state(cache_entries=self._sessions.count())
        self._heartbeat.beat(component="daemon_idle", uptime_s=self._uptime_s)
        return {"idle": True, "compaction": compact}

    async def tick(self, *, activity_score: float = 0.0) -> dict[str, Any]:
        self._uptime_s += poll_interval(pressure="normal", idle=self._idle)
        if self._idle and should_wake(activity_score=activity_score):
            self._idle = False
        interval = sleep_interval(idle=self._idle, on_battery=getattr(self._app.settings, "on_battery", False))
        self._heartbeat.beat(component="daemon", uptime_s=self._uptime_s)
        return {"idle": self._idle, "poll_s": interval, "uptime_s": self._uptime_s}

    def snapshot(self) -> dict[str, Any]:
        return {
            "started_at": self._startup._started_at,
            "recoveries": self._startup._recoveries,
            "sessions": self._sessions.count(),
            "idle": self._idle,
            "tray_visible": self._tray._visible,
            "uptime_s": self._uptime_s,
            "heartbeat": self._heartbeat.snapshot(),
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
