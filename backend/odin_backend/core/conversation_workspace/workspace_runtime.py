"""Unified chat + cognitive stream workspace."""
from __future__ import annotations
from typing import Any
from uuid import uuid4


class ConversationWorkspaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._workspace_id = str(uuid4())
        self._panels = ["chat", "thought_stream", "reasoning", "missions", "agents", "context", "memory"]

    async def open(self, *, thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_workspace_enabled", False):
            return {"accepted": False, "reason": "conversation_workspace_disabled"}
        chat = {}
        if hasattr(self._app, "conversational_os"):
            chat = await self._app.conversational_os.interact(text="workspace open", thread_id=thread_id)
        streams = {}
        if hasattr(self._app, "reasoning_streams"):
            streams = await self._app.reasoning_streams.push(thought="workspace active")
        self._emit("conversation_workspace_opened", {"workspace_id": self._workspace_id})
        return {
            "accepted": True,
            "workspace_id": self._workspace_id,
            "panels": self._panels,
            "chat": chat,
            "streams": streams,
            "approval_inline": True,
            "supervised": True,
        }

    async def interact(self, *, text: str, context: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_workspace_enabled", False):
            return {"accepted": False, "reason": "conversation_workspace_disabled"}
        resp = {}
        if hasattr(self._app, "conversational_os"):
            resp = await self._app.conversational_os.interact(text=text, workspace=context or {})
        if hasattr(self._app, "conversation"):
            await self._app.conversation.chat(prompt=text, context=context)
        self._emit("live_reasoning_rendered", {"text_len": len(text)})
        return {"accepted": True, "response": resp, "streaming": True}

    def snapshot(self) -> dict[str, Any]:
        return {"workspace_id": self._workspace_id, "panels": self._panels}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversation_workspace")
