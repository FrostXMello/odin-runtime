"""Patch outcome history."""

from __future__ import annotations

from typing import Any


class PatchHistory:
    def __init__(self) -> None:
        self._patches: list[dict[str, Any]] = []

    def record(self, *, repo: str, patch_id: str, outcome: str) -> dict[str, Any]:
        entry = {"repo": repo, "patch_id": patch_id, "outcome": outcome}
        self._patches.append(entry)
        return entry

    def count(self) -> int:
        return len(self._patches)
