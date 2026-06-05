"""Operator workflow profiles for continuous assistant."""

from __future__ import annotations

from typing import Any


DEFAULT_PROFILES = {
    "developer": {"proactive": True, "focus_aware": True, "coding_priority": 0.9},
    "researcher": {"proactive": False, "focus_aware": True, "coding_priority": 0.3},
    "balanced": {"proactive": True, "focus_aware": True, "coding_priority": 0.6},
}


class OperatorWorkflowProfiles:
    def __init__(self) -> None:
        self._active = "balanced"
        self._custom: dict[str, dict[str, Any]] = {}

    def set_profile(self, name: str) -> dict[str, Any]:
        self._active = name
        return self.get()

    def get(self) -> dict[str, Any]:
        if self._active in self._custom:
            return self._custom[self._active]
        return dict(DEFAULT_PROFILES.get(self._active, DEFAULT_PROFILES["balanced"]))

    def adapt(self, *, actions: list[str]) -> dict[str, Any]:
        coding = sum(1 for a in actions if any(k in a.lower() for k in ("code", "git", "debug")))
        if coding > 5:
            return DEFAULT_PROFILES["developer"]
        return self.get()
