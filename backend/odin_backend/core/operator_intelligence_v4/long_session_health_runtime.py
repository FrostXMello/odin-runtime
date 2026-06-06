from __future__ import annotations


def health(*, hours: float) -> dict:
    return {"hours": hours, "healthy": hours < 6.0, "suggest_break": hours >= 6.0}
