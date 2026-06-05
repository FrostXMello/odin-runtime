"""Weighted confidence voting."""

from __future__ import annotations

from typing import Any


def reach_consensus(votes: list[dict[str, Any]]) -> dict[str, Any]:
    if not votes:
        return {"consensus": False, "confidence": 0.0}
    total_w = sum(float(v.get("weight", 1.0)) for v in votes)
    approve_w = sum(float(v.get("weight", 1.0)) for v in votes if v.get("approve"))
    confidence = approve_w / max(total_w, 1e-6)
    return {"consensus": confidence >= 0.6, "confidence": round(confidence, 3), "votes": len(votes)}
