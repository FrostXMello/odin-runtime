from __future__ import annotations


def prioritize(suggestions: list[dict]) -> list[dict]:
    return sorted(suggestions, key=lambda s: s.get("priority", 0), reverse=True)[:5]
