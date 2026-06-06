from __future__ import annotations

from typing import Any
from uuid import uuid4


def plan_patch(*, goal: str, files: list[str]) -> dict[str, Any]:
    return {"plan_id": str(uuid4()), "goal": goal, "files": files, "steps": ["analyze", "edit", "test"]}
