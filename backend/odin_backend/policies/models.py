"""Policy models."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PolicyScope(StrEnum):
    GLOBAL = "global"
    WORKFLOW = "workflow"
    SANDBOX = "sandbox"
    TERMINAL = "terminal"
    BROWSER = "browser"
    FILESYSTEM = "filesystem"


class PolicyRule(BaseModel):
    id: str
    name: str
    scope: PolicyScope
    description: str = ""
    enabled: bool = True
    constraints: dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(BaseModel):
    allowed: bool
    rule_id: str | None = None
    rule_name: str | None = None
    reason: str = ""
    explainable: dict[str, Any] = Field(default_factory=dict)
    remediation: str | None = None
