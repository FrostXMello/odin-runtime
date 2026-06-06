from __future__ import annotations


def continue_goal(*, goal: str) -> dict:
    return {"goal": goal[:120], "resumable": True, "approval_required": True}
