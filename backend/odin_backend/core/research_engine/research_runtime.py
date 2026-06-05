"""Research fabric runtime — web-grounded autonomous research."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from odin_backend.core.research_engine.citation_engine import build_citations
from odin_backend.core.research_engine.contradiction_resolver import resolve_from_evidence
from odin_backend.core.research_engine.research_memory import ResearchMemory
from odin_backend.core.research_engine.research_planner import plan_research
from odin_backend.core.research_engine.synthesis_engine import synthesize
from odin_backend.core.research_engine.topic_tracker import TopicTracker
from odin_backend.core.research_engine.trend_analysis import analyze_trends
from odin_backend.core.research_engine.web_researcher import gather_evidence


class ResearchFabricRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._memory = ResearchMemory()
        self._topics = TopicTracker()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._enabled = getattr(app.settings, "research_fabric_enabled", False)

    async def start(self, *, topic: str, mission_id: str | None = None) -> dict[str, Any]:
        if not self._enabled:
            return {"accepted": False, "reason": "research_fabric_disabled"}
        if hasattr(self._app, "research_governance") and not self._app.research_governance.allow_research(topic):
            return {"accepted": False, "reason": "research_policy_blocked"}
        sid = str(uuid4())
        self._emit("research_started", {"session_id": sid, "topic": topic})
        session = await self._run_session(session_id=sid, topic=topic, mission_id=mission_id)
        self._sessions[sid] = session
        self._memory.record(session)
        self._topics.track(topic, metadata={"session_id": sid})
        self._emit("research_completed", {"session_id": sid, "topic": topic})
        return session

    async def research_topic(self, *, topic: str) -> dict[str, Any]:
        return await self.start(topic=topic)

    async def verify_source(self, *, url: str) -> dict[str, Any]:
        web = getattr(self._app, "web_access", None)
        if not web:
            return {"verified": False, "reason": "web_access_unavailable"}
        result = await web.fetch(url)
        verified = result.get("status") == "ok" and not result.get("blocked")
        if verified:
            self._emit("source_verified", {"url": url})
        return {"url": url, "verified": verified, "result": result}

    async def _run_session(self, *, session_id: str, topic: str, mission_id: str | None) -> dict[str, Any]:
        subqueries = plan_research(topic)
        evidence = await gather_evidence(self._app, topic=topic)
        contradictions = resolve_from_evidence(evidence)
        report = await synthesize(self._app, topic=topic, evidence=evidence, contradictions=contradictions)
        citations = build_citations(evidence)
        if hasattr(self._app, "knowledge_runtime"):
            for e in evidence[:5]:
                await self._app.knowledge_runtime.ingest_fact(
                    entity=topic,
                    fact=e.get("content", "")[:300],
                    confidence=float(e.get("trust_score", 0.5)),
                    source=e.get("url", "web"),
                    mission_origin=mission_id,
                    evidence=[e.get("url", "")],
                )
            if contradictions:
                await self._app.knowledge_runtime.contradictions()
        trends = []
        if hasattr(self._app, "knowledge_runtime"):
            hist = self._app.knowledge_runtime._temporal.history(topic)
            trends = analyze_trends(hist)
            for t in trends:
                self._emit("trend_detected", {"topic": topic, **t})
        if hasattr(self._app, "research_agents"):
            swarm = await self._app.research_agents.investigate(topic=topic, evidence=evidence)
            report["swarm_consensus"] = swarm.get("consensus")
        return {
            "session_id": session_id,
            "topic": topic,
            "subqueries": subqueries,
            "evidence": evidence,
            "citations": citations,
            "contradictions": contradictions,
            "report": report,
            "trends": trends,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "sessions": list(self._sessions.values())[-10:],
            "topics": self._topics.list_topics(),
            "memory": self._memory.recent()[-5:],
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="research_fabric")
