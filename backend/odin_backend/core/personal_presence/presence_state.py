from __future__ import annotations
from typing import Any

from odin_backend.core.personal_presence.adaptive_personality import refine
from odin_backend.core.personal_presence.conversation_identity import identity
from odin_backend.core.personal_presence.interaction_rhythm import rhythm
from odin_backend.core.personal_presence.operator_relationship_memory import RelationshipMemory
from odin_backend.core.personal_presence.presence_continuity import restore
from odin_backend.core.personal_presence.session_familiarity import score


class PersonalPresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._relationship = RelationshipMemory()
        self._sessions = 0
        self._familiarity = 0.3

    async def connect(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "personal_presence_enabled", False):
            return {"accepted": False, "reason": "personal_presence_disabled"}
        self._sessions += 1
        rel = self._relationship.interact()
        self._familiarity = score(sessions=self._sessions)
        cont = await restore(self._app)
        ident = identity()
        pers = refine(familiarity=self._familiarity)
        self._emit("presence_familiarity_updated", {"familiarity": self._familiarity})
        return {
            "accepted": True,
            "identity": ident,
            "personality": pers,
            "continuity": cont,
            "relationship": rel,
            "bounded_personality": True,
            "local_first": True,
        }

    async def interact(self, *, text: str, energy: float = 0.6) -> dict[str, Any]:
        self._relationship.interact()
        cadence = rhythm(energy=energy)
        return {"accepted": True, "cadence": cadence, "familiarity": self._familiarity, "text_len": len(text)}

    def snapshot(self) -> dict[str, Any]:
        return {"familiarity": self._familiarity, "sessions": self._sessions}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="personal_presence")
