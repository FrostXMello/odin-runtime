"""Resource and economic reasoning."""

from __future__ import annotations

from typing import Any


def balance_resources(resources: dict[str, float]) -> dict[str, Any]:
    total = sum(resources.values()) or 1.0
    allocation = {k: round(v / total, 4) for k, v in resources.items()}
    return {"allocation": allocation, "total": total, "balanced": True}
