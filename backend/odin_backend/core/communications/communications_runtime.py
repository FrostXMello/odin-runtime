"""Communications orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.communications.briefing_engine import generate_briefing
from odin_backend.core.communications.communication_center import CommunicationCenter
from odin_backend.core.communications.inbox_memory import InboxMemory
from odin_backend.core.communications.message_context import build_context
from odin_backend.core.communications.notification_runtime import NotificationRuntime


class CommunicationsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._center = CommunicationCenter()
        self._inbox = InboxMemory()
        self._notify = NotificationRuntime()

    async def briefing(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "communications_enabled", False):
            return {"accepted": False, "reason": "communications_disabled"}
        projects = []
        tasks = []
        if hasattr(self._app, "project_os"):
            projects = self._app.project_os._registry.list_all()
        if hasattr(self._app, "productivity_runtime"):
            tasks = self._app.productivity_runtime._tasks.list_open()
        brief = generate_briefing(projects=projects, tasks=tasks, events=self._center.recent())
        ctx = build_context(projects=projects, tasks=tasks)
        self._emit("briefing_generated", brief)
        notif = self._notify.notify(title="Odin briefing", body=brief["summary"])
        self._inbox.push({**brief, "notification": notif})
        return {"accepted": True, "briefing": brief, "context": ctx}

    async def alert(self, *, kind: str, message: str) -> dict[str, Any]:
        entry = self._center.alert(kind=kind, message=message)
        notif = self._notify.notify(title=kind, body=message)
        self._inbox.push({**entry, "notification": notif})
        return {"accepted": True, "alert": entry}

    def snapshot(self) -> dict[str, Any]:
        return {"inbox_unread": len(self._inbox.unread()), "alerts": len(self._center.recent())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="communications")
