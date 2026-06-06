from __future__ import annotations

from typing import Any


class ConversationContext:
    def __init__(self) -> None:
        self._turns = 0

    def update(self, context: dict) -> dict[str, Any]:
        self._turns += 1
        return {"turns": self._turns, "persisted": True}

    def turns(self) -> int:
        return self._turns
