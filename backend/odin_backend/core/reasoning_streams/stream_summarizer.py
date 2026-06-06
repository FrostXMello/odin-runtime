from __future__ import annotations

def summarize(*, items: list[str]) -> dict:
    return {"summary": "; ".join(items[:4])[:300], "count": len(items)}
