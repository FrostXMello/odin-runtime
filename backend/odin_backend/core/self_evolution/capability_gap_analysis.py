from __future__ import annotations
from typing import Any

def analyze(*, bottlenecks: list[dict], history: list[dict] | None = None) -> list[dict[str, Any]]:
    gaps = []
    for b in bottlenecks:
        gaps.append({"area": b["kind"], "impact": b.get("severity", "low"), "confidence": 0.75})
    if history:
        failed = [h for h in history if h.get("outcome") == "failed"]
        if len(failed) >= 2:
            gaps.append({"area": "repeated_failure", "impact": "high", "confidence": 0.85})
    return gaps
