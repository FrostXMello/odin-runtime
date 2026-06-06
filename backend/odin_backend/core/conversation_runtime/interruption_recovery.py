"""Conversation interruption recovery."""
from __future__ import annotations
from typing import Any

def recover(*, partial: str, intent: str = "") -> dict[str, Any]:
    return {"recovered": True, "resume_from": partial[-40:], "intent": intent or "continue"}
