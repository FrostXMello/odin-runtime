from __future__ import annotations

def execution_panel(*, workflow_id: str, step: str) -> dict:
    return {"workflow_id": workflow_id, "step": step, "approval_required": True}
