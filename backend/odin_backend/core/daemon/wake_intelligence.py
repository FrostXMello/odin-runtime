from __future__ import annotations

def wake(*, wakeword: str = "", energy: float = 0.5) -> dict:
    triggered = energy > 0.55 or wakeword.lower() in ("odin", "hey odin")
    return {"triggered": triggered, "wakeword": wakeword[:32], "local_only": True}
