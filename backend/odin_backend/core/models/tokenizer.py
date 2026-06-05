"""Lightweight token estimation for local context budgeting."""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Approximate token count without loading a tokenizer."""
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    return max(words, chars // 4)


def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
    total = 0
    for msg in messages:
        total += estimate_tokens(msg.get("content", "")) + 4
    return total
