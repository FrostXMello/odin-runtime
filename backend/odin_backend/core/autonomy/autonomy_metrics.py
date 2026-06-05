"""Autonomy loop metrics."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AutonomyMetrics(BaseModel):
    cycles_completed: int = 0
    objectives_generated: int = 0
    missions_spawned: int = 0
    loops_skipped_budget: int = 0
    safety_interventions: int = 0
    environment_alerts: int = 0
    research_iterations: int = 0
    loop_types_run: dict[str, int] = Field(default_factory=dict)

    def record_loop(self, loop_type: str) -> None:
        self.cycles_completed += 1
        self.loop_types_run[loop_type] = self.loop_types_run.get(loop_type, 0) + 1
