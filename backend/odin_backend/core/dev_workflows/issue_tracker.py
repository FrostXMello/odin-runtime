from __future__ import annotations

from typing import Any


class IssueTracker:
    def __init__(self) -> None:
        self._issues: list[dict[str, Any]] = []

    def add(self, *, title: str, blocked: bool, severity: str = "info") -> dict[str, Any]:
        issue = {"title": title, "blocked": blocked, "done": False, "severity": severity}
        self._issues.append(issue)
        return issue

    def completed(self) -> int:
        return sum(1 for i in self._issues if i.get("done"))

    def count(self) -> int:
        return sum(
            1
            for i in self._issues
            if not i.get("done") and i.get("severity") == "critical"
        )
