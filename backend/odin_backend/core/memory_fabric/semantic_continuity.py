from __future__ import annotations


def stitch(*, prior: str, current: str) -> dict:
    return {"prior": prior[:60], "current": current[:60], "continuous": True}
