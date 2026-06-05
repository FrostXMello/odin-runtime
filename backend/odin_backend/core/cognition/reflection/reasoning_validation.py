"""Validate reasoning quality."""

from __future__ import annotations

from typing import Any


def hallucination_risk_score(text: str, *, grounding_size: int) -> float:
    """Higher score = more hallucination risk."""
    lower = text.lower()
    risk = 0.2
    if grounding_size < 50:
        risk += 0.25
    speculative = ("probably", "might", "assume", "guess", "likely")
    risk += min(0.3, sum(0.05 for w in speculative if w in lower))
    if "http://" in lower or "api key" in lower:
        risk += 0.1
    return min(0.99, risk)


def validate_strategy(plan_text: str, capability_stats: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    for cap, stats in capability_stats.items():
        if cap in plan_text and stats.get("failure_rate", 0) > 0.5:
            issues.append(f"high_failure_capability:{cap}")
    return {"valid": not issues, "issues": issues}
