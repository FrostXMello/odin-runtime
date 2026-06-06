from __future__ import annotations
from typing import Any


def review_action(*, action: str, proposal_id: str) -> dict[str, Any]:
    if action not in ("approve", "reject", "revise"):
        return {"accepted": False, "reason": "invalid_action"}
    return {"accepted": True, "action": action, "proposal_id": proposal_id, "auto_commit": False}
