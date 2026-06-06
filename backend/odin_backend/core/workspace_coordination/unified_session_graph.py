from __future__ import annotations


def graph(*, sessions: list[str]) -> dict:
    return {"nodes": len(sessions), "unified": True}
