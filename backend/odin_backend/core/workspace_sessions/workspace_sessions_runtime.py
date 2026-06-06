"""Workspace sessions runtime (Prompt 54)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.workspace_sessions.session_store import WorkspaceSessionStore


class WorkspaceSessionsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "workspace_sessions.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = WorkspaceSessionStore(db)

    async def save_workspace_session(self, *, session_id: str = "default", repo: str = "", files: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_sessions_enabled", False):
            return {"accepted": False, "reason": "workspace_sessions_disabled"}
        payload = {"repo": repo[:80], "files": (files or [])[:20], "supervised": True}
        self._store.save(session_id=session_id, payload=payload)
        self._emit("workspace_session_saved", {"session_id": session_id})
        return {"accepted": True, "session_id": session_id, "payload": payload}

    async def restore_workspace_session(self, *, session_id: str = "default") -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_sessions_enabled", False):
            return {"accepted": False, "reason": "workspace_sessions_disabled"}
        data = self._store.load(session_id=session_id) or self._store.latest()
        if data:
            self._emit("workspace_session_restored", {"session_id": session_id})
        return {"accepted": True, "session": data}

    async def merge_workspace_context(self) -> dict[str, Any]:
        if hasattr(self._app, "workspace_coordination"):
            return await self._app.workspace_coordination.coordinate(projects=["local"])
        return {"accepted": True, "merged": True}

    async def build_resume_chain(self) -> dict[str, Any]:
        session = await self.restore_workspace_session()
        chain = []
        if session.get("session"):
            chain.append("workspace")
        if hasattr(self._app, "deferred_reasoning"):
            dr = self._app.deferred_reasoning.snapshot()
            if dr.get("pending", 0) > 0:
                chain.append("deferred_reasoning")
        return {"accepted": True, "chain": chain}

    def snapshot(self) -> dict[str, Any]:
        latest = self._store.latest()
        return {"has_session": latest is not None}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_sessions")
