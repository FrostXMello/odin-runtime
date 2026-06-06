from __future__ import annotations


class ReasoningSnapshots:
    def __init__(self) -> None:
        self._snaps: list[dict] = []

    def capture(self, thought: str) -> dict:
        s = {"thought": thought[:120]}
        self._snaps.append(s)
        return s
