from __future__ import annotations


def energy_level(*, focus_minutes: int) -> str:
    if focus_minutes > 90:
        return "low"
    if focus_minutes > 45:
        return "medium"
    return "high"
