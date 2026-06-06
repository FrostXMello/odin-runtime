from __future__ import annotations


def lifecycle(*, patch: str) -> dict:
    return {"patch": patch[:120], "branch": "sandbox", "approval_required": True, "protected_branch_write": False}
