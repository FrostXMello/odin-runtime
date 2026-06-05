"""Agent society runtime orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agent_society.agent_identity import AgentIdentity
from odin_backend.core.agent_society.agent_profiles import build_profile
from odin_backend.core.agent_society.agent_registry import SocietyAgentRegistry
from odin_backend.core.agent_society.behavioral_traits import BehavioralTraits
from odin_backend.core.agent_society.cognitive_teams import CognitiveTeams
from odin_backend.core.agent_society.collaboration_graph import CollaborationGraph
from odin_backend.core.agent_society.collaboration_history import CollaborationHistory
from odin_backend.core.agent_society.consensus_engine import reach_consensus
from odin_backend.core.agent_society.continuity_state import ContinuityState
from odin_backend.core.agent_society.debate_sessions import DebateSessions
from odin_backend.core.agent_society.delegation_planner import DelegationPlanner
from odin_backend.core.agent_society.expertise_memory import ExpertiseMemory
from odin_backend.core.agent_society.objective_chains import ObjectiveChains
from odin_backend.core.agent_society.persistent_agents import PersistentAgentStore
from odin_backend.core.agent_society.society_governance import SocietyGovernance
from odin_backend.core.agent_society.specialization import evolve_expertise, rebalance
from odin_backend.core.agent_society.task_council import TaskCouncil
from odin_backend.agent_society.registry import AgentSocietyRegistry


class AgentSocietyRuntime:
    def __init__(self, app: Any, *, legacy_registry: Any | None = None) -> None:
        self._app = app
        self._legacy_registry = legacy_registry
        self._legacy_registry = AgentSocietyRegistry(app.agent_registry)
        self._store = PersistentAgentStore(app.settings)
        self._registry = SocietyAgentRegistry()
        self._continuity = ContinuityState(app.settings)
        self._objectives = ObjectiveChains(app.settings)
        self._expertise = ExpertiseMemory()
        self._collab_history = CollaborationHistory()
        self._traits = BehavioralTraits()
        self._graph = CollaborationGraph()
        self._debates = DebateSessions()
        self._delegations = DelegationPlanner()
        self._teams = CognitiveTeams()
        self._council = TaskCouncil()
        self._governance = SocietyGovernance(app)

    async def connect(self) -> None:
        await self._store.connect()
        await self._continuity.connect()
        await self._objectives.connect()
        agents = await self._store.list_all(status=None, limit=100)
        for a in agents:
            self._registry.register(a)
            restored = await self._continuity.restore(a["agent_id"])
            if restored:
                self._emit("continuity_restored", {"agent_id": a["agent_id"]})

    async def disconnect(self) -> None:
        await self._objectives.disconnect()
        await self._continuity.disconnect()
        await self._store.disconnect()

    async def spawn_agent(
        self,
        *,
        name: str,
        role: str = "generalist",
        capabilities: list[str] | None = None,
        expertise_domains: list[str] | None = None,
    ) -> dict[str, Any]:
        allowed, reason = self._governance.allow_spawn(self._registry.count())
        if not allowed:
            return {"accepted": False, "reason": reason}
        identity = AgentIdentity(
            name=name,
            role=role,
            capabilities=capabilities or [],
            expertise_domains=expertise_domains or [],
        )
        saved = await self._store.save(identity)
        self._registry.register(saved)
        await self._continuity.checkpoint(
            identity.agent_id,
            thought={"status": "initialized"},
            memory={},
            objectives=[],
        )
        self._emit("agent_spawned", {"agent_id": identity.agent_id, "name": name, "role": role})
        return saved

    async def list_agents(self) -> list[dict[str, Any]]:
        return await self._store.list_all()

    async def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        agent = await self._store.get(agent_id)
        if not agent:
            return None
        return build_profile(
            agent,
            expertise=self._expertise.list_for(agent_id),
            performance=agent.get("performance", {}),
        )

    async def record_outcome(self, agent_id: str, *, domain: str, success: bool) -> dict[str, Any]:
        agent = await self._store.get(agent_id)
        if not agent:
            return {"error": "agent_not_found"}
        conf, label = evolve_expertise(float(agent.get("confidence", 0.5)), success=success, domain=domain)
        agent["confidence"] = conf
        if label and label not in agent.get("expertise_domains", []):
            agent.setdefault("expertise_domains", []).append(label)
        identity = AgentIdentity.model_validate(agent)
        await self._store.save(identity, performance=agent.get("performance", {}))
        self._expertise.record(agent_id, domain=domain, score=conf, source="mission")
        self._emit("expertise_updated", {"agent_id": agent_id, "domain": domain, "confidence": conf})
        await self._integrate_beliefs(agent_id, domain=domain, success=success)
        return {"agent_id": agent_id, "confidence": conf, "specialization": label}

    async def start_dialogue(self, *, topic: str, participant_ids: list[str]) -> dict[str, Any]:
        if not self._governance.track_debate("new"):
            return {"accepted": False, "reason": "debate_depth_exceeded"}
        session = self._debates.start(topic=topic, participants=participant_ids)
        for i, aid in enumerate(participant_ids):
            if i + 1 < len(participant_ids):
                self._graph.link(aid, participant_ids[i + 1])
        self._collab_history.record(agents=participant_ids, kind="dialogue")
        self._emit("debate_started", {"session_id": session["id"], "topic": topic})
        if hasattr(self._app, "agent_messages"):
            await self._app.agent_messages.broadcast(
                sender=participant_ids[0] if participant_ids else "system",
                kind="dialogue_start",
                content=topic,
                recipients=participant_ids,
            )
        return session

    async def create_delegation(self, *, from_agent: str, to_agent: str, task: str, mission_id: str | None = None) -> dict:
        entry = self._delegations.create(from_agent=from_agent, to_agent=to_agent, task=task, mission_id=mission_id)
        self._graph.link(from_agent, to_agent)
        self._emit("delegation_created", entry)
        return entry

    async def create_objective(self, *, owner_agent_id: str, title: str) -> dict[str, Any]:
        obj = await self._objectives.create(owner_agent_id=owner_agent_id, title=title)
        self._emit("objective_assigned", obj)
        return obj

    async def form_team(self, *, template: str, agent_ids: list[str]) -> dict[str, Any]:
        team = self._teams.form(template=template, agent_ids=agent_ids)
        self._emit("collaboration_formed", {"team_id": team["id"], "template": template})
        return team

    async def run_consensus(self, votes: list[dict[str, Any]]) -> dict[str, Any]:
        result = reach_consensus(votes)
        if result.get("consensus"):
            self._emit("consensus_reached", result)
        return result

    async def negotiate_task(self, *, task: str, agent_ids: list[str]) -> list[dict[str, str]]:
        agents = [await self.get_agent(a) or {"agent_id": a, "role": "generalist"} for a in agent_ids]
        return await self._council.negotiate_roles(agents, task=task)

    def expertise_heatmap(self) -> dict[str, float]:
        return self._expertise.heatmap()

    def list_profiles(self) -> list[dict[str, Any]]:
        if self._legacy_registry is not None:
            return self._legacy_registry.list_profiles()
        return []

    def route_task(self, domain: str, *, context: str = "") -> Any:
        if self._legacy_registry is not None:
            return self._legacy_registry.route_task(domain, context=context)
        return "valkyrie"

    def get_reputation(self, agent_id: str) -> dict[str, Any]:
        if self._legacy_registry is not None:
            return self._legacy_registry.get_reputation(agent_id)
        return {}

    def snapshot(self) -> dict[str, Any]:
        return {
            "agent_count": self._registry.count(),
            "collaboration_graph": self._graph.snapshot(),
            "active_debates": self._debates.list_active(),
            "delegations": self._delegations.list_all()[-10:],
            "teams": self._teams.list_active(),
            "collaboration_history": self._collab_history.recent(),
            "governance": self._governance.snapshot(),
        }

    async def _integrate_beliefs(self, agent_id: str, *, domain: str, success: bool) -> None:
        if not hasattr(self._app, "knowledge_runtime"):
            return
        fact = f"Agent {agent_id} {'succeeded' if success else 'struggled'} in {domain}"
        await self._app.knowledge_runtime.ingest_fact(
            entity=f"agent:{agent_id}",
            fact=fact,
            confidence=0.65 if success else 0.4,
            source="society_learning",
        )

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="agent_society")
