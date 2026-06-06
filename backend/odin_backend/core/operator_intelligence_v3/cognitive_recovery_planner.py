from __future__ import annotations


def plan(*, fatigue: bool) -> dict:
    return {"recovery": fatigue, "suggest_break": fatigue, "local_only": True}
