"""Execution graph runtime (Prompt 58)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.execution_graph.dag_store import ExecutionDagStore


class ExecutionGraphRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "execution_dag.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = ExecutionDagStore(db)

    async def build_execution_dag(self, *, stages: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "execution_graph_enabled", False):
            return {"accepted": False, "reason": "execution_graph_disabled"}
        pipeline = (stages or ["plan", "review", "execute"])[:16]
        for i, s in enumerate(pipeline):
            self._store.add_node(node_id=s[:80], payload={"stage": s, "index": i})
            if i > 0:
                self._store.add_edge(src=pipeline[i - 1][:80], dst=s[:80])
        self._emit("execution_dag_generated", {"stages": len(pipeline)})
        return {"accepted": True, "dag": self._store.topology(), "virtualized": len(pipeline) > 8}

    async def compute_execution_dependencies(self) -> dict[str, Any]:
        topo = self._store.topology()
        return {"accepted": True, "dependencies": topo["edges"], "bounded": True}

    async def generate_rollback_graph(self) -> dict[str, Any]:
        topo = self._store.topology()
        rollback = list(reversed([n["node_id"] for n in topo["nodes"]]))
        self._emit("rollback_graph_generated", {"nodes": len(rollback)})
        return {"accepted": True, "rollback": rollback, "reversible": True}

    async def detect_graph_pressure(self) -> dict[str, Any]:
        topo = self._store.topology()
        pressure = min(1.0, len(topo["edges"]) / 50.0)
        return {"accepted": True, "pressure": round(pressure, 2)}

    def snapshot(self) -> dict[str, Any]:
        topo = self._store.topology()
        return {"nodes": len(topo["nodes"]), "edges": len(topo["edges"])}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="execution_graph")
