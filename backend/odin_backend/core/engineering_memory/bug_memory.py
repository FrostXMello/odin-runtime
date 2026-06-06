"""Bug and fix history."""

from __future__ import annotations

from typing import Any


class BugMemory:
    def __init__(self) -> None:
        self._bugs: list[dict[str, Any]] = []

    def record(self, *, repo: str, error: str, fixed: bool) -> dict[str, Any]:
        entry = {"repo": repo, "error": error[:500], "fixed": fixed, "failed_fixes": 0 if fixed else 1}
        self._bugs.append(entry)
        return entry

    def failed_fixes(self, *, repo: str, error_prefix: str) -> int:
        return sum(1 for b in self._bugs if b["repo"] == repo and not b["fixed"] and b["error"].startswith(error_prefix))

    def count(self) -> int:
        return len(self._bugs)
