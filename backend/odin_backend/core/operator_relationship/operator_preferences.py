"""Operator preference tracking."""

from __future__ import annotations

from typing import Any


class OperatorPreferences:
    def __init__(self) -> None:
        self._prefs: dict[str, Any] = {
            "explanation_depth": "medium",
            "response_style": "concise",
            "intervention_timing": "on_request",
        }

    def update(self, **kwargs: Any) -> dict[str, Any]:
        self._prefs.update(kwargs)
        return dict(self._prefs)

    def get(self) -> dict[str, Any]:
        return dict(self._prefs)
