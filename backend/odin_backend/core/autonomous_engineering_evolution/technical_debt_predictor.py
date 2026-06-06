from __future__ import annotations


def predict_debt(*, churn: int) -> dict:
    risk = min(1.0, churn / 100.0)
    return {"risk": risk, "debt_likely": risk > 0.5}
