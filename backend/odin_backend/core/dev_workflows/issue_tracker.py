from __future__ import annotations

from typing import Any


class IssueTracker:
    def __init__(self) -> None:
        self._issues: list[dict[str, Any]] = []

    def add(self, *, title: str, blocked: bool) -> dict[str, Any]:
        issue = {"title": title, "blocked": blocked, "done": False}
        self._issues.append(issue)
        return issue

    def completed(self) -> int:
        return sum(1 for i in self._issues if i.get("done"))

    def count(self) -> int:
        return len(self._issues)
