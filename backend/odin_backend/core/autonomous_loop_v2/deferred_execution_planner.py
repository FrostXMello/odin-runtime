from __future__ import annotations


def plan(*, task: str) -> dict:
    return {"task": task[:120], "deferred": True, "execution_approval_required": True}
