"""Live workspace overlay orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.live_overlay.cognitive_notifications import notify
from odin_backend.core.live_overlay.contextual_hints import OVERLAY_MODES, hint
from odin_backend.core.live_overlay.debug_overlay import debug_panel
from odin_backend.core.live_overlay.execution_overlay import execution_panel
from odin_backend.core.live_overlay.inline_reasoning import inline
from odin_backend.core.live_overlay.workspace_annotations import annotate


class LiveOverlayRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "assistant"

    async def render(self, *, context: dict | None = None, mode: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_overlay_enabled", False):
            return {"accepted": False, "reason": "live_overlay_disabled"}
        self._mode = mode or self._mode
        ctx = context or {}
        h = hint(context=ctx, mode=self._mode)
        panels = {
            "hint": h,
            "notification": notify(title="Odin", body=h["text"]),
            "inline": inline(line=ctx.get("line", 1), reasoning="contextual analysis"),
            "annotation": annotate(target=ctx.get("file", "workspace"), note=h["text"]),
        }
        if ctx.get("error"):
            panels["debug"] = debug_panel(error=str(ctx["error"]))
        if ctx.get("workflow_id"):
            panels["execution"] = execution_panel(workflow_id=str(ctx["workflow_id"]), step="active")
        if ctx.get("mission_id"):
            panels["mission_hud"] = {"mission_id": ctx["mission_id"], "state": ctx.get("mission_state", "active")}
        if ctx.get("terminal"):
            panels["terminal_overlay"] = {"line": str(ctx["terminal"].get("line", ""))[:120]}
        if self._mode in ("assistive", "collaborative", "engineering"):
            panels["recovery_prompt"] = {"visible": bool(ctx.get("interrupted")), "supervised": True}
        self._emit("live_overlay_rendered", {"mode": self._mode, "panels": list(panels.keys())})
        self._emit("attention_focus_changed", {"mode": self._mode})
        return {"accepted": True, "mode": self._mode, "panels": panels, "modes": list(OVERLAY_MODES)}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "modes": list(OVERLAY_MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_overlay")
