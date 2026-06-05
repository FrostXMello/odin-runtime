"""Shared reasoning context between human and operator."""

from __future__ import annotations

from typing import Any


class SharedContext:
    def __init__(self) -> None:
        self._notes: list[dict[str, Any]] = []
        self._focus: str = ""

    def set_focus(self, topic: str) -> None:
        self._focus = topic[:500]

    def add_note(self, *, author: str, content: str) -> None:
        self._notes.append({"author": author, "content": content[:2000]})
        if len(self._notes) > 50:
            self._notes = self._notes[-50:]

    def snapshot(self) -> dict[str, Any]:
        return {"focus": self._focus, "notes": list(self._notes)[-10:]}
