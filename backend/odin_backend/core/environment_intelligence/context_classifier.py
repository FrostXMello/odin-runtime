from __future__ import annotations


def classify(*, context: str) -> str:
    c = context.lower()
    if "debug" in c:
        return "debugging"
    if "test" in c:
        return "testing"
    return "engineering"
