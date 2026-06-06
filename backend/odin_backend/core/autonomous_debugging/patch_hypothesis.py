from __future__ import annotations


def hypothesize(*, cause: str, file: str) -> dict:
    return {"file": file, "hypothesis": f"guard {cause[:40]}", "auto_apply": False, "approval_required": True}
