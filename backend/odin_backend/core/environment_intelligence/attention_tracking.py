from __future__ import annotations


def track(*, focus: str) -> dict:
    return {"focus": focus[:80], "intensity": 0.7}
