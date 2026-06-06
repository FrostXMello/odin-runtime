from __future__ import annotations


def aware(*, context: str) -> dict:
    return {"context": context[:80], "aware": True}
