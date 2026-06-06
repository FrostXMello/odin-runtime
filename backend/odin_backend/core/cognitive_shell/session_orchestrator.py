"""Session orchestration for cognitive shell."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


def start_session(*, operator_id: str = "default") -> dict[str, Any]:
    return {"session_id": str(uuid4()), "operator_id": operator_id, "turns": 0}


def merge_session(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    merged.update(update)
    merged["turns"] = merged.get("turns", 0) + update.get("turn_delta", 0)
    return merged
