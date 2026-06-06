from __future__ import annotations

def week_context(*, items: list[str]) -> dict:
    return {"items": items[:14], "count": len(items)}
