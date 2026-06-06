from __future__ import annotations

def interrupt(*, reason: str = "operator") -> dict:
    return {"interrupted": True, "reason": reason[:80], "recovery": True}
