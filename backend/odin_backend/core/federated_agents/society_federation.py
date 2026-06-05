"""Society federation bridge."""

from __future__ import annotations

from typing import Any

from odin_backend.core.federated_agents.cross_node_consensus import reach_cross_node_consensus
from odin_backend.core.federated_agents.distributed_delegation import DistributedDelegation
from odin_backend.core.federated_agents.federation_dialogue import FederationDialogue
from odin_backend.core.federated_agents.remote_agent_proxy import RemoteAgentProxy
from odin_backend.core.federated_agents.remote_reasoning import RemoteReasoning
from odin_backend.core.federated_agents.shared_objectives import SharedObjectives


class SocietyFederation:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._proxies: dict[str, RemoteAgentProxy] = {}
        self._dialogues = FederationDialogue()
        self._reasoning = RemoteReasoning()
        self._delegations = DistributedDelegation()
        self._objectives = SharedObjectives()

    def register_proxy(self, proxy: RemoteAgentProxy) -> dict[str, Any]:
        key = f"{proxy.node_id}:{proxy.agent_id}"
        self._proxies[key] = proxy
        return proxy.to_dict()

    def list_proxies(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self._proxies.values()]

    async def delegate_reasoning(self, *, to_node: str, query: str, mission_id: str | None = None) -> dict[str, Any]:
        fed = getattr(self._app, "federation_runtime", None)
        if not fed or not fed.local_node_id:
            return {"accepted": False, "reason": "no_local_node"}
        policies = fed._policies
        if not policies.allow_remote_reasoning(fed.snapshot().get("mode", "isolated")):
            return {"accepted": False, "reason": "mode_restricted"}
        req = self._reasoning.request(
            from_node=fed.local_node_id, to_node=to_node, query=query, mission_id=mission_id
        )
        self._emit("remote_reasoning_requested", req)
        result = self._reasoning.complete(
            req["id"], result=f"reasoning_stub:{query[:40]}", confidence=0.72
        )
        if result:
            self._emit("remote_reasoning_completed", result)
        return {"accepted": True, "request": req, "result": result}

    def start_dialogue(self, *, topic: str, node_ids: list[str]) -> dict[str, Any]:
        return self._dialogues.start(topic=topic, node_ids=node_ids)

    def create_delegation(self, *, from_node: str, to_node: str, task: str, mission_id: str | None = None) -> dict[str, Any]:
        return self._delegations.create(from_node=from_node, to_node=to_node, task=task, mission_id=mission_id)

    def run_consensus(self, votes: list[dict[str, Any]]) -> dict[str, Any]:
        return reach_cross_node_consensus(votes)

    def snapshot(self) -> dict[str, Any]:
        return {
            "proxies": len(self._proxies),
            "active_dialogues": len(self._dialogues.list_active()),
            "delegations": len(self._delegations.list_all()),
            "shared_objectives": len(self._objectives.list_all()),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="federated_agents")
