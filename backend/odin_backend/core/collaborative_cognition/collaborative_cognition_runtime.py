"""Collaborative cognition runtime (Prompt 62)."""
from __future__ import annotations
from typing import Any

PROFILES = ("solo", "pair", "team", "supervisory", "overnight_collaboration")


class CollaborativeCognitionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._initialized = False
        self._profile = "balanced"
        self._attention = 0.5
        self._sync_loops = 0
        self._surfaces: dict[str, str] = {}

    async def initialize_collaboration(self, *, profile: str = "team") -> dict[str, Any]:
        if not getattr(self._app.settings, "collaborative_cognition_enabled", False):
            return {"accepted": False, "reason": "collaborative_cognition_disabled"}
        if profile not in PROFILES:
            profile = getattr(self._app.settings, "collaboration_profile", "balanced")
        self._initialized = True
        self._profile = profile
        self._emit("collaborative_cognition_initialized", {"profile": self._profile})
        return {"accepted": True, "initialized": True, "profile": self._profile, "transparent": True}

    async def synchronize_operator_state(self) -> dict[str, Any]:
        if self._sync_loops > 48:
            return {"accepted": False, "reason": "collaboration_sync_bounded"}
        self._sync_loops += 1
        if hasattr(self._app, "operator_sessions"):
            await self._app.operator_sessions.synchronize_session_state()
        return {"accepted": True, "synchronized": True, "bounded": True}

    async def assign_cognition_surface(self, *, operator_id: str = "operator-local", surface: str = "shared-command") -> dict[str, Any]:
        self._surfaces[operator_id] = surface
        return {"accepted": True, "operator_id": operator_id, "surface": surface, "operator_visible": True}

    async def rebalance_shared_attention(self) -> dict[str, Any]:
        self._attention = max(0.1, self._attention - 0.05)
        if hasattr(self._app, "team_coordination"):
            await self._app.team_coordination.rebalance_team_attention()
        return {"accepted": True, "attention": round(self._attention, 2), "permission_aware": True}

    def snapshot(self) -> dict[str, Any]:
        return {"initialized": self._initialized, "profile": self._profile, "attention": self._attention, "surfaces": self._surfaces}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="collaborative_cognition")
