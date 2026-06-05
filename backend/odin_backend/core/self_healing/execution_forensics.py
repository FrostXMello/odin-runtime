"""Forensic execution analysis."""

from __future__ import annotations

from typing import Any


def analyze_lineage(executions: list[dict[str, Any]]) -> dict[str, Any]:
    if not executions:
        return {"nodes": 0, "failures": 0, "branches": 0}
    failures = sum(1 for e in executions if e.get("state") == "failed")
    missions = {e.get("mission_id") for e in executions if e.get("mission_id")}
    return {
        "nodes": len(executions),
        "failures": failures,
        "branches": len(missions),
        "failure_rate": failures / max(len(executions), 1),
    }
