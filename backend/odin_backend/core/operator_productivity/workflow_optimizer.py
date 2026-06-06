from __future__ import annotations
from typing import Any


def optimize(*, bottlenecks: list[str]) -> dict[str, Any]:
    return {"suggestions": bottlenecks[:3], "approval_required": True}
