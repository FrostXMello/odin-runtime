"""Real-time conversational presence layer (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.conversational_presence.conversation_continuity import restore_context
from odin_backend.core.conversational_presence.conversation_memory_threads import recall_thread
from odin_backend.core.conversational_presence.emotion_signals import emotion_from_energy
from odin_backend.core.conversational_presence.interrupt_reasoning import handle_interrupt
from odin_backend.core.conversational_presence.presence_sessions import PresenceSessions
from odin_backend.core.conversational_presence.realtime_turn_manager import RealtimeTurnManager
from odin_backend.core.conversational_presence.voice_attention import voice_attention


class ConversationalPresenceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions = PresenceSessions()
        self._turns = RealtimeTurnManager()
        self._familiarity = 0.5

    async def connect(self, *, thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "conversational_presence_enabled", False):
            return {"accepted": False, "reason": "conversational_presence_disabled"}
        session = self._sessions.open(thread_id=thread_id)
        continuity = await restore_context(self._app)
        self._emit("live_presence_updated", {"session_id": session["thread_id"]})
        return {
            "accepted": True,
            "session": session,
            "continuity": continuity,
            "local_first": True,
            "supervised": True,
        }

    async def turn(self, *, text: str, energy: float = 0.6) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversational_presence_enabled", False):
            return {"accepted": False, "reason": "conversational_presence_disabled"}
        turn = self._turns.next_turn()
        resp = {}
        if hasattr(self._app, "conversational_os"):
            resp = await self._app.conversational_os.interact(text=text)
        recall = await recall_thread(self._app, topic=text[:60])
        self._emit("conversation_memory_recalled", {"turn": turn})
        emotion = emotion_from_energy(energy)
        attention = voice_attention(energy=energy)
        return {
            "accepted": True,
            "turn": turn,
            "response": resp,
            "recall": recall,
            "emotion": emotion,
            "attention": attention,
            "familiarity": self._familiarity,
        }

    async def interrupt(self) -> dict[str, Any]:
        hit = await handle_interrupt(self._app)
        return {"accepted": True, "interrupt": hit}

    def snapshot(self) -> dict[str, Any]:
        return {"familiarity": self._familiarity}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversational_presence")
