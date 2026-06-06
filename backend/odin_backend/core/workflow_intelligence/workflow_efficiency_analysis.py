from __future__ import annotations

from typing import Any


def analyze_efficiency(*, session_hours: float) -> dict[str, Any]:
    drop = session_hours > 3.0
    return {"session_hours": session_hours, "focus_drop": drop, "recommend_break": drop}
