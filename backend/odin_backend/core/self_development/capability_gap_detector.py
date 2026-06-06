from __future__ import annotations
from typing import Any

def detect_gaps(*, metrics: dict) -> list[dict[str, Any]]:
    gaps = []
    if metrics.get("latency_ms", 0) > 500:
        gaps.append({"area": "latency", "severity": "medium"})
    if metrics.get("error_rate", 0) > 0.05:
        gaps.append({"area": "reliability", "severity": "high"})
    return gaps
