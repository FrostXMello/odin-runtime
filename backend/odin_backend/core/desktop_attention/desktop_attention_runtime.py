"""Desktop attention runtime (Prompt 54)."""
from __future__ import annotations
from typing import Any


class DesktopAttentionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._salience: dict[str, float] = {"workspace": 0.5, "engineering": 0.4}

    async def prioritize_desktop_attention(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "desktop_attention_enabled", False):
            return {"accepted": False, "reason": "desktop_attention_disabled"}
        if hasattr(self._app, "attention_engine"):
            await self._app.attention_engine.calculate_attention_weights()
        self._emit("desktop_attention_rebalanced", {"salience": self._salience})
        return {"accepted": True, "salience": self._salience, "bounded": True}

    async def compute_workspace_salience(self, *, workspace: str) -> dict[str, Any]:
        score = min(1.0, self._salience.get(workspace, 0.3) + 0.1)
        self._salience[workspace[:40]] = score
        self._emit("workspace_salience_updated", {"workspace": workspace[:40], "score": score})
        return {"accepted": True, "workspace": workspace[:40], "score": score}

    async def suppress_low_priority_surfaces(self) -> dict[str, Any]:
        if hasattr(self._app, "live_overlays_v2"):
            await self._app.live_overlays_v2.suppress_overlay(overlay_type="memory_recall")
        return {"accepted": True, "suppressed_low_priority": True}

    async def rebalance_attention_surfaces(self) -> dict[str, Any]:
        return await self.prioritize_desktop_attention()

    def snapshot(self) -> dict[str, Any]:
        return {"salience": self._salience}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_attention")
