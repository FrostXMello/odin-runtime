from __future__ import annotations


def attention_vector(*, focus: str, weight: float = 0.7) -> dict:
    return {"focus": focus[:120], "weight": weight}
