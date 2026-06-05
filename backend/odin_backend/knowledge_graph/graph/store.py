"""NetworkX graph store — Neo4j migration path via same interface."""

from typing import Any

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class GraphStore:
    def __init__(self) -> None:
        self._nx = None
        self._graph: Any = None
        self._init_graph()

    def _init_graph(self) -> None:
        try:
            import networkx as nx

            self._nx = nx
            self._graph = nx.DiGraph()
            self._seed_odin_architecture()
        except ImportError:
            logger.warning("networkx_not_installed_using_dict_fallback")
            self._graph = {"nodes": {}, "edges": []}
            self._seed_dict_fallback()

    def _seed_odin_architecture(self) -> None:
        if self._nx is None:
            return
        nodes = [
            ("PROJECT_ODIN", {"type": "project"}),
            ("RuntimeSupervisor", {"type": "component"}),
            ("Heimdall", {"type": "agent"}),
            ("DAGWorkflowRunner", {"type": "component"}),
            ("MimirCoordinator", {"type": "component"}),
            ("VoiceSystem", {"type": "component"}),
            ("ConversationManager", {"type": "component"}),
        ]
        self._graph.add_nodes_from(nodes)
        edges = [
            ("PROJECT_ODIN", "RuntimeSupervisor", {"relation": "contains"}),
            ("PROJECT_ODIN", "Heimdall", {"relation": "secures"}),
            ("PROJECT_ODIN", "DAGWorkflowRunner", {"relation": "orchestrates"}),
            ("PROJECT_ODIN", "MimirCoordinator", {"relation": "remembers"}),
            ("PROJECT_ODIN", "VoiceSystem", {"relation": "speaks"}),
            ("PROJECT_ODIN", "ConversationManager", {"relation": "dialogues"}),
            ("DAGWorkflowRunner", "Heimdall", {"relation": "checks"}),
        ]
        self._graph.add_edges_from(edges)

    def _seed_dict_fallback(self) -> None:
        nodes = {
            "PROJECT_ODIN": {"type": "project"},
            "RuntimeSupervisor": {"type": "component"},
            "Heimdall": {"type": "agent"},
            "DAGWorkflowRunner": {"type": "component"},
            "MimirCoordinator": {"type": "component"},
            "VoiceSystem": {"type": "component"},
            "ConversationManager": {"type": "component"},
        }
        self._graph["nodes"].update(nodes)
        for src, tgt, rel in [
            ("PROJECT_ODIN", "RuntimeSupervisor", "contains"),
            ("PROJECT_ODIN", "Heimdall", "secures"),
            ("PROJECT_ODIN", "DAGWorkflowRunner", "orchestrates"),
            ("PROJECT_ODIN", "MimirCoordinator", "remembers"),
            ("PROJECT_ODIN", "VoiceSystem", "speaks"),
            ("PROJECT_ODIN", "ConversationManager", "dialogues"),
            ("DAGWorkflowRunner", "Heimdall", "checks"),
        ]:
            self._graph["edges"].append({"source": src, "target": tgt, "relation": rel})

    @property
    def graph(self) -> Any:
        return self._graph

    def add_entity(self, entity_id: str, **attrs) -> None:
        if self._nx and hasattr(self._graph, "add_node"):
            self._graph.add_node(entity_id, **attrs)
        else:
            self._graph["nodes"][entity_id] = attrs

    def add_relation(self, source: str, target: str, relation: str, **attrs) -> None:
        if self._nx and hasattr(self._graph, "add_edge"):
            self._graph.add_edge(source, target, relation=relation, **attrs)
        else:
            self._graph["edges"].append({"source": source, "target": target, "relation": relation})
