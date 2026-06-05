"""Local text-to-speech — Piper adapter stub."""

from __future__ import annotations

from typing import Any


async def synthesize(settings: Any, text: str) -> dict[str, Any]:
    voice = getattr(settings, "piper_voice_path", None) or "default"
    return {"voice": voice, "text_length": len(text), "audio_path": None, "stub": True}
