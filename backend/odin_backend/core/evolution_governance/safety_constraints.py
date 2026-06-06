from __future__ import annotations

def check(*, direct_modify: bool, recursion_depth: int) -> dict:
    blocked = direct_modify or recursion_depth >= 3
    return {"allowed": not blocked, "blocked_reason": "unsafe" if blocked else None}
