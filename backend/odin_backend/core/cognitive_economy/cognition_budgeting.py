"""Cognitive budget management."""

from __future__ import annotations

from typing import Any

MODES = ("low_resource", "balanced", "high_performance")


class CognitionBudgeting:
    def __init__(self, mode: str = "balanced") -> None:
        self._mode = mode if mode in MODES else "balanced"
        self._budget = {"tokens": 10000, "compute_units": 100.0, "spent_tokens": 0}
        self.set_mode(self._mode)

    def set_mode(self, mode: str) -> None:
        if mode in MODES:
            self._mode = mode
            multipliers = {"low_resource": 0.5, "balanced": 1.0, "high_performance": 2.0}
            self._budget["tokens"] = int(10000 * multipliers[mode])

    def spend(self, tokens: int) -> tuple[bool, str]:
        if self._budget["spent_tokens"] + tokens > self._budget["tokens"]:
            return False, "budget_exceeded"
        self._budget["spent_tokens"] += tokens
        return True, "ok"

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, **self._budget, "remaining": self._budget["tokens"] - self._budget["spent_tokens"]}
