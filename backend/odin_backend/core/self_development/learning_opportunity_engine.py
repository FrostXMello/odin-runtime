from __future__ import annotations

def opportunities(*, gaps: list[dict]) -> list[dict]:
    return [{"title": f"Improve {g['area']}", "priority": g.get("severity", "low")} for g in gaps]
