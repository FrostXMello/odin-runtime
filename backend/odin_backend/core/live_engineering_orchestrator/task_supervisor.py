from __future__ import annotations
from typing import Any


def supervise(*, tasks: list[str]) -> dict[str, Any]:
    return {"tasks": tasks[:12], "approval_required": True, "auto_patch": False}
