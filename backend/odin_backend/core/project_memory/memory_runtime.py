"""Persistent project memory (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.project_memory.architecture_memory import ArchitectureMemory
from odin_backend.core.project_memory.decision_memory import DecisionMemory
from odin_backend.core.project_memory.dependency_memory import deps_for
from odin_backend.core.project_memory.engineering_sessions import EngineeringSessions
from odin_backend.core.project_memory.issue_history import recurrence
from odin_backend.core.project_memory.project_resume import load_resume, save_resume
from odin_backend.core.project_memory.project_timeline import ProjectTimeline


class ProjectMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._timeline = ProjectTimeline()
        self._decisions = DecisionMemory()
        self._sessions = EngineeringSessions()
        self._architecture = ArchitectureMemory()
        self._path = "./data/project_memory.json"

    async def remember(self, *, repo: str, decision: str = "", issue: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "project_memory_enabled", False):
            return {"accepted": False, "reason": "project_memory_disabled"}
        self._sessions.start(repo)
        if decision:
            self._decisions.record(decision, rationale=issue or repo)
            self._timeline.add("decision", decision)
        if issue:
            self._timeline.add("issue", issue)
        self._architecture.remember(repo, note=decision or "active")
        save_resume(path=self._path, data={"repo": repo, "timeline": self._timeline.replay()})
        return {
            "accepted": True,
            "timeline": self._timeline.replay(),
            "dependencies": deps_for(repo),
            "recurrence": recurrence([issue] if issue else []),
        }

    async def resume(self, *, repo: str = "") -> dict[str, Any]:
        restored = load_resume(path=self._path)
        if restored.get("restored"):
            self._emit("engineering_session_restored", {"repo": repo or restored.get("data", {}).get("repo")})
        return {"accepted": True, **restored, "timeline": self._timeline.replay()}

    def snapshot(self) -> dict[str, Any]:
        return {"timeline_len": len(self._timeline.replay())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="project_memory")
