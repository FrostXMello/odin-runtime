from __future__ import annotations

def propose_patch(*, title: str, plan: list[str]) -> dict:
    return {"title": title, "plan": plan, "approval_required": True, "auto_apply": False}
