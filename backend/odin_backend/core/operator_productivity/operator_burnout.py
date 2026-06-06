from __future__ import annotations


def risk(*, session_hours: float) -> dict:
    return {"burnout_risk": session_hours > 10, "hours": session_hours}
