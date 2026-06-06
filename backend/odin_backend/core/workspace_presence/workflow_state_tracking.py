from __future__ import annotations

def track(*, state: str) -> dict:
    return {"state": state, "ts": __import__("time").time()}
