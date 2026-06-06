from __future__ import annotations
from typing import Any

def surface(*, app: str, title: str = "") -> dict[str, Any]:
    return {"app": app, "title": title[:120], "focused": True}
