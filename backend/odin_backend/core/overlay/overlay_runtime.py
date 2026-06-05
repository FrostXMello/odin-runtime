"""Overlay runtime for visible supervised execution."""

from __future__ import annotations

from typing import Any

from odin_backend.core.overlay.action_visualizer import visualize_action
from odin_backend.core.overlay.cursor_highlighter import CursorHighlighter
from odin_backend.core.overlay.execution_annotations import ExecutionAnnotations
from odin_backend.core.overlay.live_status_overlay import LiveStatusOverlay


class OverlayRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._cursor = CursorHighlighter()
        self._annotations = ExecutionAnnotations()
        self._status = LiveStatusOverlay()
        self._enabled = getattr(app.settings, "overlay_enabled", False)

    def annotate_action(self, action: dict[str, Any]) -> None:
        if not self._enabled:
            return
        viz = visualize_action(action)
        self._annotations.add(viz)
        payload = action.get("payload", {})
        if payload.get("x") is not None and payload.get("y") is not None:
            self._cursor.set(x=int(payload["x"]), y=int(payload["y"]))
        self._status.set_status("executing", countdown=3)
        self._emit("overlay_rendered", viz)

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "cursor": self._cursor.snapshot(),
            "annotations": self._annotations.recent(),
            "status": self._status.snapshot(),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="overlay_runtime")
