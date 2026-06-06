from __future__ import annotations
from typing import Any

MODES = ("passive", "assistant", "engineering", "debugging", "strategic")

def hint(*, context: dict, mode: str = "assistant") -> dict[str, Any]:
    m = mode if mode in MODES else "assistant"
    return {"text": f"Hint for {context.get('file', 'workspace')}", "mode": m}
