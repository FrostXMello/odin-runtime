"""Recovery report generation."""

from __future__ import annotations

from typing import Any


def build_recovery_report(*, guardian: dict, healing: dict, daemon: dict) -> dict[str, Any]:
    return {
        "guardian": guardian,
        "healing": healing,
        "daemon": daemon,
        "status": "healthy" if not guardian.get("degraded") else "degraded",
    }
