from __future__ import annotations

def emotional_tts(*, text: str, mood: str = "neutral") -> dict:
    return {"text": text[:500], "mood": mood, "local_only": True, "simulated_emotion": True}
