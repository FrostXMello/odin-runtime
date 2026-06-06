from __future__ import annotations

def bridge(*, url: str, title: str = "") -> dict:
    return {"url": url[:200], "title": title[:120], "local_only": True}
