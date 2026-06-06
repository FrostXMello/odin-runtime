from __future__ import annotations


def replay(items: list[str]) -> list[dict]:
    return [{"item": i[:60]} for i in items[-6:]]
