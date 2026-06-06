from __future__ import annotations

class TerminalMemory:
    def __init__(self) -> None:
        self._lines: list[str] = []

    def remember(self, line: str) -> None:
        self._lines.append(line[:200])
        self._lines = self._lines[-50:]

    def snapshot(self) -> list[str]:
        return self._lines[-10:]
