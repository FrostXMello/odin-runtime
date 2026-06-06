from __future__ import annotations

from typing import Any


def generate_rollback(*, plan_id: str) -> dict[str, Any]:
    return {"plan_id": plan_id, "rollback_steps": ["git stash", "git checkout -- .", "restore branch"], "mandatory": True}
