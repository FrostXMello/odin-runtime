from __future__ import annotations
from uuid import uuid4

def prepare(*, branch: str) -> dict:
    return {"rollback_id": str(uuid4()), "branch": branch, "mandatory": True, "plan": ["reset branch", "restore snapshot"]}
