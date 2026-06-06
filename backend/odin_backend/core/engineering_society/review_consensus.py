from __future__ import annotations


def consensus(votes: list[bool]) -> dict:
    approved = sum(votes) >= max(2, len(votes) // 2 + 1)
    return {"approved": approved, "votes": len(votes)}
