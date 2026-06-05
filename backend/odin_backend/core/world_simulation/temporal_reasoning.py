"""Temporal reasoning over world timelines."""

from __future__ import annotations

from typing import Any


def analyze_timeline(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {"trend": "stable", "confidence": 0.5}
    confidences = [e.get("confidence", 0.5) for e in events]
    avg = sum(confidences) / len(confidences)
    trend = "improving" if confidences[-1] > confidences[0] else "declining" if confidences[-1] < confidences[0] else "stable"
    return {"trend": trend, "confidence": round(avg, 4), "event_count": len(events)}
