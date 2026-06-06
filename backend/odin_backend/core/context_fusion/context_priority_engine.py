from __future__ import annotations

from typing import Any


def prioritize(*, context: dict, focus: dict) -> dict[str, Any]:
    score = 0.4 + len(context.get("sources", [])) * 0.15 + focus.get("intensity", 0) * 0.3
    return {"score": round(min(1.0, score), 3)}
