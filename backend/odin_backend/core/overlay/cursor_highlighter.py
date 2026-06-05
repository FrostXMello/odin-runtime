"""Cursor highlight state."""

from __future__ import annotations

from typing import Any


class CursorHighlighter:
    def __init__(self) -> None:
        self._position: dict[str, int] | None = None

    def set(self, *, x: int, y: int) -> None:
        self._position = {"x": x, "y": y}

    def snapshot(self) -> dict[str, Any] | None:
        return self._position
