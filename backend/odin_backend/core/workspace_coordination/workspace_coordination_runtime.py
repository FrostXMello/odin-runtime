"""Multi-workspace cognitive coordination (Prompt 51)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.workspace_coordination.cross_workspace_context_bridge import bridge
from odin_backend.core.workspace_coordination.engineering_workspace_coordinator import coordinate
from odin_backend.core.workspace_coordination.multi_project_attention_router import route
from odin_backend.core.workspace_coordination.unified_session_graph import graph
from odin_backend.core.workspace_coordination.workspace_prediction_engine_v2 import predict


class WorkspaceCoordinationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def coordinate(self, *, projects: list[str]) -> dict[str, Any]:
        if not getattr(self._app.settings, "workspace_coordination_enabled", False):
            return {"accepted": False, "reason": "workspace_coordination_disabled"}
        b = bridge(projects=projects)
        r = route(projects=projects)
        self._emit("multi_project_context_linked", b)
        self._emit("workspace_attention_shifted", r)
        if hasattr(self._app, "memory_fabric_v2") and len(projects) >= 2:
            await self._app.memory_fabric_v2.link_semantic(topic=projects[0], prior=projects[1])
        return {"accepted": True, "bridge": b, "routing": r, "supervised": True}

    async def predict_restore(self, *, context: str = "engineering") -> dict[str, Any]:
        p = predict(context=context)
        if hasattr(self._app, "autonomous_workspace"):
            await self._app.autonomous_workspace.predict_next()
        return {"accepted": True, "prediction": p}

    async def unify_timeline(self, *, sessions: list[str]) -> dict[str, Any]:
        g = graph(sessions=sessions)
        return {"accepted": True, "graph": g}

    async def engineering_session(self, *, repo: str) -> dict[str, Any]:
        c = await coordinate(self._app, repo=repo)
        return {"accepted": True, "coordination": c}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workspace_coordination")
