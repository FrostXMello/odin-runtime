from __future__ import annotations

def rehydrate(*, snapshot: dict) -> dict:
    return {"rehydrated": bool(snapshot), "keys": list(snapshot.keys())[:15]}
