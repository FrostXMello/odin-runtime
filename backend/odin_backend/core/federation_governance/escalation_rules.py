"""Governance escalation rules."""

from __future__ import annotations

from typing import Any


def should_escalate(*, trust: float, violation_count: int) -> dict[str, Any]:
    if violation_count >= 3 or trust < 0.2:
        return {"escalate": True, "action": "quarantine"}
    if violation_count >= 1:
        return {"escalate": True, "action": "warn"}
    return {"escalate": False, "action": "none"}
