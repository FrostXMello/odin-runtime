"""Resource negotiation between subsystems."""

from __future__ import annotations

from typing import Any


def negotiate(requests: list[dict[str, Any]], budget: float) -> list[dict[str, Any]]:
    total = sum(r.get("amount", 0) for r in requests) or 1.0
    return [{"subsystem": r.get("name"), "allocated": round(budget * r.get("amount", 0) / total, 4)} for r in requests]
