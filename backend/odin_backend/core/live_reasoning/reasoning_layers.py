from __future__ import annotations
from typing import Any


def layer_stack(thought: str) -> list[dict[str, Any]]:
    return [
        {"layer": "perception", "weight": 0.2},
        {"layer": "planning", "weight": 0.5, "text": thought[:80]},
        {"layer": "reflection", "weight": 0.3},
    ]
