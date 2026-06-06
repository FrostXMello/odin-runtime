from __future__ import annotations


def detect(tests: list[str]) -> dict:
    return {"drift": len(tests) > 10, "count": len(tests)}
