"""Embodied presence orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.presence.ambient_state import ambient
from odin_backend.core.presence.conversational_rhythm import rhythm
from odin_backend.core.presence.emotion_model import estimate_emotion
from odin_backend.core.presence.expression_engine import expression_for
from odin_backend.core.presence.interaction_energy import track_energy
from odin_backend.core.presence.operator_sync import sync_score
from odin_backend.core.presence.personality_projection import project


class PresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._events = 0
        self._emotion = estimate_emotion(energy=0.5)
        self._personality = project()

    async def update(self, *, energy: float | None = None, idle_s: float = 0.0) -> dict[str, Any]:
        if not getattr(self._app.settings, "presence_enabled", False):
            return {"accepted": False, "reason": "presence_disabled"}
        e = energy if energy is not None else track_energy(events=self._events, duration_s=max(idle_s, 1))
        self._emotion = estimate_emotion(energy=e)
        expr = expression_for(self._emotion["mood"])
        amb = ambient(idle_s=idle_s)
        sync = sync_score(operator_actions=max(1, self._events), odin_responses=self._events)
        self._emit("presence_shifted", {"mood": self._emotion["mood"], "simulated": True})
        self._emit("emotional_state_updated", {**self._emotion, "expression": expr["color"]})
        return {
            "accepted": True,
            "emotion": self._emotion,
            "expression": expr,
            "ambient": amb,
            "rhythm": rhythm(),
            "sync": sync,
            "personality": self._personality,
            "disclosure": "simulated_emotional_model",
        }

    async def record_interaction(self) -> dict[str, Any]:
        self._events += 1
        return {"accepted": True, "events": self._events}

    def snapshot(self) -> dict[str, Any]:
        return {"emotion": self._emotion, "personality": self._personality, "events": self._events}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="presence")
