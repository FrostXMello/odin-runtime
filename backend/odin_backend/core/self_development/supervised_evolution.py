from __future__ import annotations

def evolve(*, proposal: dict) -> dict:
    return {"accepted": False, "approval_required": True, "proposal": proposal, "direct_modification": False}
