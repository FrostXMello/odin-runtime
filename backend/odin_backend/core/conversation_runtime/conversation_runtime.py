"""Real-time conversational runtime orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.conversation_runtime.contextual_response_engine import respond
from odin_backend.core.conversation_runtime.conversation_memory_threads import ThreadStore
from odin_backend.core.conversation_runtime.intent_tracker import track_intent
from odin_backend.core.conversation_runtime.interruption_recovery import recover
from odin_backend.core.conversation_runtime.live_reasoning_renderer import render_reasoning
from odin_backend.core.conversation_runtime.realtime_chat import MODES, start_turn
from odin_backend.core.conversation_runtime.response_personality import tone_for_mode
from odin_backend.core.conversation_runtime.streaming_dialogue import stream_tokens


class ConversationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._threads = ThreadStore()
        self._mode = "assistant"
        self._turns: list[str] = []

    async def chat(self, *, prompt: str, mode: str | None = None, context: dict | None = None, thread_id: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_runtime_enabled", False):
            return {"accepted": False, "reason": "conversation_runtime_disabled"}
        self._mode = mode or self._mode
        turn = start_turn(mode=self._mode, prompt=prompt)
        if self._mode not in MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        resp = respond(prompt=prompt, context=context)
        if hasattr(self._app, "local_ai"):
            gen = await self._app.local_ai.generate(prompt=prompt, template="summary")
            resp["text"] = gen.get("text", resp["text"])
        tokens = stream_tokens(resp["text"])
        reasoning = render_reasoning(steps=[f"analyze:{prompt[:30]}", "compose response"])
        self._turns.append(prompt)
        intent = track_intent(turns=self._turns)
        thread = self._threads.append(thread_id, "user", prompt)
        self._threads.append(thread["thread_id"], "assistant", resp["text"])
        tone = tone_for_mode(self._mode)
        self._emit("thought_generated", {"mode": self._mode, "tokens": len(tokens)})
        self._emit("reasoning_stream_updated", {"steps": len(reasoning["steps"])})
        return {
            "accepted": True,
            "mode": self._mode,
            "response": resp["text"],
            "tokens": tokens,
            "reasoning": reasoning,
            "intent": intent,
            "tone": tone,
            "thread_id": thread["thread_id"],
            "streaming": True,
        }

    async def restore_thread(self, *, thread_id: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "conversation_runtime_enabled", False):
            return {"accepted": False, "reason": "conversation_runtime_disabled"}
        restored = self._threads.restore(thread_id)
        if restored["restored"]:
            self._emit("conversation_thread_restored", {"thread_id": thread_id, "messages": len(restored["messages"])})
        return {"accepted": True, **restored}

    async def recover_interruption(self, *, partial: str) -> dict[str, Any]:
        rec = recover(partial=partial, intent=self._mode)
        self._emit("reasoning_stream_updated", {"recovered": True})
        return {"accepted": True, **rec}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "turns": len(self._turns), "modes": list(MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="conversation_runtime")
