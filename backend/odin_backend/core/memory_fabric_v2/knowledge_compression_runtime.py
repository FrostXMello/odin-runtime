from __future__ import annotations


def compress(*, tokens: int) -> dict:
    return {"tokens_in": tokens, "tokens_out": max(32, tokens // 4), "lossy": False}
