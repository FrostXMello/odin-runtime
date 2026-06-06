"""Live reasoning visualization chunks."""
from __future__ import annotations
from typing import Any

def render_reasoning(*, steps: list[str]) -> dict[str, Any]:
    return {"steps": steps[:12], "streaming": True, "complete": len(steps) <= 12}
