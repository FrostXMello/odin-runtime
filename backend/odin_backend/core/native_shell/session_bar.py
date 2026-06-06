from __future__ import annotations

def bar(*, missions: int = 0, status: str = "ready") -> dict:
    return {"missions": missions, "status": status, "cognitive_online": True}
