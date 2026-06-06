from __future__ import annotations


def debate(topic: str) -> dict:
    return {"topic": topic[:80], "positions": ["modular", "monolith"], "consensus_required": True}
