"""Behavioral profile traits."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BehavioralProfile(BaseModel):
    reasoning_style: str = "analytical"
    verbosity: float = 0.5
    planning_aggressiveness: float = 0.5
    exploration_tendency: float = 0.4
    risk_tolerance: float = 0.3

    def clamp(self) -> "BehavioralProfile":
        for field in ("verbosity", "planning_aggressiveness", "exploration_tendency", "risk_tolerance"):
            val = getattr(self, field)
            setattr(self, field, max(0.1, min(0.9, val)))
        return self
