from __future__ import annotations


class OperatorBehaviorModel:
    def __init__(self) -> None:
        self._sessions = 0

    def observe(self) -> dict:
        self._sessions += 1
        return {"sessions": self._sessions}
