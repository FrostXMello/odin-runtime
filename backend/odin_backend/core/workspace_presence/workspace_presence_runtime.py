"""Deep workspace integration orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.workspace_presence.active_project_detection import detect
from odin_backend.core.workspace_presence.browser_context_bridge import bridge
from odin_backend.core.workspace_presence.editor_presence import editor
from odin_backend.core.workspace_presence.live_workspace_graph import graph
from odin_backend.core.workspace_presence.repository_presence import repo as repo_presence
from odin_backend.core.workspace_presence.terminal_state_memory import TerminalMemory
from odin_backend.core.workspace_presence.workflow_state_tracking import track


class WorkspacePresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._terminal = TerminalMemory()
        self._project = ""

    async def observe(self, *, repo: str = "", branch: str = "main", terminal: dict | None = None, ide: dict | None = None, browser: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_presence_enabled", False):
            return {"accepted": False, "reason": "workspace_presence_disabled"}
        self._project = repo or self._project
        proj = detect(repo=repo or "unknown", branch=branch)
        if terminal and terminal.get("line"):
            self._terminal.remember(str(terminal["line"]))
        nodes = [n for n in [repo, branch, (ide or {}).get("file"), (browser or {}).get("url", "")[:30]] if n]
        g = graph(nodes=nodes)
        if hasattr(self._app, "context_fusion"):
            await self._app.context_fusion.fuse(ide=ide, terminal=terminal, browser=browser)
        if hasattr(self._app, "workstation_awareness"):
            await self._app.workstation_awareness.observe(snapshot={"app": "engineering", "title": repo})
        self._emit("workspace_context_restored", {"repo": repo, "nodes": len(nodes)})
        return {
            "accepted": True,
            "project": proj,
            "repository": repo_presence(name=repo, dirty=bool(terminal)),
            "editor": editor(file=str((ide or {}).get("file", "")), line=int((ide or {}).get("line", 1))),
            "browser": bridge(url=str((browser or {}).get("url", "")), title=str((browser or {}).get("title", ""))),
            "terminal": self._terminal.snapshot(),
            "workflow": track(state="engineering" if repo else "idle"),
            "graph": g,
        }

    async def restore_session(self) -> dict[str, Any]:
        return await self.observe(repo=self._project)

    def snapshot(self) -> dict[str, Any]:
        return {"project": self._project, "terminal_lines": len(self._terminal.snapshot())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_presence")
