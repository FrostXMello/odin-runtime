from __future__ import annotations

def prioritize(threads: list[dict]) -> list[dict]:
    return sorted(threads, key=lambda t: t.get("weight", 0), reverse=True)
