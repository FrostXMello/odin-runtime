"""Contextual response assembly."""
from __future__ import annotations
from typing import Any

def respond(*, prompt: str, context: dict | None = None) -> dict[str, Any]:
    ctx = context or {}
    return {"text": f"Understood: {prompt[:80]}", "context_keys": list(ctx.keys())[:8], "confidence": 0.72}
