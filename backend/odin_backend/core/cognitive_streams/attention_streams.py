from __future__ import annotations


def stream(*, focus: str) -> dict:
    return {"channel": "attention", "focus": focus[:60]}
