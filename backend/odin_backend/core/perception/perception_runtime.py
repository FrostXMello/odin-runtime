"""Multimodal perception runtime — unified local operator intelligence state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.perception.active_workspace import ActiveWorkspace
from odin_backend.core.perception.desktop_state import DesktopState
from odin_backend.core.perception.multimodal_context import MultimodalContext
from odin_backend.core.perception.temporal_context import TemporalContext
from odin_backend.core.perception.visual_memory import VisualMemory


class MultimodalPerceptionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._context = MultimodalContext()
        self._desktop = DesktopState()
        self._visual = VisualMemory()
        self._temporal = TemporalContext()
        self._workspace = ActiveWorkspace()
        self._enabled = getattr(app.settings, "multimodal_perception_enabled", False)
        self._metrics: dict[str, int] = {"updates": 0, "snapshots": 0}

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    async def update_from_desktop(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        if not self._enabled:
            return {"accepted": False, "reason": "multimodal perception disabled"}
        self._desktop.apply_snapshot(snapshot)
        self._workspace.update_from_snapshot(snapshot)
        self._temporal.record_event("desktop_snapshot", snapshot.get("active_window", {}))
        self._context.stitch(
            desktop=self._desktop.snapshot(),
            workspace=self._workspace.snapshot(),
            temporal=self._temporal.recent_summary(),
        )
        self._metrics["updates"] += 1
        self._emit("perception_updated", {"source": "desktop"})
        if hasattr(self._app, "perception"):
            await self._app.perception.ingest_environment(snapshot)
        return self.snapshot()

    async def ingest_screenshot(self, *, path: str, analysis: dict[str, Any]) -> None:
        if not self._enabled:
            return
        self._visual.store(path, analysis)
        self._metrics["snapshots"] += 1
        self._context.stitch(visual=self._visual.recent(limit=3))
        self._emit("screen_parsed", {"path": path})

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "context": self._context.snapshot(),
            "desktop": self._desktop.snapshot(),
            "workspace": self._workspace.snapshot(),
            "visual": self._visual.recent(limit=5),
            "temporal": self._temporal.recent_summary(),
            "metrics": dict(self._metrics),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="perception_runtime")
