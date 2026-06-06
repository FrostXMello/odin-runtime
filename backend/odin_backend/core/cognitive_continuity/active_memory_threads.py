from __future__ import annotations

from typing import Any


class MemoryThreads:
    def __init__(self) -> None:
        self._threads: list[dict[str, Any]] = []

    def open(self, *, project: str, focus: str) -> dict[str, Any]:
        t = {"project": project, "focus": focus, "active": True}
        self._threads.append(t)
        return t

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._threads)
