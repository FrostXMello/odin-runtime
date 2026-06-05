"""Execution outcome analysis."""

from __future__ import annotations

from typing import Any


def analyze_outcomes(events: list[dict[str, Any]]) -> dict[str, Any]:
    successes = sum(1 for e in events if e.get("success"))
    failures = len(events) - successes
    retries = sum(1 for e in events if e.get("event") == "retry" or "retry" in str(e.get("reason", "")))
    latencies = [float(e["latency_ms"]) for e in events if e.get("latency_ms")]
    return {
        "total": len(events),
        "successes": successes,
        "failures": failures,
        "retry_count": retries,
        "success_rate": successes / len(events) if events else 0.0,
        "avg_latency_ms": sum(latencies) / len(latencies) if latencies else None,
    }
