"""Knowledge graph service — traversal and contextual search."""

from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.knowledge_graph.graph.store import GraphStore
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class KnowledgeGraphService:
    def __init__(self, event_bus: EventBus) -> None:
        self._store = GraphStore()
        self._event_bus = event_bus

    async def add_workflow_entity(self, workflow_id: str, objective: str, project: str = "PROJECT_ODIN") -> None:
        self._store.add_entity(workflow_id, type="workflow", objective=objective)
        self._store.add_relation(project, workflow_id, "executed")
        await self._emit({"workflow_id": workflow_id, "action": "added"})

    def find_related_entities(self, entity_id: str, depth: int = 2) -> list[dict[str, Any]]:
        g = self._store.graph
        if isinstance(g, dict):
            related: list[dict] = []
            visited = {entity_id}
            frontier = [entity_id]
            for _ in range(depth):
                next_frontier = []
                for node in frontier:
                    for edge in g.get("edges", []):
                        if edge["source"] == node and edge["target"] not in visited:
                            visited.add(edge["target"])
                            tgt = edge["target"]
                            related.append({
                                "entity": tgt,
                                "from": node,
                                "relation": edge.get("relation", "related"),
                                **g["nodes"].get(tgt, {}),
                            })
                            next_frontier.append(tgt)
                frontier = next_frontier
            return related
        if not hasattr(g, "successors"):
            return []
        related: list[dict] = []
        visited = {entity_id}
        frontier = [entity_id]
        for _ in range(depth):
            next_frontier = []
            for node in frontier:
                for succ in list(g.successors(node)):
                    if succ not in visited:
                        visited.add(succ)
                        edge = g.get_edge_data(node, succ) or {}
                        related.append({
                            "entity": succ,
                            "from": node,
                            "relation": edge.get("relation", "related"),
                            **dict(g.nodes[succ]),
                        })
                        next_frontier.append(succ)
            frontier = next_frontier
        return related

    def project_dependency_map(self, project_id: str = "PROJECT_ODIN") -> dict[str, Any]:
        related = self.find_related_entities(project_id, depth=3)
        return {"project": project_id, "dependencies": related}

    def contextual_graph_search(self, query: str, limit: int = 10) -> list[dict]:
        g = self._store.graph
        q = query.lower()
        hits: list[dict] = []

        if hasattr(g, "nodes") and callable(getattr(g, "nodes", None)):
            for node, data in g.nodes(data=True):
                blob = f"{node} {data}".lower()
                if any(word in blob for word in q.split() if len(word) > 2):
                    hits.append({"entity": node, **data})
            return hits[:limit]

        for node, data in g.get("nodes", {}).items():
            blob = f"{node} {data}".lower()
            if any(word in blob for word in q.split() if len(word) > 2):
                hits.append({"entity": node, **data})
        return hits[:limit]

    async def _emit(self, payload: dict) -> None:
        await self._event_bus.publish(
            Event(type=EventType.KNOWLEDGE_GRAPH_UPDATED, source=AgentId.MIMIR, payload=payload)
        )
