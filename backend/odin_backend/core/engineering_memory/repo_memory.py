"""Repository structure memory."""

from __future__ import annotations

from typing import Any


class RepoMemory:
    def __init__(self) -> None:
        self._entries: dict[str, dict[str, Any]] = {}

    def remember(self, *, repo: str, structure: dict[str, Any]) -> dict[str, Any]:
        entry = {"repo": repo, "structure": structure, "version": len(self._entries.get(repo, {}).get("history", [])) + 1}
        hist = self._entries.setdefault(repo, {"history": []})
        hist["history"].append(entry)
        hist["latest"] = entry
        return entry

    def latest(self, repo: str) -> dict[str, Any] | None:
        return self._entries.get(repo, {}).get("latest")

    def count(self) -> int:
        return len(self._entries)
