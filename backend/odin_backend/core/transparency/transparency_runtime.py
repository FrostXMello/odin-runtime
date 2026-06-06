"""Safety and transparency layer."""
from __future__ import annotations
from typing import Any

from odin_backend.core.transparency.ai_disclosure import disclosure
from odin_backend.core.transparency.autonomy_disclosure import autonomy_status
from odin_backend.core.transparency.cognition_boundaries import boundaries
from odin_backend.core.transparency.operator_visibility import visibility


class TransparencyRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def explain(self, *, feature: str, confidence: float = 0.7, reason: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "transparency_enabled", False):
            return {"accepted": False, "reason": "transparency_disabled"}
        return {
            "accepted": True,
            "disclosure": disclosure(feature=feature),
            "boundaries": boundaries(),
            "visibility": visibility(confidence=confidence, reason=reason or "heuristic analysis"),
            "autonomy": autonomy_status(mode=getattr(self._app.settings, "survival_mode", "balanced")),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"boundaries": boundaries(), "autonomy": autonomy_status(mode="supervised")}

