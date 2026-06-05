"""Voice runtime orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.voice.realtime_conversation import RealtimeConversation
from odin_backend.core.voice.wakeword import WakewordDetector


class VoiceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._conversation = RealtimeConversation(app)
        self._wakeword = WakewordDetector(enabled=getattr(app.settings, "voice_enabled", False))

    async def start_session(self) -> dict[str, Any]:
        result = await self._conversation.start()
        obs = getattr(self._app, "observability", None)
        if obs:
            from odin_backend.core.observability.events import TraceEventKind

            obs.tracer.record(
                TraceEventKind.VOICE_SESSION_STARTED,
                message="voice session started",
                payload={},
                component="voice_runtime",
            )
        return result

    async def stop_session(self) -> dict[str, Any]:
        return await self._conversation.stop()

    async def process(self, *, text: str = "") -> dict[str, Any]:
        return await self._conversation.handle_utterance(text=text)

    def snapshot(self) -> dict[str, Any]:
        return {
            "active": self._conversation.active,
            "turns": len(self._conversation._memory._turns),
            "voice_enabled": getattr(self._app.settings, "voice_enabled", False),
        }
