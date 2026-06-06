from __future__ import annotations

def suggest(*, file: str, issue: str) -> dict:
    return {"file": file, "issue": issue[:120], "approval_required": True, "no_main_commit": True}
