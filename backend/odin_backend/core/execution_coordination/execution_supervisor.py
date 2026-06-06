from __future__ import annotations

from typing import Any


def supervise(*, workflow_id: str, step: str) -> dict[str, Any]:
    return {"workflow_id": workflow_id, "step": step, "supervised": True}
