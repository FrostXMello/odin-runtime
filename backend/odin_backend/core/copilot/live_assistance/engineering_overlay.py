from __future__ import annotations

from typing import Any


def overlay_hints(*, context: dict) -> dict[str, Any]:
    return {"hints": 1 if context else 0, "visible": True}
