"""HEIMDALL — centralized security, approvals, audit."""

from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.events.bus import EventBus
from odin_backend.monitoring.audit import AuditLogger
from odin_backend.permissions.models import PermissionClass, PermissionDecision
from odin_backend.permissions.service import PermissionService
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class PermissionRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tool_name: str
    agent_id: AgentId
    permission_class: PermissionClass
    reason: str = ""
    approved: bool | None = None
    task_id: str | None = None


class HeimdallService:
    """Permission interception, approval workflows, audit."""

    def __init__(
        self,
        permission_service: PermissionService,
        event_bus: EventBus,
        audit: AuditLogger,
    ) -> None:
        self._permissions = permission_service
        self._event_bus = event_bus
        self._audit = audit
        self._pending: dict[str, PermissionRequest] = {}

    async def check_and_audit(
        self,
        tool_name: str,
        agent_id: AgentId,
        *,
        user_confirmed: bool = False,
    ) -> PermissionDecision:
        decision = self._permissions.check(tool_name, agent_id, user_confirmed=user_confirmed)
        await self._audit.log_permission(
            tool_name, str(agent_id), decision.allowed, decision.reason
        )

        if decision.requires_confirmation and not user_confirmed:
            req = PermissionRequest(
                tool_name=tool_name,
                agent_id=agent_id,
                permission_class=decision.permission_class,
                reason=decision.reason,
            )
            self._pending[req.id] = req
            await self._event_bus.publish(
                Event(
                    type=EventType.PERMISSION_REQUESTED,
                    source=AgentId.HEIMDALL,
                    payload=req.model_dump(mode="json"),
                )
            )

        if not decision.allowed and not decision.requires_confirmation:
            await self._event_bus.publish(
                Event(
                    type=EventType.PERMISSION_DENIED,
                    source=AgentId.HEIMDALL,
                    payload={"tool": tool_name, "reason": decision.reason},
                )
            )

        return decision

    async def approve(self, request_id: str) -> PermissionRequest | None:
        req = self._pending.pop(request_id, None)
        if not req:
            return None
        req.approved = True
        await self._event_bus.publish(
            Event(
                type=EventType.PERMISSION_GRANTED,
                source=AgentId.HEIMDALL,
                payload=req.model_dump(mode="json"),
            )
        )
        return req

    def list_pending(self) -> list[PermissionRequest]:
        return list(self._pending.values())
