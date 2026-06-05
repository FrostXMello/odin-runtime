"""Hallucination scoring."""

from __future__ import annotations

from typing import Any


def score_hallucination(*, claims: int, supported: int) -> dict[str, Any]:
    rate = 1 - (supported / max(claims, 1))
    return {"hallucination_rate": round(rate, 4), "claims": claims, "supported": supported}
