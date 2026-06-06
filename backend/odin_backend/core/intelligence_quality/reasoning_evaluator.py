"""Evaluate reasoning chain quality."""

from __future__ import annotations

from typing import Any


def evaluate_chain(*, steps: list[str], evidence: list[str] | None = None) -> dict[str, Any]:
    evidence = evidence or []
    depth = len(steps)
    grounded = min(1.0, len(evidence) / max(depth, 1))
    coherence = 0.5 + min(0.5, depth * 0.05) if depth >= 2 else 0.3
    score = round((grounded * 0.6 + coherence * 0.4), 3)
    return {"score": score, "depth": depth, "grounded": grounded, "coherence": coherence}
