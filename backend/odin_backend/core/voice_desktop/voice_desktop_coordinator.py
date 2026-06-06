"""Desktop-first voice experience coordinator."""
from __future__ import annotations
from typing import Any

VOICE_MODES = ("passive", "assistant", "immersive", "daemon")


class VoiceDesktopCoordinator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = "assistant"

    async def listen(self, *, text: str, energy: float = 0.6, push_to_talk: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "voice_desktop_enabled", False):
            return {"accepted": False, "reason": "voice_desktop_disabled"}
        if not getattr(self._app.settings, "realtime_voice_enabled", False):
            return {"accepted": False, "reason": "realtime_voice_disabled"}
        resp = await self._app.realtime_voice.process_utterance(text=text, energy=energy)
        if hasattr(self._app, "daemon_runtime") and self._mode == "daemon":
            await self._app.daemon_runtime.cognitive_tick(wakeword="odin", energy=energy)
        return {"accepted": True, "voice": resp, "mode": self._mode, "push_to_talk": push_to_talk, "subtitles": True}

    async def interrupt(self) -> dict[str, Any]:
        hit = self._app.realtime_voice.interrupt()
        if hasattr(self._app, "daemon_runtime"):
            await self._app.daemon_runtime.handle_interrupt(reason="voice")
        self._emit("voice_interrupt_detected", hit if isinstance(hit, dict) else {"interrupted": True})
        return {"accepted": True, "interrupt": hit}

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in VOICE_MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        return {"accepted": True, "mode": mode}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "modes": list(VOICE_MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="voice_desktop")
