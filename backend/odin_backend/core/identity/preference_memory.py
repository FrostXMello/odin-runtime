"""Operator preference memory for identity."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PreferenceMemory(BaseModel):
    preferred_strategies: list[str] = Field(default_factory=list)
    avoided_capabilities: list[str] = Field(default_factory=list)
    operator_notes: str = ""
