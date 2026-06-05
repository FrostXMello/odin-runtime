"""Optional wake-word detection stub."""

from __future__ import annotations


class WakewordDetector:
    def __init__(self, *, enabled: bool = False) -> None:
        self._enabled = enabled

    def check(self, transcript: str) -> bool:
        if not self._enabled:
            return False
        return "odin" in transcript.lower()
