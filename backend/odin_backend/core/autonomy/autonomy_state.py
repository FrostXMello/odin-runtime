"""Autonomous operator runtime state."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class AutonomyRunState(StrEnum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    COOLDOWN = "cooldown"


class AutonomyState(BaseModel):
    run_state: AutonomyRunState = AutonomyRunState.STOPPED
    mode: str = "supervised"
    cycle_count: int = 0
    missions_generated: int = 0
    last_cycle_at: datetime | None = None
    paused_at: datetime | None = None
    active_loops: list[str] = Field(default_factory=list)
    cooldown_until: datetime | None = None

    def snapshot(self) -> dict:
        return self.model_dump(mode="json")
