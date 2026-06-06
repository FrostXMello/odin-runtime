"""Personality continuity projection."""
from __future__ import annotations
from typing import Any

TRAITS = ("precise", "supportive", "curious")

def project(*, mode: str = "engineering") -> dict[str, Any]:
    return {"traits": list(TRAITS), "mode": mode, "stable": True}
