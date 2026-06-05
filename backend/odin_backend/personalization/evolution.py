"""Continuous personalization evolution — transparent adaptation."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.personalization.engine import PersonalizationEngine, UserProfile


class PreferenceEvolutionState(BaseModel):
    verbosity: str = "balanced"  # concise | balanced | detailed
    coding_style: str = "structured"
    productivity_peak_hours: list[int] = Field(default_factory=list)
    workflow_habits: dict[str, int] = Field(default_factory=dict)
    interaction_count: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PreferenceEvolutionEngine:
    def __init__(self, base: PersonalizationEngine) -> None:
        self._base = base
        self._evolution = PreferenceEvolutionState()

    async def load(self) -> PreferenceEvolutionState:
        stored = await self._base._memory.get_preference("preference_evolution")
        if stored:
            self._evolution = PreferenceEvolutionState.model_validate(stored)
        return self._evolution

    async def save(self) -> None:
        await self._base._memory.set_preference(
            "preference_evolution", self._evolution.model_dump(mode="json")
        )

    async def record_interaction(self, interaction_type: str) -> None:
        self._evolution.interaction_count += 1
        self._evolution.workflow_habits[interaction_type] = (
            self._evolution.workflow_habits.get(interaction_type, 0) + 1
        )
        hour = datetime.now(timezone.utc).hour
        if hour not in self._evolution.productivity_peak_hours:
            self._evolution.productivity_peak_hours.append(hour)
            self._evolution.productivity_peak_hours = self._evolution.productivity_peak_hours[-12:]
        await self.save()

    def adapt_response_style(self) -> dict[str, Any]:
        profile: UserProfile = self._base._profile
        verbosity = self._evolution.verbosity
        if self._evolution.interaction_count > 50:
            top_habit = max(self._evolution.workflow_habits, key=self._evolution.workflow_habits.get, default="")
            if top_habit == "quick_query":
                verbosity = "concise"

        return {
            "tone": profile.tone,
            "verbosity": verbosity,
            "summarization_style": profile.summarization_style,
            "research_depth": profile.research_depth,
            "transparent": True,
            "explainable": {
                "interaction_count": self._evolution.interaction_count,
                "top_workflow_habit": max(
                    self._evolution.workflow_habits,
                    key=self._evolution.workflow_habits.get,
                    default=None,
                ),
            },
        }
