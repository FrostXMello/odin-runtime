"""Detect hallucination risk in outputs."""

from __future__ import annotations

from typing import Any

RISK_MARKERS = ("definitely", "100%", "always works", "guaranteed", "cannot fail")


def assess_hallucination_risk(*, text: str, citations: list[str] | None = None) -> dict[str, Any]:
    citations = citations or []
    marker_hits = sum(1 for m in RISK_MARKERS if m in text.lower())
    uncited_claims = len(text.split(".")) - len(citations)
    risk = min(1.0, marker_hits * 0.15 + max(0, uncited_claims) * 0.02)
    return {"risk": round(risk, 3), "high_risk": risk > 0.5, "marker_hits": marker_hits}
