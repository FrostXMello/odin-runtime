"""Autonomy policy configuration (operator mode)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class AutonomyPermissionMode(StrEnum):
    OBSERVE_ONLY = "observe_only"
    SUPERVISED = "supervised"
    SEMI_AUTONOMOUS = "semi_autonomous"
    RESEARCH_ONLY = "research_only"
    FULLY_LOCAL_AUTONOMOUS = "fully_local_autonomous"


class AutonomyPolicyConfig(BaseModel):
    mode: AutonomyPermissionMode = AutonomyPermissionMode.SUPERVISED
    max_missions_per_hour: int = 5
    max_cycle_budget_seconds: float = 30.0
    cooldown_seconds: float = 10.0
    require_approval_for_missions: bool = True
    allow_research: bool = True
    allow_optimization: bool = True
    allow_proactive_missions: bool = False
    max_recursion_depth: int = 3
    enabled_loop_types: list[str] = Field(
        default_factory=lambda: [
            "monitoring_loop",
            "reflection_loop",
            "memory_consolidation_loop",
        ]
    )
