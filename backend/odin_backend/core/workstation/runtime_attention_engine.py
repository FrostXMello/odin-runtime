from __future__ import annotations

from typing import Any


def compute_attention(*, app: str, duration_s: float) -> dict[str, Any]:
    weight = min(1.0, duration_s / 300)
    return {"app": app, "weight": round(weight, 3)}
