"""Base tool interface — agents never hardcode tools."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.task import AgentId
from odin_backend.permissions.models import PermissionClass


class ToolContext(BaseModel):
    """Runtime context passed to every tool invocation."""

    task_id: str | None = None
    agent_id: AgentId
    correlation_id: str | None = None
    user_confirmed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Standard tool output envelope."""

    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class Tool(ABC):
    """Abstract modular tool."""

    name: str
    description: str
    permission_class: PermissionClass

    @abstractmethod
    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        """Execute tool with validated parameters."""

    def get_schema(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "permission_class": self.permission_class.value,
        }
