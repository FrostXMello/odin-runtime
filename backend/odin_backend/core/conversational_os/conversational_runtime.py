"""Conversational operating layer orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.conversational_os.contextual_intents import intent
from odin_backend.core.conversational_os.conversational_memory import ConvMemory
from odin_backend.core.conversational_os.multi_modal_sessions import session
from odin_backend.core.conversational_os.natural_command_router import route
from odin_backend.core.conversational_os.persistent_threads import ThreadStore


class ConversationalOSRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = ConvMemory()
        self._threads = ThreadStore()

    async def interact(self, *, text: str, workspace: dict | None = None, thread_id: str = "", voice: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversational_os_enabled", False):
            return {"accepted": False, "reason": "conversational_os_disabled"}
        cmd = route(text=text)
        self._memory.add("user", text)
        resp = f"Routing to {cmd['command']}: acknowledged."
        if hasattr(self._app, "conversation"):
            chat = await self._app.conversation.chat(prompt=text, context=workspace or {})
            resp = chat.get("response", resp)
        self._memory.add("assistant", resp)
        tid = self._threads.append(thread_id, {"role": "user", "content": text})
        self._threads.append(tid, {"role": "assistant", "content": resp})
        self._emit("reasoning_stream_updated", {"command": cmd["command"]})
        return {
            "accepted": True,
            "command": cmd,
            "response": resp,
            "intent": intent(workspace=workspace),
            "session": session(voice=voice),
            "thread_id": tid,
            "supervised": True,
        }

    async def restore(self, *, thread_id: str) -> dict[str, Any]:
        restored = self._threads.restore(thread_id)
        if restored["restored"]:
            self._emit("conversational_context_restored", {"thread_id": thread_id})
        return {"accepted": True, **restored}

    def snapshot(self) -> dict[str, Any]:
        return {"turns": len(self._memory._turns)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversational_os")
