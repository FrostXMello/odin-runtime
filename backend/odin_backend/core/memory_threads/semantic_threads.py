from __future__ import annotations

def semantic(*, topic: str) -> dict:
    return {"topic": topic[:120], "kind": "semantic"}
