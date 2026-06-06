from __future__ import annotations

from typing import Any


def benchmark_patch(*, before: str, after: str) -> dict[str, Any]:
    delta = abs(len(after) - len(before))
    score = max(0.2, 1.0 - delta / max(len(before), 1) * 0.1)
    return {"score": round(score, 3), "delta_chars": delta}
