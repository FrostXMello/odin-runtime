from __future__ import annotations


def heatmap(*, weights: dict[str, float]) -> list[float]:
    return [min(1.0, max(0.0, v)) for v in weights.values()] or [0.5]
