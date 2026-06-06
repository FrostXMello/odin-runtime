"""Persistent autonomous workspace (Prompt 49)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_workspace.daily_resumption_planner import plan
from odin_backend.core.autonomous_workspace.intent_continuation_runtime import continue_intent
from odin_backend.core.autonomous_workspace.session_prediction_engine import predict
from odin_backend.core.autonomous_workspace.workflow_recovery_system import recover
from odin_backend.core.autonomous_workspace.workspace_continuity_v2 import load_graph, save_graph


class AutonomousWorkspaceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = "./data/autonomous_workspace.json"
        self._history: list[str] = []

    async def open(self, *, project: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_workspace_enabled", False):
            return {"accepted": False, "reason": "autonomous_workspace_disabled"}
        graph = {"project": project, "nodes": []}
        if hasattr(self._app, "cognitive_kernel"):
            await self._app.cognitive_kernel.restore()
        save_graph(path=self._path, graph=graph)
        return {"accepted": True, "graph": graph, "supervised": True}

    async def predict_next(self) -> dict[str, Any]:
        pred = predict(history=self._history)
        self._emit("workspace_prediction_generated", pred)
        return {"accepted": True, **pred}

    async def recover_workflow(self) -> dict[str, Any]:
        rec = await recover(self._app)
        cont = continue_intent(intent=rec.get("narrative", "engineering"))
        self._emit("workflow_resumed", cont)
        return {"accepted": True, "recovery": rec, "continuation": cont}

    async def daily_resume(self) -> dict[str, Any]:
        p = await plan(self._app)
        restored = load_graph(path=self._path)
        return {"accepted": True, "plan": p, "workspace": restored}

    def snapshot(self) -> dict[str, Any]:
        return {"history_len": len(self._history)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_workspace")
