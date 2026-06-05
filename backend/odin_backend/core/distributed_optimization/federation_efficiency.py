"""Federation efficiency metrics."""

from __future__ import annotations

from typing import Any


def measure(*, successful: int, total: int, avg_latency: float) -> dict[str, Any]:
    rate = successful / max(total, 1)
    return {"success_rate": round(rate, 4), "avg_latency_ms": avg_latency, "efficiency": round(rate / max(avg_latency / 100, 0.1), 4)}
