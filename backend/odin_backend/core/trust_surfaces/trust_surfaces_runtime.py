"""Trust surfaces runtime (Prompt 59)."""
from __future__ import annotations
from typing import Any


class TrustSurfacesRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._trust = 0.75
        self._integrity = 0.8

    async def compute_operator_trust(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "trust_surfaces_enabled", False):
            return {"accepted": False, "reason": "trust_surfaces_disabled"}
        if hasattr(self._app, "operator_alignment"):
            a = await self._app.operator_alignment.estimate_operator_alignment()
            self._trust = a.get("alignment", 0.75)
        self._emit("operator_trust_updated", {"trust": self._trust})
        return {"accepted": True, "trust": round(self._trust, 2), "explainable": True, "bounded": True}

    async def estimate_supervision_integrity(self) -> dict[str, Any]:
        self._emit("supervision_integrity_evaluated", {"integrity": self._integrity})
        return {"accepted": True, "integrity": round(self._integrity, 2), "operator_visible": True}

    async def surface_governance_confidence(self) -> dict[str, Any]:
        return {"accepted": True, "confidence": round((self._trust + self._integrity) / 2, 2), "transparent": True}

    async def detect_alignment_instability(self) -> dict[str, Any]:
        unstable = self._trust < 0.4
        return {"accepted": True, "unstable": unstable, "operator_override": True}

    def snapshot(self) -> dict[str, Any]:
        return {"trust": self._trust, "integrity": self._integrity}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="trust_surfaces")
