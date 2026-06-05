"""Observable agent message bus."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agent_messages.coordination_memory import CoordinationMemory
from odin_backend.core.agent_messages.internal_mailbox import InternalMailbox
from odin_backend.core.agent_messages.structured_dialogue import build_message


class AgentMessageBus:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mailbox = InternalMailbox()
        self._memory = CoordinationMemory()

    async def broadcast(self, *, sender: str, kind: str, content: str, recipients: list[str]) -> dict[str, Any]:
        gov = getattr(self._app, "society_governance", None) or getattr(self._app.agent_society, "_governance", None)
        if gov and not gov.allow_message(sender):
            return {"delivered": False, "reason": "rate_limited"}
        msg = build_message(sender=sender, kind=kind, content=content, recipients=recipients)
        for r in recipients:
            self._mailbox.deliver(r, msg)
        self._memory.record(msg)
        self._emit("reasoning_shared", {"message_id": msg["id"], "kind": kind})
        return msg

    def dialogues(self) -> list[dict[str, Any]]:
        return self._memory.recent()

    def inbox(self, agent_id: str) -> list[dict[str, Any]]:
        return self._mailbox.inbox(agent_id)

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="agent_messages")
