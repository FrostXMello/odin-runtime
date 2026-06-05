"""Behavioral profiles and workflow preference learning."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.memory.coordinator import MimirCoordinator


class UserProfile(BaseModel):
    tone: str = "professional"  # professional | concise | detailed
    research_depth: str = "normal"  # shallow | normal | deep
    summarization_style: str = "bullet"  # bullet | narrative
    preferred_agents: dict[str, int] = Field(default_factory=dict)
    tool_preferences: dict[str, int] = Field(default_factory=dict)
    project_priorities: list[str] = Field(default_factory=lambda: ["PROJECT_ODIN"])


class PersonalizationEngine:
    def __init__(self, memory: MimirCoordinator) -> None:
        self._memory = memory
        self._profile = UserProfile()

    async def load(self) -> UserProfile:
        stored = await self._memory.get_preference("user_profile")
        if stored:
            self._profile = UserProfile.model_validate(stored)
        return self._profile

    async def save(self) -> None:
        await self._memory.set_preference("user_profile", self._profile.model_dump())

    async def record_tool_use(self, tool_name: str, agent_id: str) -> None:
        self._profile.tool_preferences[tool_name] = self._profile.tool_preferences.get(tool_name, 0) + 1
        self._profile.preferred_agents[agent_id] = self._profile.preferred_agents.get(agent_id, 0) + 1
        await self.save()

    def adapt_planning_hints(self) -> dict[str, Any]:
        return {
            "tone": self._profile.tone,
            "research_depth": self._profile.research_depth,
            "summarization_style": self._profile.summarization_style,
            "priority_projects": self._profile.project_priorities,
        }

    def update_preference(self, **kwargs) -> UserProfile:
        for k, v in kwargs.items():
            if hasattr(self._profile, k):
                setattr(self._profile, k, v)
        return self._profile
