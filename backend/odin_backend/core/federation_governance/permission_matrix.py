"""Federation permission levels."""

from __future__ import annotations

LEVELS = ("none", "read", "reason", "delegate", "admin")


def check_permission(level: str, action: str) -> bool:
    idx = LEVELS.index(level) if level in LEVELS else 0
    required = {"read": 1, "reason": 2, "delegate": 3, "quarantine": 4, "admin": 4}
    return idx >= required.get(action, 99)
