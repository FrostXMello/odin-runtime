"""Federation runtime orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.federation.federation_health import FederationHealth
from odin_backend.core.federation.federation_policies import FederationPolicies
from odin_backend.core.federation.federation_presence import FederationPresence
from odin_backend.core.federation.federation_security import FederationSecurity
from odin_backend.core.federation.federation_state_sync import FederationStateSync
from odin_backend.core.federation.federation_topology import FederationTopology
from odin_backend.core.federation.federation_transport import FederationTransport
from odin_backend.core.federation.node_identity import NodeIdentity
from odin_backend.core.federation.node_registry import NodeRegistry


class FederationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._registry = NodeRegistry(app.settings)
        self._transport = FederationTransport()
        self._topology = FederationTopology()
        self._presence = FederationPresence()
        self._sync = FederationStateSync()
        self._security = FederationSecurity(app.settings)
        self._policies = FederationPolicies(app.settings)
        self._health = FederationHealth()
        self._local_node: dict[str, Any] | None = None
        self._mode = "isolated"

    async def connect(self) -> None:
        await self._registry.connect()
        if not self._local_node:
            await self._bootstrap_local()

    async def disconnect(self) -> None:
        await self._registry.disconnect()

    async def _bootstrap_local(self) -> None:
        agent_count = 0
        mission_count = 0
        if hasattr(self._app, "agent_society"):
            agents = await self._app.agent_society.list_agents()
            agent_count = len(agents)
        if hasattr(self._app, "mission_manager"):
            missions = await self._app.mission_manager.list_active_missions()
            mission_count = len(missions) if missions else 0
        identity = NodeIdentity(
            name=getattr(self._app.settings, "federation_node_name", "odin-local"),
            role=getattr(self._app.settings, "federation_node_role", "coordinator"),
            capabilities=["reasoning", "execution", "knowledge"],
            federation_mode=self._mode,
            active_agent_count=agent_count,
            active_mission_count=mission_count,
        )
        saved = await self._registry.save(identity)
        self._local_node = saved
        self._security.issue_token(identity.node_id)
        self._presence.heartbeat(identity.node_id)

    @property
    def local_node_id(self) -> str | None:
        return self._local_node.get("node_id") if self._local_node else None

    async def connect_node(
        self,
        *,
        name: str,
        role: str = "worker",
        capabilities: list[str] | None = None,
        mode: str = "trusted_cluster",
        token: str | None = None,
    ) -> dict[str, Any]:
        allowed, reason = self._policies.allow_connect(mode)
        if not allowed:
            return {"accepted": False, "reason": reason}
        if hasattr(self._app, "federation_governance"):
            gov_ok, gov_reason = self._app.federation_governance.allow_connection(name)
            if not gov_ok:
                return {"accepted": False, "reason": gov_reason}
        identity = NodeIdentity(
            name=name,
            role=role,
            capabilities=capabilities or ["reasoning"],
            federation_mode=mode,
        )
        saved = await self._registry.save(identity)
        issued = self._security.issue_token(identity.node_id)
        if token:
            ok, _ = self._security.authenticate(identity.node_id, token)
            if not ok:
                return {"accepted": False, "reason": "auth_failed"}
        local_id = self.local_node_id
        if local_id:
            self._topology.link(local_id, identity.node_id, kind=mode)
        self._presence.heartbeat(identity.node_id)
        self._health.record(identity.node_id, latency_ms=5.0, healthy=True)
        self._mode = mode
        self._emit("federation_node_connected", {"node_id": identity.node_id, "name": name, "mode": mode})
        return {"accepted": True, "node": saved, "token": issued}

    async def disconnect_node(self, node_id: str) -> dict[str, Any]:
        await self._registry.update_status(node_id, "disconnected")
        self._emit("federation_node_disconnected", {"node_id": node_id})
        return {"node_id": node_id, "status": "disconnected"}

    async def list_nodes(self) -> list[dict[str, Any]]:
        return await self._registry.list_all(status=None, limit=100)

    def topology(self) -> dict[str, Any]:
        return self._topology.snapshot()

    def trust_map(self) -> dict[str, float]:
        nodes = {}
        if self._local_node:
            nodes[self._local_node["node_id"]] = self._local_node.get("trust_level", 0.5)
        return nodes

    async def sync_state(self, node_id: str) -> dict[str, Any]:
        node = await self._registry.get(node_id)
        if not node:
            return {"error": "node_not_found"}
        return self._sync.push(node_id, node)

    def snapshot(self) -> dict[str, Any]:
        return {
            "mode": self._mode,
            "local_node_id": self.local_node_id,
            "topology": self._topology.snapshot(),
            "presence": self._presence.snapshot(),
            "health": self._health.snapshot(),
            "transport_pending": self._transport.pending_count(),
            "sync_versions": self._sync.versions(),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="federation")
