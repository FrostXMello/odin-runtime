"""Active context service — transparent, permission-aware, opt-in."""

import platform
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ActiveContext(BaseModel):
    enabled: bool = False
    active_application: str | None = None
    focused_window: str | None = None
    clipboard_preview: str | None = None
    current_project: str = "PROJECT_ODIN"
    current_workflow_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActiveContextService:
    """Tracks operational context when explicitly enabled."""

    def __init__(self, settings: Settings, event_bus: EventBus) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._context = ActiveContext(enabled=settings.context_awareness_enabled)

    @property
    def enabled(self) -> bool:
        return self._context.enabled

    async def set_enabled(self, enabled: bool) -> None:
        self._context.enabled = enabled
        await self._emit_update()

    async def update(
        self,
        *,
        application: str | None = None,
        window: str | None = None,
        clipboard: str | None = None,
        project: str | None = None,
        workflow_id: str | None = None,
    ) -> ActiveContext:
        if not self._context.enabled:
            return self._context

        if application is not None:
            self._context.active_application = application
        if window is not None:
            self._context.focused_window = window
        if clipboard is not None:
            self._context.clipboard_preview = clipboard[:200] if clipboard else None
        if project is not None:
            self._context.current_project = project
        if workflow_id is not None:
            self._context.current_workflow_id = workflow_id

        await self._emit_update()
        return self._context

    async def snapshot(self) -> ActiveContext:
        if self._context.enabled and not self._context.active_application:
            self._context.active_application = platform.system()
        return self._context

    async def _emit_update(self) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.CONTEXT_UPDATED,
                source=AgentId.ODIN,
                workflow_id=self._context.current_workflow_id,
                payload=self._context.model_dump(mode="json"),
            )
        )
