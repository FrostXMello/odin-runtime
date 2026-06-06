"""Interaction state tracking."""

from __future__ import annotations

from typing import Any


class InteractionState:
    def __init__(self) -> None:
        self._mode = "assistant"
        self._last_action = ""

    def set_mode(self, mode: str) -> dict[str, Any]:
        allowed = {"assistant", "engineering", "passive", "collaborative"}
        if mode not in allowed:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        return {"accepted": True, "mode": mode}

    def record_action(self, action: str) -> None:
        self._last_action = action

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "last_action": self._last_action}
