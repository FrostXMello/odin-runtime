"""Operator focus tracking."""

from __future__ import annotations

from typing import Any


class AttentionModel:
    def __init__(self) -> None:
        self._focus_app: str | None = None
        self._focus_duration_s: float = 0

    def update(self, *, app: str, duration_s: float) -> dict[str, Any]:
        self._focus_app = app
        self._focus_duration_s = duration_s
        return {"app": app, "duration_s": duration_s, "deep_focus": duration_s > 300}
