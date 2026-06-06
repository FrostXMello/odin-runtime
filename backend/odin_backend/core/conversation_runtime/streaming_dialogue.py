"""Token streaming dialogue."""
from __future__ import annotations
from typing import Any

def stream_tokens(text: str, *, chunk: int = 8) -> list[str]:
    return [text[i : i + chunk] for i in range(0, max(len(text), 1), chunk)] or [""]
