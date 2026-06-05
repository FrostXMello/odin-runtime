"""Adaptive context truncation."""

from __future__ import annotations

from typing import Any


def truncate_context(messages: list[dict], *, max_tokens: int = 4096, chars_per_token: int = 4) -> list[dict]:
    budget = max_tokens * chars_per_token
    out: list[dict] = []
    used = 0
    for msg in reversed(messages):
        content = str(msg.get("content", ""))
        if used + len(content) > budget:
            remaining = budget - used
            if remaining > 100:
                out.insert(0, {**msg, "content": content[-remaining:]})
            break
        out.insert(0, msg)
        used += len(content)
    return out or messages[-1:]
