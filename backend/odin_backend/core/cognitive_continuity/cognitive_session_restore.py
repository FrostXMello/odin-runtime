from __future__ import annotations

from typing import Any


def restore_session(*, threads: list[dict], unfinished: list[dict]) -> dict[str, Any]:
    return {"restored": bool(threads or unfinished), "threads": len(threads), "unfinished": len(unfinished)}
