from __future__ import annotations


def link(*, topic: str, prior: str) -> dict:
    return {"topic": topic[:80], "prior": prior[:80], "linked": True}
