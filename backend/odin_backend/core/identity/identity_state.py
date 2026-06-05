"""Versioned identity state model."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from odin_backend.core.identity.behavioral_profile import BehavioralProfile
from odin_backend.core.identity.communication_style import CommunicationStyle
from odin_backend.core.identity.mission_style import MissionStyle
from odin_backend.core.identity.preference_memory import PreferenceMemory


class IdentityState(BaseModel):
    version: int = 1
    name: str = "Odin"
    behavioral: BehavioralProfile = Field(default_factory=BehavioralProfile)
    communication: CommunicationStyle = Field(default_factory=CommunicationStyle)
    preferences: PreferenceMemory = Field(default_factory=PreferenceMemory)
    mission_style: MissionStyle = Field(default_factory=MissionStyle)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changelog: list[str] = Field(default_factory=list)

    def apply_bounded_update(self, patch: dict, *, max_delta: float = 0.15) -> "IdentityState":
        """Apply operator-controlled bounded trait updates."""
        if "behavioral" in patch:
            b = patch["behavioral"]
            for key in ("verbosity", "planning_aggressiveness", "exploration_tendency", "risk_tolerance"):
                if key in b:
                    current = getattr(self.behavioral, key)
                    delta = max(-max_delta, min(max_delta, float(b[key]) - current))
                    setattr(self.behavioral, key, current + delta)
            if "reasoning_style" in b:
                self.behavioral.reasoning_style = str(b["reasoning_style"])[:32]
        if "communication" in patch:
            c = patch["communication"]
            if "tone" in c:
                self.communication.tone = str(c["tone"])[:32]
        self.behavioral.clamp()
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)
        self.changelog.append(f"v{self.version} bounded update")
        if len(self.changelog) > 20:
            self.changelog = self.changelog[-20:]
        return self
