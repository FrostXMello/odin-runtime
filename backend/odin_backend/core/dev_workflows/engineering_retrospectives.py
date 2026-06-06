from __future__ import annotations

from typing import Any


def generate_retrospective(*, sprint: str, completed: int) -> dict[str, Any]:
    return {"sprint": sprint, "completed": completed, "learnings": ["maintain branch isolation", "validate patches in sandbox"]}
