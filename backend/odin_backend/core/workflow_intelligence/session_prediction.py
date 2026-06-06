from __future__ import annotations

from typing import Any


def predict_session(*, history: list[str]) -> dict[str, Any]:
    nxt = history[-1] if history else "explore"
    return {"next": nxt, "confidence": 0.6 if history else 0.3}
