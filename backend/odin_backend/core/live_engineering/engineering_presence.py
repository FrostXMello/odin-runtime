from __future__ import annotations
from typing import Any

from odin_backend.core.live_engineering.architecture_assistant import advise
from odin_backend.core.live_engineering.live_debug_assistant import assist
from odin_backend.core.live_engineering.live_patch_assist import suggest
from odin_backend.core.live_engineering.realtime_repo_awareness import observe
from odin_backend.core.live_engineering.terminal_reasoning import reason
from odin_backend.core.live_engineering.workflow_guidance import guide


class LiveEngineeringRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._repo = ""

    async def session(self, *, repo: str, terminal: dict | None = None, ide: dict | None = None, error: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_engineering_enabled", False):
            return {"accepted": False, "reason": "live_engineering_disabled"}
        self._repo = repo
        obs = observe(repo=repo, branch=terminal.get("branch", "main") if terminal else "main")
        if hasattr(self._app, "context_fusion"):
            await self._app.context_fusion.fuse(ide=ide, terminal=terminal)
        if hasattr(self._app, "workstation_awareness"):
            await self._app.workstation_awareness.observe(snapshot={"app": "engineering", "title": repo})
        dbg = assist(error=error) if error else {"hints": []}
        term = reason(line=str((terminal or {}).get("line", "")))
        self._emit("live_engineering_detected", {"repo": repo})
        if error:
            patch = suggest(file=str((ide or {}).get("file", "unknown")), issue=error)
            self._emit("live_patch_suggested", patch)
        return {
            "accepted": True,
            "repo": obs,
            "debug": dbg,
            "terminal": term,
            "guidance": guide(step="debug" if error else "observe"),
            "architecture": advise(component=repo),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"repo": self._repo}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_engineering")
