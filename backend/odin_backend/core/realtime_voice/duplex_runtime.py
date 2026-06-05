"""Low-latency duplex voice runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.realtime_voice.conversational_memory import ConversationalMemory
from odin_backend.core.realtime_voice.emotional_tone import estimate_tone
from odin_backend.core.realtime_voice.interruption_detection import InterruptionDetection
from odin_backend.core.realtime_voice.latency_optimizer import optimize
from odin_backend.core.realtime_voice.voice_activity_detection import is_speech_active


class RealtimeVoiceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = ConversationalMemory()
        self._interrupt = InterruptionDetection()
        self._session_id: str | None = None

    async def process_utterance(self, *, text: str, energy: float = 0.5) -> dict[str, Any]:
        if not getattr(self._app.settings, "realtime_voice_enabled", False):
            return {"accepted": False, "reason": "realtime_voice_disabled"}
        if not is_speech_active(energy=energy):
            return {"accepted": False, "reason": "no_speech"}
        if self._interrupt.check().get("interrupted"):
            return {"accepted": False, "reason": "interrupted"}
        self._memory.add_turn(role="user", content=text)
        tone = estimate_tone(text)
        response = f"Acknowledged: {text[:60]}"
        if hasattr(self._app, "local_ai"):
            gen = await self._app.local_ai.generate(prompt=text, template="summary")
            response = gen.get("text", response)
        self._memory.add_turn(role="assistant", content=response)
        lat = optimize(stt_ms=50, llm_ms=200, tts_ms=80)
        self._emit("voice_turn_completed", {"latency_ms": lat["total_ms"]})
        return {"accepted": True, "response": response, "tone": tone, "latency": lat}

    def interrupt(self) -> None:
        self._interrupt.signal()

    def snapshot(self) -> dict[str, Any]:
        return {"turns": len(self._memory._turns), "session_id": self._session_id}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="realtime_voice")
