from __future__ import annotations

LEVELS = ("observe_only", "proposal_only", "supervised_apply", "supervised_merge")

def score(*, touches_core: bool, regression_risk: float) -> dict:
    risk = 0.2
    if touches_core:
        risk += 0.4
    risk += regression_risk * 0.4
    level = "proposal_only"
    if risk > 0.7:
        level = "observe_only"
    elif risk < 0.35:
        level = "supervised_apply"
    return {"risk": round(min(1.0, risk), 3), "recommended_level": level}
