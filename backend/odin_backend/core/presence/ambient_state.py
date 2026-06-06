"""Ambient presence state."""
from __future__ import annotations
from typing import Any

def ambient(*, idle_s: float) -> dict[str, Any]:
    return {"idle": idle_s > 120, "presence": "background" if idle_s > 120 else "active"}
