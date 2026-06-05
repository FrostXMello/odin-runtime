"""Agent profile snapshots."""

from __future__ import annotations

from typing import Any


def build_profile(identity: dict[str, Any], *, expertise: list[dict], performance: dict) -> dict[str, Any]:
    return {
        "agent_id": identity.get("agent_id"),
        "name": identity.get("name"),
        "role": identity.get("role"),
        "confidence": identity.get("confidence"),
        "expertise_domains": identity.get("expertise_domains", []),
        "expertise_records": expertise[-5:],
        "performance": performance,
        "status": identity.get("status"),
    }
