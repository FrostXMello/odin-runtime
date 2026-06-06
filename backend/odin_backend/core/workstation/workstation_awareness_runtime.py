"""Workstation awareness orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.workstation.application_relationships import map_relationships
from odin_backend.core.workstation.desktop_flow_memory import record_flow
from odin_backend.core.workstation.live_activity_graph import ActivityGraph
from odin_backend.core.workstation.realtime_workspace_monitor import monitor_snapshot
from odin_backend.core.workstation.runtime_attention_engine import compute_attention
from odin_backend.core.workstation.semantic_window_analysis import analyze_window


class WorkstationAwarenessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._graph = ActivityGraph()
        self._exclusions: set[str] = set()

    async def observe(self, *, snapshot: dict[str, Any]) -> dict[str, Any]:
        if not getattr(self._app.settings, "workstation_awareness_enabled", False):
            return {"accepted": False, "reason": "workstation_awareness_disabled"}
        app_name = snapshot.get("app", "unknown")
        if app_name in self._exclusions:
            return {"accepted": True, "excluded": True}
        mon = monitor_snapshot(snapshot)
        semantic = analyze_window(title=snapshot.get("title", ""), app=app_name)
        attention = compute_attention(app=app_name, duration_s=snapshot.get("duration_s", 0))
        self._graph.add_node(app=app_name, weight=attention["weight"])
        flow = record_flow(from_app=snapshot.get("prev_app"), to_app=app_name)
        relationships = map_relationships(nodes=self._graph.nodes())
        if snapshot.get("prev_app") and snapshot.get("prev_app") != app_name:
            self._emit("workspace_attention_shifted", {"from": snapshot.get("prev_app"), "to": app_name})
        return {
            "accepted": True,
            "monitor": mon,
            "semantic": semantic,
            "attention": attention,
            "flow": flow,
            "relationships": relationships,
            "local_only": True,
            "privacy_preserving": True,
        }

    def set_exclusions(self, apps: list[str]) -> dict[str, Any]:
        self._exclusions = set(apps)
        return {"exclusions": list(self._exclusions)}

    def snapshot(self) -> dict[str, Any]:
        return {"graph": self._graph.snapshot(), "exclusions": len(self._exclusions)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="workstation")
