"""Cross-node weighted consensus."""

from __future__ import annotations

from typing import Any


def reach_cross_node_consensus(votes: list[dict[str, Any]]) -> dict[str, Any]:
    if not votes:
        return {"consensus": False, "reason": "no_votes"}
    weighted = sum(v.get("confidence", 0.5) * v.get("trust", 0.5) for v in votes)
    avg = weighted / len(votes)
    winner = max(votes, key=lambda v: v.get("confidence", 0) * v.get("trust", 0.5))
    return {
        "consensus": avg >= 0.45,
        "score": round(avg, 4),
        "winner": winner.get("position"),
        "votes": len(votes),
    }
