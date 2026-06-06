from __future__ import annotations
from typing import Any

OVERLAY_MODES = ("passive", "assistant", "engineering", "debugging", "strategic", "assistive", "collaborative")

def hint(*, context: dict, mode: str = "assistant") -> dict[str, Any]:
    m = mode if mode in OVERLAY_MODES else "assistant"
    return {"text": f"Hint for {context.get('file', 'workspace')}", "mode": m}
