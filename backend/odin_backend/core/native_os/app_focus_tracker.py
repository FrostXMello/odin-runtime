from __future__ import annotations


def track(*, app: str) -> dict:
    return {"app": app[:80], "focused": True}
