from __future__ import annotations
from typing import Any
from uuid import uuid4

def plan(*, goal: str, files: list[str]) -> dict[str, Any]:
    return {"plan_id": str(uuid4()), "goal": goal[:200], "files": files[:20], "isolated_branch": True}
