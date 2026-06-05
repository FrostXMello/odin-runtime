"""Policy tuning — metadata-only confidence adjustments."""

from __future__ import annotations

from typing import Any


def tune_policies(
    strategy_stats: dict[str, dict[str, float]],
    *,
    prune_below: float = 0.25,
) -> dict[str, Any]:
    pruned = [k for k, v in strategy_stats.items() if v.get("success_rate", 0) < prune_below]
    promoted = [k for k, v in strategy_stats.items() if v.get("success_rate", 0) >= 0.75]
    return {"pruned_strategies": pruned, "promoted_strategies": promoted}
