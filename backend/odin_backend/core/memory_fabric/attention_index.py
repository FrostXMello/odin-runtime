from __future__ import annotations


def index(items: list[str], *, weight: float = 0.5) -> list[dict]:
    return [{"item": i[:60], "weight": weight} for i in items[:12]]
