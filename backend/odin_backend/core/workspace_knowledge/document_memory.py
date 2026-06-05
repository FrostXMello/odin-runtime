"""Document memory store."""

from __future__ import annotations

from typing import Any


class DocumentMemory:
    def __init__(self) -> None:
        self._docs: list[dict[str, Any]] = []

    def store(self, *, title: str, content: str, kind: str = "note") -> dict[str, Any]:
        entry = {"title": title, "content": content[:2000], "kind": kind}
        self._docs.append(entry)
        return entry

    def list_all(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._docs[-limit:]
