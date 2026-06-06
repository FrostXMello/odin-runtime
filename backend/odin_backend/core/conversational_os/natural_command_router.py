from __future__ import annotations
from typing import Any

COMMANDS = ("mission", "benchmark", "focus", "debug", "status", "restore")

def route(*, text: str) -> dict[str, Any]:
    lower = text.lower()
    for c in COMMANDS:
        if c in lower:
            return {"command": c, "confidence": 0.8, "text": text[:200]}
    return {"command": "chat", "confidence": 0.5, "text": text[:200]}
