"""Conscious loop governance decisions."""

from enum import StrEnum

from pydantic import BaseModel, Field


class CycleDecision(StrEnum):
    ALLOW = "allow"
    ESCALATE = "escalate"
    DEFER = "defer"
    OBSERVE = "observe"


class CycleGovernanceResult(BaseModel):
    decision: CycleDecision
    reason: str
    ready_nodes: int = 0
    explainable: dict = Field(default_factory=dict)
