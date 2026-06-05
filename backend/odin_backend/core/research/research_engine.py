"""Autonomous research engine — local iterative reasoning."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.cognition.reflection.contradiction_detection import detect_contradictions
from odin_backend.core.research.debate import run_debate
from odin_backend.core.research.hypothesis import generate_hypothesis
from odin_backend.core.research.research_session import ResearchIteration, ResearchSession


class ResearchEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions: dict[str, ResearchSession] = {}
        self._active_id: str | None = None

    def list_sessions(self) -> list[dict]:
        return [s.model_dump(mode="json") for s in self._sessions.values()]

    def get_session(self, session_id: str) -> ResearchSession | None:
        return self._sessions.get(session_id)

    async def start(self, *, topic: str) -> ResearchSession:
        session = ResearchSession(topic=topic)
        self._sessions[session.session_id] = session
        self._active_id = session.session_id
        await self.run_iteration(topic=topic, session_id=session.session_id)
        return session

    async def run_iteration(self, *, topic: str, session_id: str | None = None) -> dict[str, Any]:
        sid = session_id or self._active_id
        session = self._sessions.get(sid) if sid else None
        if not session:
            session = ResearchSession(topic=topic)
            self._sessions[session.session_id] = session
            sid = session.session_id

        iteration_num = len(session.iterations) + 1
        ctx = await self._app.reasoning_pipeline.build(objective=topic)
        hypothesis = generate_hypothesis(topic, context=ctx.get("prompt_block", ""), iteration=iteration_num)
        debate = await run_debate(self._app, topic=topic, hypothesis=hypothesis)
        contradictions = detect_contradictions(debate.get("critic", ""))
        iteration = ResearchIteration(
            iteration=iteration_num,
            hypothesis=hypothesis,
            critique=debate.get("critic", ""),
            synthesis=debate.get("synthesizer", ""),
            contradictions=contradictions,
        )
        session.iterations.append(iteration)
        session.updated_at = datetime.now(timezone.utc)
        if len(session.iterations) >= 3:
            session.report = debate.get("synthesizer", "")
            session.status = "completed"
        loop = getattr(self._app, "autonomous_loop", None)
        if loop:
            loop.metrics.research_iterations += 1
        self._emit("research_iteration", {"session_id": sid, "iteration": iteration_num})
        return iteration.model_dump(mode="json")

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="research_engine")
