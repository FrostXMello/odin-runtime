"""Bounded hypothetical simulation engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class SimulationEngine:
    def __init__(self) -> None:
        self._runs: list[dict[str, Any]] = []

    def run(self, *, scenario: str, assumptions: list[str], branches: int = 2) -> dict[str, Any]:
        branches = min(branches, 5)
        outcomes = []
        for i in range(branches):
            conf = round(0.9 - i * 0.12, 2)
            outcomes.append({
                "branch": i,
                "outcome": f"{scenario}_branch_{i}",
                "confidence": conf,
                "assumptions": assumptions,
            })
        run = {
            "id": str(uuid4()),
            "scenario": scenario,
            "branches": outcomes,
            "reversible": True,
            "bounded": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._runs.append(run)
        return run

    def list_runs(self) -> list[dict[str, Any]]:
        return list(self._runs)
