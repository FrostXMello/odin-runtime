"""Cross-node contradiction resolution."""

from __future__ import annotations

from typing import Any


def resolve_contradiction(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    trust_a = a.get("trust", 0.5) * a.get("confidence", 0.5)
    trust_b = b.get("trust", 0.5) * b.get("confidence", 0.5)
    winner = "a" if trust_a >= trust_b else "b"
    return {
        "resolved": True,
        "winner": winner,
        "score_a": round(trust_a, 4),
        "score_b": round(trust_b, 4),
        "method": "trust_weighted",
    }
