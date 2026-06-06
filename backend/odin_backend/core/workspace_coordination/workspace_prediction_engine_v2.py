from __future__ import annotations


def predict(*, context: str) -> dict:
    return {"next": context[:60], "confidence": 0.7}
