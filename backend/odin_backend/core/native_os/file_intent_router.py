from __future__ import annotations


def route(*, path: str, action: str = "open") -> dict:
    return {"path": path[:200], "action": action, "local_only": True}
