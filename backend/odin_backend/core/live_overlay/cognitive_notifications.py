from __future__ import annotations

def notify(*, title: str, body: str) -> dict:
    return {"title": title[:80], "body": body[:200], "local_only": True}
