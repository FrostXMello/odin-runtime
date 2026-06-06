from __future__ import annotations


def evolve(*, churn: int) -> dict:
    return {"churn": churn, "debt_trend": "rising" if churn > 20 else "stable"}
