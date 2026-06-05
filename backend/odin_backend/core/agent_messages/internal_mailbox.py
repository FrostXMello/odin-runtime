"""Per-agent mailboxes."""

from __future__ import annotations

from collections import deque
from typing import Any


class InternalMailbox:
    def __init__(self, *, max_messages: int = 50) -> None:
        self._boxes: dict[str, deque[dict[str, Any]]] = {}
        self._max = max_messages

    def deliver(self, agent_id: str, message: dict[str, Any]) -> None:
        box = self._boxes.setdefault(agent_id, deque(maxlen=self._max))
        box.append(message)

    def inbox(self, agent_id: str) -> list[dict[str, Any]]:
        return list(self._boxes.get(agent_id, []))
