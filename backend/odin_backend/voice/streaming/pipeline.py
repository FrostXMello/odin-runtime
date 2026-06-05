"""Streaming voice pipeline — progressive STT/TTS with interruption."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from odin_backend.cognition.stream import CognitionStream
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.models.trace import TraceContext
from odin_backend.voice.sessions import VoiceSessionManager, VoiceSessionState
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class StreamingVoicePipeline:
    """Full-duplex style interaction with progressive output (push-to-talk)."""

    def __init__(
        self,
        voice: VoiceSessionManager,
        cognition: CognitionStream,
        event_bus: EventBus,
    ) -> None:
        self._voice = voice
        self._cognition = cognition
        self._event_bus = event_bus
        self._speech_queue: asyncio.Queue[str] = asyncio.Queue()
        self._interrupted = False

    async def stream_response(
        self,
        session_id: str,
        messages: list[str],
        *,
        trace: TraceContext | None = None,
    ) -> AsyncIterator[str]:
        """Yield progressive speech chunks while emitting cognition events."""
        self._interrupted = False
        session = self._voice.get_session(session_id)
        if session:
            session.state = VoiceSessionState.SPEAKING

        for msg in messages:
            if self._interrupted:
                await self._emit_interrupt(session_id)
                break
            await self._cognition.emit(msg, stage="voice.speaking", trace=trace)
            await self._voice.stream_cognition_chunk(session_id, msg)
            yield msg
            await asyncio.sleep(0.05)

        if session:
            session.state = VoiceSessionState.IDLE

    def interrupt(self, session_id: str) -> None:
        self._interrupted = True
        self._voice.interrupt(session_id)

    async def emit_partial_transcript(self, session_id: str, partial: str) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.VOICE_PARTIAL_TRANSCRIPT,
                source=AgentId.ODIN,
                payload={"session_id": session_id, "text": partial},
            )
        )

    async def _emit_interrupt(self, session_id: str) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.VOICE_INTERRUPTED,
                source=AgentId.ODIN,
                payload={"session_id": session_id},
            )
        )
