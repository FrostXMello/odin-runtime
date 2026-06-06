from __future__ import annotations


def tokenize_stream(text: str, *, chunk: int = 8) -> list[str]:
    words = text.split()
    return [" ".join(words[i : i + chunk]) for i in range(0, max(len(words), 1), chunk)] or [text]
