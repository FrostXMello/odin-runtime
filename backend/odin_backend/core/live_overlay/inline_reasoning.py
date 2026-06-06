from __future__ import annotations

def inline(*, line: int, reasoning: str) -> dict:
    return {"line": line, "reasoning": reasoning[:300]}
