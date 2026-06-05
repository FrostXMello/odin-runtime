"""Voice session management — push-to-talk, streaming chunks, interrupt support."""

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.voice.stt.whisper_stt import WhisperSTT
from odin_backend.voice.tts.piper_tts import PiperTTS
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class VoiceSessionState(StrEnum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class VoiceSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    state: VoiceSessionState = VoiceSessionState.IDLE
    push_to_talk: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transcript: str = ""


class VoiceSessionManager:
    """Push-to-talk only — no wake word, no always-listening."""

    def __init__(self, settings: Settings, event_bus: EventBus) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._stt = WhisperSTT(settings.whisper_model)
        self._tts = PiperTTS(settings.piper_voice_path)
        self._sessions: dict[str, VoiceSession] = {}
        self._audio_dir = Path("./data/voice")
        self._audio_dir.mkdir(parents=True, exist_ok=True)

    @property
    def enabled(self) -> bool:
        return self._settings.voice_enabled

    async def start_session(self, *, push_to_talk: bool = True) -> VoiceSession:
        session = VoiceSession(push_to_talk=push_to_talk)
        session.state = VoiceSessionState.LISTENING if push_to_talk else VoiceSessionState.IDLE
        self._sessions[session.id] = session
        await self._event_bus.publish(
            Event(
                type=EventType.VOICE_SESSION_STARTED,
                source=AgentId.ODIN,
                payload=session.model_dump(mode="json"),
            )
        )
        return session

    async def stream_cognition_chunk(self, session_id: str, message: str) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.VOICE_CHUNK,
                source=AgentId.ODIN,
                payload={"session_id": session_id, "message": message, "type": "cognition"},
            )
        )

    async def process_audio(self, session_id: str, audio_path: Path) -> str:
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Unknown voice session")
        session.state = VoiceSessionState.PROCESSING
        text = await self._stt.transcribe(audio_path)
        session.transcript = text
        session.state = VoiceSessionState.IDLE
        return text

    async def speak(self, session_id: str, text: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.state = VoiceSessionState.SPEAKING
        out = self._audio_dir / f"{session_id}.wav"
        ok = await self._tts.synthesize(text, out)
        session.state = VoiceSessionState.IDLE
        await self.stream_cognition_chunk(session_id, text)
        return ok

    def interrupt(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.state = VoiceSessionState.IDLE

    def get_session(self, session_id: str) -> VoiceSession | None:
        return self._sessions.get(session_id)
