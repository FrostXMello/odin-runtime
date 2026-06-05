"""Token accounting for local inference."""

from __future__ import annotations

from typing import Any


class TokenAccounting:
    def __init__(self) -> None:
        self._usage: dict[str, int] = {"prompt": 0, "completion": 0}

    def record(self, *, prompt_tokens: int, completion_tokens: int) -> dict[str, int]:
        self._usage["prompt"] += prompt_tokens
        self._usage["completion"] += completion_tokens
        return dict(self._usage)

    def estimate_chars(self, text: str) -> int:
        return max(1, len(text) // 4)

    def snapshot(self) -> dict[str, Any]:
        return {"usage": dict(self._usage), "total": self._usage["prompt"] + self._usage["completion"]}
