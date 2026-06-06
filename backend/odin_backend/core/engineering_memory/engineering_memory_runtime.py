"""Engineering memory orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.engineering_memory.architecture_memory import ArchitectureMemory
from odin_backend.core.engineering_memory.bug_memory import BugMemory
from odin_backend.core.engineering_memory.dependency_evolution import track_dependency_change
from odin_backend.core.engineering_memory.engineering_sessions import EngineeringSessions
from odin_backend.core.engineering_memory.patch_history import PatchHistory
from odin_backend.core.engineering_memory.repo_memory import RepoMemory
from odin_backend.core.engineering_memory.repository_timelines import RepositoryTimeline
from odin_backend.core.engineering_memory.technical_decisions import TechnicalDecisions


class EngineeringMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._repos = RepoMemory()
        self._architecture = ArchitectureMemory()
        self._bugs = BugMemory()
        self._patches = PatchHistory()
        self._sessions = EngineeringSessions()
        self._decisions = TechnicalDecisions()
        self._timelines = RepositoryTimeline()

    async def record_repo(self, *, repo: str, structure: dict[str, Any]) -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_memory_enabled", False):
            return {"accepted": False, "reason": "engineering_memory_disabled"}
        entry = self._repos.remember(repo=repo, structure=structure)
        self._timelines.add(repo=repo, event="structure_recorded", detail=structure)
        self._emit("repository_graph_updated", {"repo": repo, "nodes": len(structure.get("files", []))})
        return {"accepted": True, "entry": entry}

    async def record_bug(self, *, repo: str, error: str, fixed: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_memory_enabled", False):
            return {"accepted": False, "reason": "engineering_memory_disabled"}
        entry = self._bugs.record(repo=repo, error=error, fixed=fixed)
        self._timelines.add(repo=repo, event="bug_recorded", detail={"error": error[:120], "fixed": fixed})
        return {"accepted": True, "entry": entry}

    async def record_decision(self, *, repo: str, decision: str, rationale: str) -> dict[str, Any]:
        entry = self._decisions.record(repo=repo, decision=decision, rationale=rationale)
        self._architecture.note(repo=repo, layer="decision", detail=decision)
        return {"accepted": True, "entry": entry}

    async def record_patch(self, *, repo: str, patch_id: str, outcome: str) -> dict[str, Any]:
        entry = self._patches.record(repo=repo, patch_id=patch_id, outcome=outcome)
        return {"accepted": True, "entry": entry}

    async def start_session(self, *, repo: str, focus: str) -> dict[str, Any]:
        session = self._sessions.start(repo=repo, focus=focus)
        return {"accepted": True, "session": session}

    async def dependency_change(self, *, repo: str, package: str, from_ver: str, to_ver: str) -> dict[str, Any]:
        change = track_dependency_change(repo=repo, package=package, from_ver=from_ver, to_ver=to_ver)
        self._timelines.add(repo=repo, event="dependency_changed", detail=change)
        return {"accepted": True, **change}

    def snapshot(self) -> dict[str, Any]:
        return {
            "repos": self._repos.count(),
            "bugs": self._bugs.count(),
            "patches": self._patches.count(),
            "sessions": self._sessions.count(),
            "decisions": self._decisions.count(),
            "timelines": self._timelines.count(),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_memory")
