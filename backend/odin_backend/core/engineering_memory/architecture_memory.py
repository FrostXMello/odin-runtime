"""Architecture decision memory."""

from __future__ import annotations

from typing import Any


class ArchitectureMemory:
    def __init__(self) -> None:
        self._layers: dict[str, list[dict[str, Any]]] = {}

    def note(self, *, repo: str, layer: str, detail: str) -> dict[str, Any]:
        entry = {"repo": repo, "layer": layer, "detail": detail}
        self._layers.setdefault(repo, []).append(entry)
        return entry

    def snapshot(self, repo: str) -> list[dict[str, Any]]:
        return list(self._layers.get(repo, []))
