"""Detect runtime bottlenecks from metrics."""
from __future__ import annotations
from typing import Any

def detect(*, metrics: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict] = []
    if metrics.get("latency_ms", 0) > 400:
        out.append({"kind": "latency", "severity": "high", "value": metrics["latency_ms"]})
    if metrics.get("error_rate", 0) > 0.03:
        out.append({"kind": "errors", "severity": "high", "value": metrics["error_rate"]})
    if metrics.get("memory_mb", 0) > 12000:
        out.append({"kind": "memory", "severity": "medium", "value": metrics["memory_mb"]})
    if metrics.get("agent_queue", 0) > 10:
        out.append({"kind": "agent_coordination", "severity": "medium", "value": metrics["agent_queue"]})
    return out
