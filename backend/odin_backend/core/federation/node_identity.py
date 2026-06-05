"""Federated node identity model."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class NodeIdentity(BaseModel):
    node_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "odin-local"
    role: str = "worker"
    capabilities: list[str] = Field(default_factory=list)
    topology_metadata: dict = Field(default_factory=dict)
    health_state: str = "healthy"
    trust_level: float = 0.5
    latency_ms: float = 0.0
    active_agent_count: int = 0
    active_mission_count: int = 0
    federation_mode: str = "isolated"
    status: str = "active"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
