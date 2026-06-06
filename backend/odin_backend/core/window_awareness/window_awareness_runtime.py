"""Window awareness runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.window_awareness.window_classifier import classify


class WindowAwarenessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._active = {"title": "Odin", "app": "odin"}
        self._exclusions: list[str] = []
        self._monitoring_visible = True

    async def detect_workspace_transition(self, *, window: str, app: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "window_awareness_enabled", False):
            return {"accepted": False, "reason": "window_awareness_disabled"}
        if not getattr(self._app.settings, "window_tracking_enabled", True):
            return {"accepted": False, "reason": "window_tracking_disabled"}
        prior = self._active.copy()
        self._active = {"title": window[:120], "app": app[:60]}
        if prior.get("title") != window:
            self._emit("workspace_transition_detected", {"from": prior.get("title"), "to": window[:60]})
        return {"accepted": True, "transition": True, "transparent": True, "exclusions": self._exclusions}

    async def classify_active_window(self) -> dict[str, Any]:
        c = classify(title=self._active.get("title", ""), app=self._active.get("app", ""))
        self._emit("active_window_classified", c)
        return {"accepted": True, "classification": c}

    async def estimate_focus_depth(self) -> dict[str, Any]:
        depth = 0.7 if self._active.get("app") not in self._exclusions else 0.2
        return {"accepted": True, "depth": depth}

    async def build_workspace_snapshot(self) -> dict[str, Any]:
        c = classify(title=self._active.get("title", ""), app=self._active.get("app", ""))
        return {"accepted": True, "snapshot": {"active": self._active, "classification": c, "monitoring_visible": self._monitoring_visible}}

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "monitoring_visible": self._monitoring_visible}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="window_awareness")
