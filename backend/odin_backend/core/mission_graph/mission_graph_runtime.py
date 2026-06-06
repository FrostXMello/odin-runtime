"""Mission graph runtime (Prompt 56)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.mission_graph.graph_store import MissionGraphStore


class MissionGraphRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "mission_graph.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = MissionGraphStore(db)

    async def build_mission_graph(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "mission_graph_enabled", False):
            return {"accepted": False, "reason": "mission_graph_disabled"}
        nodes = self._store.nodes()
        edges = self._store.edges()
        return {"accepted": True, "graph": {"nodes": nodes, "edges": edges}, "virtualized": len(nodes) > 20}

    async def link_related_objectives(self, *, src: str, dst: str) -> dict[str, Any]:
        self._store.add_node(node_id=src, payload={"type": "objective"})
        self._store.add_node(node_id=dst, payload={"type": "objective"})
        self._store.link(src=src, dst=dst)
        self._emit("mission_graph_linked", {"src": src[:40], "dst": dst[:40]})
        return {"accepted": True, "linked": True, "supervised": True}

    async def analyze_dependency_pressure(self) -> dict[str, Any]:
        edges = self._store.edges()
        pressure = min(1.0, len(edges) / 50.0)
        return {"accepted": True, "pressure": round(pressure, 2), "bounded": True}

    async def compute_mission_continuity_score(self) -> dict[str, Any]:
        if hasattr(self._app, "mission_continuity"):
            h = await self._app.mission_continuity.estimate_continuity_health()
            return {"accepted": True, "score": h.get("health", 0.5)}
        return {"accepted": True, "score": 0.5}

    def snapshot(self) -> dict[str, Any]:
        return {"nodes": len(self._store.nodes()), "edges": len(self._store.edges())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="mission_graph")
