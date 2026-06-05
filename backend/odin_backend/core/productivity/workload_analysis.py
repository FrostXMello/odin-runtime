"""Workload analysis."""

from __future__ import annotations

from typing import Any


def analyze_workload(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    open_tasks = [t for t in tasks if t.get("status") != "done"]
    return {"open": len(open_tasks), "total": len(tasks), "load": "high" if len(open_tasks) > 10 else "normal"}
