from __future__ import annotations
from typing import Any
from uuid import uuid4

def propose(*, title: str, rationale: str, expected_gain: str, risk: str = "medium") -> dict[str, Any]:
    return {
        "proposal_id": str(uuid4()),
        "title": title[:200],
        "rationale": rationale[:500],
        "expected_gain": expected_gain,
        "risk": risk,
        "approval_level": "proposal_only",
        "no_main_commit": True,
    }
