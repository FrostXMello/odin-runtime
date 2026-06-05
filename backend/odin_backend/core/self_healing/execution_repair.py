"""Execution repair helpers."""

from __future__ import annotations

from typing import Any


def repair_execution(execution: dict[str, Any]) -> dict[str, Any]:
    state = execution.get("state", "unknown")
    if state in ("running", "queued"):
        return {"action": "retry", "execution_id": execution.get("execution_id")}
    if state == "failed":
        return {"action": "salvage", "execution_id": execution.get("execution_id")}
    return {"action": "none", "execution_id": execution.get("execution_id")}
