"""Realtime voice conversation loop."""

from __future__ import annotations

from typing import Any

from odin_backend.core.voice.conversation_memory import ConversationMemory
from odin_backend.core.voice.interruption_manager import InterruptionManager
from odin_backend.core.voice.speech_to_text import transcribe
from odin_backend.core.voice.text_to_speech import synthesize


class RealtimeConversation:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = ConversationMemory()
        self._interrupt = InterruptionManager()
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    async def start(self) -> dict[str, Any]:
        self._active = True
        return {"status": "started"}

    async def stop(self) -> dict[str, Any]:
        self._active = False
        return {"status": "stopped", "turns": len(self._memory._turns)}

    async def handle_utterance(self, *, text: str = "", audio_path: str | None = None) -> dict[str, Any]:
        if self._interrupt.interrupted:
            self._interrupt.clear()
            return {"interrupted": True}
        transcript = await transcribe(self._app.settings, audio_path, text_hint=text)
        self._memory.add("user", transcript)
        response = await self._respond(transcript)
        self._memory.add("assistant", response)
        tts = await synthesize(self._app.settings, response)
        return {"transcript": transcript, "response": response, "tts": tts}

    async def _respond(self, user_text: str) -> str:
        ctx = ""
        if hasattr(self._app, "multimodal_perception"):
            ctx = self._app.multimodal_perception._context.prompt_block()
        messages = self._memory.context_messages()[-6:]
        messages.append(
            {
                "role": "user",
                "content": f"Workspace context: {ctx}\n\nUser: {user_text}",
            }
        )
        if hasattr(self._app, "model_manager"):
            return str(
                await self._app.model_manager.runtime.infer(
                    messages=messages,
                    task_kind="synthesis",
                )
            )
        return f"I heard: {user_text[:120]}"
