"""Productivity orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.productivity.focus_sessions import FocusSessions
from odin_backend.core.productivity.habit_tracking import HabitTracking
from odin_backend.core.productivity.interruption_filter import should_interrupt
from odin_backend.core.productivity.project_deadlines import ProjectDeadlines
from odin_backend.core.productivity.reminder_engine import ReminderEngine
from odin_backend.core.productivity.schedule_awareness import schedule_context
from odin_backend.core.productivity.task_runtime import TaskRuntime
from odin_backend.core.productivity.workload_analysis import analyze_workload


class ProductivityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._tasks = TaskRuntime()
        self._focus = FocusSessions()
        self._habits = HabitTracking()
        self._reminders = ReminderEngine()
        self._deadlines = ProjectDeadlines()

    async def create_task(self, *, title: str, project_id: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "productivity_enabled", False):
            return {"accepted": False, "reason": "productivity_disabled"}
        task = self._tasks.create(title=title, project_id=project_id)
        self._emit("productivity_pattern_detected", {"pattern": "task_created"})
        return {"accepted": True, "task": task}

    async def start_focus(self, *, label: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "productivity_enabled", False):
            return {"accepted": False, "reason": "productivity_disabled"}
        session = self._focus.start(label=label)
        self._emit("focus_session_started", session)
        return {"accepted": True, "session": session}

    async def stop_focus(self) -> dict[str, Any]:
        ended = self._focus.stop()
        return {"accepted": True, "session": ended}

    def analytics(self) -> dict[str, Any]:
        tasks = list(self._tasks._tasks.values())
        return {
            "schedule": schedule_context(),
            "workload": analyze_workload(tasks),
            "reminders": len(self._reminders.due()),
            "deadlines": len(self._deadlines.upcoming()),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"open_tasks": len(self._tasks.list_open()), "analytics": self.analytics()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="productivity")
