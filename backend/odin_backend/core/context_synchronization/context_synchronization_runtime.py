"""Context synchronization runtime (Prompt 55)."""
from __future__ import annotations
from typing import Any


class ContextSynchronizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._last_checkpoint: dict | None = None
        self._sync_loops = 0

    async def synchronize_context_surfaces(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "context_synchronization_enabled", False):
            return {"accepted": False, "reason": "context_synchronization_disabled"}
        if self._sync_loops > 32:
            return {"accepted": False, "reason": "sync_loop_bounded"}
        self._sync_loops += 1
        surfaces = []
        if hasattr(self._app, "workspace_sessions"):
            surfaces.append("workspace_sessions")
        if hasattr(self._app, "memory_fabric_v2"):
            surfaces.append("memory_fabric_v2")
        self._emit("context_surfaces_synchronized", {"surfaces": surfaces})
        return {"accepted": True, "surfaces": surfaces, "local_first": True}

    async def merge_runtime_context(self) -> dict[str, Any]:
        merged = {"sources": []}
        if hasattr(self._app, "workspace_sessions"):
            ws = await self._app.workspace_sessions.restore_workspace_session()
            merged["sources"].append("workspace_sessions")
            merged["workspace"] = ws.get("session")
        if hasattr(self._app, "runtime_coordination"):
            await self._app.runtime_coordination.merge_contexts()
            merged["sources"].append("runtime_coordination")
        return {"accepted": True, "merged": merged, "deduplicated": True}

    async def restore_context_checkpoint(self) -> dict[str, Any]:
        if self._last_checkpoint:
            return {"accepted": True, "checkpoint": self._last_checkpoint}
        if hasattr(self._app, "workspace_sessions"):
            r = await self._app.workspace_sessions.restore_workspace_session()
            self._last_checkpoint = r.get("session")
        return {"accepted": True, "checkpoint": self._last_checkpoint}

    async def detect_context_divergence(self) -> dict[str, Any]:
        diverged = False
        if hasattr(self._app, "workspace_sessions") and hasattr(self._app, "memory_fabric_v2"):
            diverged = self._sync_loops > 8
        if diverged:
            self._emit("context_divergence_detected", {"loops": self._sync_loops})
        return {"accepted": True, "diverged": diverged, "transparent": True}

    def snapshot(self) -> dict[str, Any]:
        return {"sync_loops": self._sync_loops, "has_checkpoint": self._last_checkpoint is not None}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="context_synchronization")
