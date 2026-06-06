from __future__ import annotations


def compress(thoughts: list[str], *, max_items: int = 8) -> list[str]:
    return thoughts[-max_items:]
