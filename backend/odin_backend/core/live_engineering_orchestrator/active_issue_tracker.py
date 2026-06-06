from __future__ import annotations
from typing import Any


class ActiveIssueTracker:
    def __init__(self) -> None:
        self._issues: list[dict] = []

    def track(self, *, title: str, blocked: bool = False) -> dict[str, Any]:
        item = {"title": title[:120], "blocked": blocked, "open": True}
        self._issues.append(item)
        return item

    def open_issues(self) -> list[dict]:
        return [i for i in self._issues if i.get("open")]
