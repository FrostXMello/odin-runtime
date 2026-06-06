from __future__ import annotations


def heartbeat(*, idle_s: float) -> dict:
    return {"idle_s": idle_s, "attention": "ambient" if idle_s > 120 else "active"}
