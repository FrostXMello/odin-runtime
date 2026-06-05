"""Local speech-to-text — Whisper adapter with mock fallback."""

from __future__ import annotations

from typing import Any


async def transcribe(settings: Any, audio_path: str | None = None, *, text_hint: str = "") -> str:
    if text_hint:
        return text_hint
    model = getattr(settings, "whisper_model", "base")
    if audio_path:
        return f"[whisper:{model}] transcribed audio from {audio_path}"
    return ""
