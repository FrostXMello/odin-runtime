"""Execution success tracking."""

from __future__ import annotations

from typing import Any


def track_execution(*, total: int, success: int, avg_latency_ms: float) -> dict[str, Any]:
    return {"success_rate": round(success / max(total, 1), 4), "avg_latency_ms": avg_latency_ms}
