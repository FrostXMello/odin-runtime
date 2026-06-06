from __future__ import annotations

class ConvMemory:
    def __init__(self) -> None:
        self._turns: list[dict] = []

    def add(self, role: str, content: str) -> None:
        self._turns.append({"role": role, "content": content[:2000]})

    def context(self, limit: int = 8) -> list[dict]:
        return self._turns[-limit:]
