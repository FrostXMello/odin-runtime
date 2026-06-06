from __future__ import annotations

def attention(*, focus: str, weight: float = 0.5) -> dict:
    return {"focus": focus[:80], "weight": round(weight, 3)}
