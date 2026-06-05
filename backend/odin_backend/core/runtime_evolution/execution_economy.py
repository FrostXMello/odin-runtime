"""Execution cost tracking."""

from __future__ import annotations

from typing import Any


class ExecutionEconomy:
    def __init__(self) -> None:
        self._costs: list[float] = []

    def record(self, cost: float) -> None:
        self._costs.append(cost)

    def average(self) -> float:
        if not self._costs:
            return 0.0
        return round(sum(self._costs) / len(self._costs), 4)

    def snapshot(self) -> dict[str, Any]:
        return {"samples": len(self._costs), "average_cost": self.average()}
