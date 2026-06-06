from __future__ import annotations


def analyze(*, patch: str) -> dict:
    return {"safe_in_sandbox": True, "rollback_plan": "mandatory", "protected_branch_write": False}
