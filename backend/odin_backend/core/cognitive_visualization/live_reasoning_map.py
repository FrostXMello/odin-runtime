from __future__ import annotations
from typing import Any

def reasoning_map(*, steps: list[str]) -> dict[str, Any]:
    return {"layers": [{"id": f"s{i}", "label": s} for i, s in enumerate(steps[:10])]}
