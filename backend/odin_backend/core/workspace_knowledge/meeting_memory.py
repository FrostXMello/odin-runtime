"""Meeting notes memory."""

from __future__ import annotations

from typing import Any


class MeetingMemory:
    def __init__(self) -> None:
        self._meetings: list[dict[str, Any]] = []

    def record(self, *, title: str, notes: str) -> dict[str, Any]:
        entry = {"title": title, "notes": notes[:1000]}
        self._meetings.append(entry)
        return entry
