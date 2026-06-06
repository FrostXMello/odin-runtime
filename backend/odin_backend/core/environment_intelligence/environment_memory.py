from __future__ import annotations


class EnvironmentMemory:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def remember(self, entry: dict) -> None:
        self._entries.append(entry)

    def recent(self) -> list[dict]:
        return self._entries[-16:]
