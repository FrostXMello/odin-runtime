from __future__ import annotations


def link_events(events: list[str]) -> list[dict]:
    return [{"a": events[i], "b": events[i + 1]} for i in range(max(0, len(events) - 1))]
