"""GitHub read-only runtime."""

from __future__ import annotations

from typing import Any


class GitHubRuntime:
    def __init__(self) -> None:
        self._repos: list[dict[str, Any]] = []

    def observe_repo(self, *, owner: str, name: str) -> dict[str, Any]:
        entry = {"owner": owner, "name": name, "read_only": True}
        self._repos.append(entry)
        return entry

    def snapshot(self) -> dict[str, Any]:
        return {"repos": self._repos[-20:]}
