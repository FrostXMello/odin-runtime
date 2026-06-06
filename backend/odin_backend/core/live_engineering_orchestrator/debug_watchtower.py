from __future__ import annotations
from typing import Any


def watch(*, logs: list[str], errors: list[str]) -> dict[str, Any]:
    return {"log_lines": len(logs), "errors": errors[:5], "suggest_debug": bool(errors)}
