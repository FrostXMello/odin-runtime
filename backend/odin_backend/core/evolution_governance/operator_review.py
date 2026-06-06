from __future__ import annotations
from typing import Any

def review_packet(*, proposal: dict, risk: dict) -> dict[str, Any]:
    return {
        "why": proposal.get("rationale", "runtime bottleneck detected"),
        "expected_gains": proposal.get("expected_gain", "performance"),
        "expected_losses": "possible temporary regression",
        "risk": risk,
        "override_allowed": True,
    }
