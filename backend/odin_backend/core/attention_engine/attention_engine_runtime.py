"""Attention engine (Prompt 52)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.attention_engine.focus_heatmap import heatmap
from odin_backend.core.attention_engine.interruption_classifier import classify
from odin_backend.core.attention_engine.salience_scorer import score

PROFILES = ("survival", "balanced", "engineering", "immersive", "overnight")


class AttentionEngineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._profile = "balanced"
        self._focus = "workspace"
        self._weights: dict[str, float] = {"workspace": 0.5, "engineering": 0.3}

    async def calculate_attention_weights(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "attention_engine_enabled", False):
            return {"accepted": False, "reason": "attention_engine_disabled"}
        s = score(repos=2, failures=1, pending=1)
        return {"accepted": True, "weights": self._weights, "salience": s, "profile": self._profile}

    async def shift_attention(self, *, focus: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "attention_engine_enabled", False):
            return {"accepted": False, "reason": "attention_engine_disabled"}
        self._focus = focus[:60]
        self._weights[self._focus] = min(1.0, self._weights.get(self._focus, 0.3) + 0.1)
        self._emit("attention_shift_detected", {"focus": self._focus})
        if hasattr(self._app, "attention_flow"):
            await self._app.attention_flow.route(focus=self._focus)
        return {"accepted": True, "focus": self._focus, "bounded": True}

    async def detect_attention_conflict(self) -> dict[str, Any]:
        conflicts = [k for k, v in self._weights.items() if v > 0.8]
        return {"accepted": True, "conflicts": conflicts, "has_conflict": len(conflicts) > 1}

    async def compute_focus_heatmap(self) -> dict[str, Any]:
        cells = heatmap(weights=self._weights)
        self._emit("focus_heatmap_updated", {"cells": len(cells)})
        return {"accepted": True, "heatmap": cells}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile}

    def snapshot(self) -> dict[str, Any]:
        return {"focus": self._focus, "profile": self._profile, "weights": self._weights}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="attention_engine")
