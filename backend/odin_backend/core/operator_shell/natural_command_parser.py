"""Natural language command parsing."""

from __future__ import annotations

from typing import Any


def parse_natural(text: str) -> dict[str, Any]:
    lower = text.lower()
    intent = "search"
    if "resume" in lower or "continue" in lower:
        intent = "resume"
    elif "failed" in lower or "error" in lower:
        intent = "diagnostics"
    elif "optimize" in lower or "battery" in lower:
        intent = "optimize"
    elif "search" in lower:
        intent = "search"
    return {"intent": intent, "raw": text}
