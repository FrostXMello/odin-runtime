"""Degraded operation mode management."""

from __future__ import annotations

from typing import Any


MODES = ("normal", "degraded", "minimal", "emergency")


def activate_degraded(*, reason: str, level: str = "degraded") -> dict[str, Any]:
    return {
        "mode": level if level in MODES else "degraded",
        "reason": reason,
        "cognition_depth": 1 if level == "emergency" else 2,
        "max_concurrent": 1 if level in ("minimal", "emergency") else 2,
        "streaming_enabled": level not in ("emergency",),
    }
