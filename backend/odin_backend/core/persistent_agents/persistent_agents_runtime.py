"""Persistent agents runtime (Prompt 52)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.persistent_agents.agent_store import AgentStore

DEFAULT_AGENTS = (
    ("architect", "Architect"),
    ("debugger", "Debugger"),
    ("researcher", "Researcher"),
    ("reviewer", "Reviewer"),
    ("optimizer", "Optimizer"),
    ("planner", "Planner"),
    ("documentation", "Documentation"),
    ("infrastructure", "Infrastructure"),
)


class PersistentAgentsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "persistent_agents.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = AgentStore(db)

    async def restore_agents(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_agents_enabled", False):
            return {"accepted": False, "reason": "persistent_agents_disabled"}
        existing = {a["agent_id"] for a in self._store.list_agents()}
        restored = 0
        for agent_id, spec in DEFAULT_AGENTS:
            if agent_id not in existing:
                self._store.upsert({
                    "agent_id": agent_id,
                    "specialization": spec,
                    "memory_summary": "",
                    "active_objectives": [],
                    "workload_score": 0.0,
                })
                restored += 1
        self._emit("persistent_agent_restored", {"restored": restored})
        return {"accepted": True, "agents": self._store.list_agents(), "supervised": True}

    async def assign_objective(self, *, agent_id: str, objective: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "persistent_agents_enabled", False):
            return {"accepted": False, "reason": "persistent_agents_disabled"}
        agents = {a["agent_id"]: a for a in self._store.list_agents()}
        agent = agents.get(agent_id)
        if not agent:
            return {"accepted": False, "reason": "agent_not_found"}
        objs = list(agent.get("active_objectives", []))
        objs.append(objective[:120])
        agent["active_objectives"] = objs[-8:]
        self._store.upsert(agent)
        self._emit("persistent_agent_assigned", {"agent_id": agent_id, "objective": objective[:80]})
        return {"accepted": True, "agent": agent, "approval_required": True}

    async def update_agent_state(self, *, agent_id: str, workload: float) -> dict[str, Any]:
        agents = {a["agent_id"]: a for a in self._store.list_agents()}
        agent = agents.get(agent_id)
        if not agent:
            return {"accepted": False, "reason": "agent_not_found"}
        agent["workload_score"] = min(1.0, max(0.0, workload))
        self._store.upsert(agent)
        return {"accepted": True, "agent": agent}

    async def compute_agent_load(self) -> dict[str, Any]:
        agents = self._store.list_agents()
        total = sum(a.get("workload_score", 0.0) for a in agents)
        return {"accepted": True, "total_load": total, "agent_count": len(agents)}

    async def summarize_agent_memory(self, *, agent_id: str) -> dict[str, Any]:
        agents = {a["agent_id"]: a for a in self._store.list_agents()}
        agent = agents.get(agent_id)
        if not agent:
            return {"accepted": False, "reason": "agent_not_found"}
        return {"accepted": True, "summary": agent.get("memory_summary", ""), "agent_id": agent_id}

    def snapshot(self) -> dict[str, Any]:
        return {"agents": len(self._store.list_agents())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="persistent_agents")
