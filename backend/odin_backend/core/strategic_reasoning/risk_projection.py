"""Risk projection with uncertainty."""

from __future__ import annotations

from typing import Any


def project_risk(*, likelihood: float, impact: float) -> dict[str, Any]:
    score = likelihood * impact
    level = "high" if score > 0.6 else "medium" if score > 0.3 else "low"
    return {
        "risk_score": round(score, 4),
        "level": level,
        "likelihood": likelihood,
        "impact": impact,
        "uncertainty": round(1.0 - likelihood, 4),
    }
