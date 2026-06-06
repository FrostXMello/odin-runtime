from __future__ import annotations

from typing import Any


def hierarchical_infer(*, prompt: str, complexity: float) -> dict[str, Any]:
    model = "fast" if complexity < 0.5 else "reasoning"
    return {"model": model, "text": f"[{model}]{prompt[:80]}"}
