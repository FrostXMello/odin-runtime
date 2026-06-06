from __future__ import annotations

from typing import Any


def score_engineering(*, patch_score: float, gate_passed: bool) -> dict[str, Any]:
    score = patch_score * (1.0 if gate_passed else 0.5)
    return {"score": round(score, 3), "gate_passed": gate_passed}
