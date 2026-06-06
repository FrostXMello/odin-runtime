from __future__ import annotations


def map_failures(tests: list[str]) -> dict:
    return {"flaky": [t for t in tests if "retry" in t.lower()], "count": len(tests)}
