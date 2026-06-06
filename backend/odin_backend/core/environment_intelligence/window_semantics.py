from __future__ import annotations


def semantics(*, title: str, app: str) -> dict:
    return {"title": title[:80], "app": app[:40], "coding": "code" in title.lower()}
