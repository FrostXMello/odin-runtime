from __future__ import annotations


class EngineeringSessions:
    def __init__(self) -> None:
        self._sessions: list[dict] = []

    def start(self, repo: str) -> dict:
        s = {"repo": repo, "active": True}
        self._sessions.append(s)
        return s
