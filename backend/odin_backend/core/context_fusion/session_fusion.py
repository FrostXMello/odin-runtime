from __future__ import annotations

from typing import Any


def fuse_sessions(*, sources: list[str]) -> dict[str, Any]:
    return {"sources": sources, "unified": len(sources) > 1, "session_id": "-".join(sources) or "idle"}
