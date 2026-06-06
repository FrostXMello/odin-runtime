from __future__ import annotations


def schedule(*, load: float) -> dict:
    return {"priority": "reasoning" if load > 0.6 else "workspace", "bounded": True}
