from __future__ import annotations


def metrics(*, ticks: int, memory_links: int) -> dict:
    return {"ticks": ticks, "memory_links": memory_links, "healthy": True}
