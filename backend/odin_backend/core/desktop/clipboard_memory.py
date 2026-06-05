"""Privacy-filtered clipboard memory."""

from __future__ import annotations

from collections import deque
from typing import Any

_SENSITIVE = ("password", "token", "secret", "api_key", "credential")


class ClipboardMemory:
    def __init__(self, *, max_entries: int = 20) -> None:
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)

    def record(self, text: str) -> bool:
        lower = text.lower()
        if any(s in lower for s in _SENSITIVE):
            return False
        if len(text) > 2000:
            text = text[:2000] + "..."
        self._entries.append({"text": text, "length": len(text)})
        return True

    def recent(self) -> list[dict[str, Any]]:
        return list(self._entries)
