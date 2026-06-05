"""Agent communication protocol — agents speak to ODIN only."""

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class AgentMessageType(StrEnum):
    RESULT = "result"
    REQUEST = "request"
    ERROR = "error"
    UPDATE = "update"
    ALERT = "alert"


class AgentMessage(BaseModel):
    """Inbound agent → ODIN envelope. No peer-to-peer routing."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent: str
    to_odin: bool = True
    type: AgentMessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    task_id: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_escalation: bool = False

    @field_validator("to_odin")
    @classmethod
    def must_target_odin(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Agent messages must target ODIN (to_odin=True)")
        return v
