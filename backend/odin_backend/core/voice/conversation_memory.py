"""Voice conversation continuity."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any


class ConversationMemory:
    def __init__(self, *, max_turns: int = 40) -> None:
        self._turns: deque[dict[str, Any]] = deque(maxlen=max_turns)

    def add(self, role: str, content: str) -> None:
        self._turns.append(
            {"role": role, "content": content[:2000], "timestamp": datetime.now(timezone.utc).isoformat()}
        )

    def context_messages(self) -> list[dict[str, str]]:
        return [{"role": t["role"], "content": t["content"]} for t in self._turns]
