"""Recursion guard decision models."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RecursionGuardDecision(StrEnum):
    ALLOW = "allow"
    SUPPRESS = "suppress"
    ESCALATE = "escalate"


class RecursionGuardResult(BaseModel):
    decision: RecursionGuardDecision
    reason: str = ""
    chain_key: str = ""
    depth: int = 0
    repeat_count: int = 0
    trace: list[str] = Field(default_factory=list)


class SuppressedLoopRecord(BaseModel):
    chain_key: str
    repeat_count: int
    first_seen_ms: float
    last_seen_ms: float
    sample_types: list[str] = Field(default_factory=list)


class RecursionGuardMetrics(BaseModel):
    recursion_events_detected: int = 0
    suppressed_signal_count: int = 0
    escalated_signal_count: int = 0
    active_signal_chains: int = 0
    kernel_processing_rate: float = 0.0
    runtime_loop_health: str = "healthy"
    suppressed_loops: list[dict[str, Any]] = Field(default_factory=list)
    active_chains: list[dict[str, Any]] = Field(default_factory=list)
