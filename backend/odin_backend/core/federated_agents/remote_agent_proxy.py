"""Remote agent proxy — agents remain sandboxed to origin node."""

from __future__ import annotations

from typing import Any


class RemoteAgentProxy:
    def __init__(self, *, node_id: str, agent_id: str, capabilities: list[str], expertise: list[str], trust: float, latency_ms: float) -> None:
        self.node_id = node_id
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.expertise_domains = expertise
        self.trust_score = trust
        self.reasoning_latency_ms = latency_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "expertise_domains": self.expertise_domains,
            "trust_score": self.trust_score,
            "reasoning_latency_ms": self.reasoning_latency_ms,
            "sandboxed": True,
        }
