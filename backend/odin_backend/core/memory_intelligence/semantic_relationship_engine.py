from __future__ import annotations


def relate(*, a: str, b: str) -> dict:
    return {"a": a[:60], "b": b[:60], "relationship": "related"}
