from __future__ import annotations

from typing import Any


def debug_assist(context: dict) -> dict[str, Any]:
    return {"error": context.get("error", "")[:120], "steps": ["reproduce", "localize", "patch in sandbox"]}
