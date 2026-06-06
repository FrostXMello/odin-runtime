from __future__ import annotations


class ArchitectureMemory:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def remember(self, component: str, note: str) -> dict:
        e = {"component": component, "note": note[:120]}
        self._entries.append(e)
        return e
