"""Hallucination pattern detection."""

from __future__ import annotations

from typing import Any


def review(*, claims: list[str], evidence: list[str]) -> dict[str, Any]:
    unsupported = max(0, len(claims) - len(evidence))
    detected = unsupported > len(claims) * 0.3
    return {"hallucination_risk": detected, "unsupported_claims": unsupported, "total_claims": len(claims)}
