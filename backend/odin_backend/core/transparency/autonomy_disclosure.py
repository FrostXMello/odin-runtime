from __future__ import annotations

def autonomy_status(*, mode: str) -> dict:
    return {"mode": mode, "approval_checkpoints": True, "unrestricted_autonomy": False}
