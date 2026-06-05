"""Project OS orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.project_os.codebase_context import build_codebase_context
from odin_backend.core.project_os.continuity_engine import restore_context
from odin_backend.core.project_os.project_memory import ProjectMemory
from odin_backend.core.project_os.project_registry import ProjectRegistry
from odin_backend.core.project_os.repository_intelligence import summarize_repo
from odin_backend.core.project_os.session_linking import SessionLinking
from odin_backend.core.project_os.task_history import TaskHistory
from odin_backend.core.project_os.workflow_patterns import detect_patterns
from odin_backend.core.project_os.workspace_indexer import index_workspace


class ProjectOSRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._registry = ProjectRegistry()
        self._memory = ProjectMemory()
        self._sessions = SessionLinking()
        self._tasks = TaskHistory()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def register_project(self, *, name: str, path: str, metadata: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "project_os_enabled", False):
            return {"accepted": False, "reason": "project_os_disabled"}
        project = self._registry.register(name=name, path=path, metadata=metadata)
        indexed = index_workspace(root=path)
        ctx = build_codebase_context(repo_path=path)
        self._memory.append(project["id"], text=f"Registered project {name}", kind="register")
        self._emit("repository_indexed", {"project_id": project["id"], "path": path})
        return {"accepted": True, "project": project, "index": indexed, "codebase": ctx}

    async def restore(self, project_id: str, *, session_id: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "project_os_enabled", False):
            return {"accepted": False, "reason": "project_os_disabled"}
        project = self._registry.get(project_id)
        if not project:
            return {"accepted": False, "reason": "project_not_found"}
        timeline = self._memory.timeline(project_id)
        restored = restore_context(project=project, timeline=timeline)
        if session_id:
            self._sessions.link(session_id, project_id)
        self._emit("project_context_restored", restored)
        self._emit("coding_session_resumed", {"project_id": project_id, "session_id": session_id})
        return {"accepted": True, **restored}

    async def summarize(self, project_id: str) -> dict[str, Any]:
        project = self._registry.get(project_id)
        if not project:
            return {"error": "project_not_found"}
        repo = summarize_repo(path=project["path"])
        patterns = detect_patterns(self._memory.timeline(project_id))
        return {"project": project, "repo": repo, "patterns": patterns}

    def snapshot(self) -> dict[str, Any]:
        return {
            "projects": len(self._registry.list_all()),
            "project_list": self._registry.list_all()[-10:],
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="project_os")
