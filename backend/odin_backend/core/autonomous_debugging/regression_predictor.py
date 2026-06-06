from __future__ import annotations


def predict(*, diff_size: int, tests_touched: int) -> dict:
    risk = min(1.0, diff_size / 500 + tests_touched / 20)
    return {"risk": round(risk, 3), "regression_likely": risk > 0.6}
