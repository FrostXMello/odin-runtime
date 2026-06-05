"""Runtime agent registry — health, heartbeats, active workflows."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.agents.base import AgentState
from odin_backend.models.task import AgentId


class AgentRuntimeRecord(BaseModel):
    agent_id: AgentId
    state: AgentState = AgentState.IDLE
    health: str = "healthy"  # healthy | degraded | unhealthy
    last_heartbeat: datetime | None = None
    active_workflows: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    restart_count: int = 0


class AgentRuntimeRegistry:
    def __init__(self) -> None:
        self._agents: dict[AgentId, AgentRuntimeRecord] = {}

    def register(self, agent_id: AgentId) -> AgentRuntimeRecord:
        if agent_id not in self._agents:
            self._agents[agent_id] = AgentRuntimeRecord(agent_id=agent_id)
        return self._agents[agent_id]

    def heartbeat(self, agent_id: AgentId, *, state: AgentState | None = None, metrics: dict | None = None) -> AgentRuntimeRecord:
        rec = self.register(agent_id)
        rec.last_heartbeat = datetime.now(timezone.utc)
        if state:
            rec.state = state
        if metrics:
            rec.metrics.update(metrics)
        return rec

    def set_state(self, agent_id: AgentId, state: AgentState) -> None:
        self.register(agent_id).state = state

    def add_workflow(self, agent_id: AgentId, workflow_id: str) -> None:
        rec = self.register(agent_id)
        if workflow_id not in rec.active_workflows:
            rec.active_workflows.append(workflow_id)

    def remove_workflow(self, agent_id: AgentId, workflow_id: str) -> None:
        rec = self._agents.get(agent_id)
        if rec and workflow_id in rec.active_workflows:
            rec.active_workflows.remove(workflow_id)

    def mark_unhealthy(self, agent_id: AgentId) -> None:
        self.register(agent_id).health = "unhealthy"

    def list_all(self) -> list[AgentRuntimeRecord]:
        return list(self._agents.values())

    def get_stale(self, max_age_seconds: int) -> list[AgentId]:
        now = datetime.now(timezone.utc)
        stale: list[AgentId] = []
        for rec in self._agents.values():
            if rec.last_heartbeat is None:
                stale.append(rec.agent_id)
                continue
            age = (now - rec.last_heartbeat).total_seconds()
            if age > max_age_seconds:
                stale.append(rec.agent_id)
        return stale
