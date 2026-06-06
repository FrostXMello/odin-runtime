from __future__ import annotations


def execute_proposal(*, proposal_id: str) -> dict:
    return {"proposal_id": proposal_id, "executed": False, "approval_required": True}
