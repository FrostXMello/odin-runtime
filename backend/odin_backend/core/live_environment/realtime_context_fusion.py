from __future__ import annotations

def fuse(*, signals: list[str]) -> dict:
    return {"signals": signals[:10], "count": len(signals)}
