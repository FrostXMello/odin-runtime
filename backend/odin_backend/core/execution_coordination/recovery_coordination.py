from __future__ import annotations

from typing import Any


def recover_partial(*, workflow_id: str, completed: list[str]) -> dict[str, Any]:
    return {"workflow_id": workflow_id, "completed": completed, "recovered": True}
