"""Cognitive memory continuity orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognitive_continuity.active_memory_threads import MemoryThreads
from odin_backend.core.cognitive_continuity.cognitive_session_restore import restore_session
from odin_backend.core.cognitive_continuity.continuity_linker import link_threads
from odin_backend.core.cognitive_continuity.long_horizon_context import build_horizon
from odin_backend.core.cognitive_continuity.unfinished_work_tracker import UnfinishedWorkTracker


class CognitiveContinuityRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads = MemoryThreads()
        self._unfinished = UnfinishedWorkTracker()

    async def track_work(self, *, title: str, project: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_continuity_enabled", False):
            return {"accepted": False, "reason": "cognitive_continuity_disabled"}
        entry = self._unfinished.add(title=title, project=project)
        thread = self._threads.open(project=project, focus=title)
        self._emit("unfinished_work_detected", {"title": title, "project": project})
        return {"accepted": True, "work": entry, "thread": thread}

    async def restore(self) -> dict[str, Any]:
        restored = restore_session(threads=self._threads.list_all(), unfinished=self._unfinished.list_all())
        if restored.get("restored"):
            self._emit("continuity_restored_live", restored)
        horizon = build_horizon(threads=self._threads.list_all())
        linked = link_threads(threads=self._threads.list_all())
        return {"accepted": True, "restored": restored, "horizon": horizon, "linked": linked}

    def snapshot(self) -> dict[str, Any]:
        return {"threads": len(self._threads.list_all()), "unfinished": len(self._unfinished.list_all())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_continuity")
