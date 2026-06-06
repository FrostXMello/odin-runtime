from __future__ import annotations


class OperatorState:
    def __init__(self) -> None:
        self._focus = "workspace"
        self._sessions = 0

    def shift(self, focus: str) -> dict:
        self._focus = focus[:80]
        self._sessions += 1
        return {"focus": self._focus, "sessions": self._sessions}
