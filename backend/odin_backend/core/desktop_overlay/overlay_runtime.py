"""Floating desktop overlay orchestrator."""
from __future__ import annotations
from typing import Any

OVERLAY_KINDS = ("terminal", "debug", "mission_hud", "subtitles", "memory_hint", "workflow")


class DesktopOverlayRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attached: list[str] = []

    async def attach(self, *, kind: str, context: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "desktop_overlay_enabled", False):
            return {"accepted": False, "reason": "desktop_overlay_disabled"}
        k = kind if kind in OVERLAY_KINDS else "workflow"
        self._attached.append(k)
        panel = {"kind": k, "movable": True, "transparent": True, "local_only": True}
        if hasattr(self._app, "live_overlay"):
            ext = await self._app.live_overlay.render(context=context or {}, mode="assistive")
            panel["live_overlay"] = ext.get("panels", {})
        self._emit("overlay_attached", {"kind": k})
        return {"accepted": True, "overlay": panel, "attached": self._attached[-6:]}

    async def memory_surface(self) -> dict[str, Any]:
        threads = {}
        if hasattr(self._app, "memory_threads"):
            threads = await self._app.memory_threads.recall()
        self._emit("memory_surface_rendered", {"threads": len(threads.get("threads", []))})
        return {"accepted": True, "memory": threads}

    def snapshot(self) -> dict[str, Any]:
        return {"attached": self._attached}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_overlay")
