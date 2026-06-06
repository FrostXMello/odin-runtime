"""Repository graph intelligence runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.copilot.code_reasoning.api_contract_mapper import map_api_contracts
from odin_backend.core.copilot.code_reasoning.architecture_drift_detector import detect_drift
from odin_backend.core.copilot.code_reasoning.dependency_graph_engine import build_dependency_graph
from odin_backend.core.copilot.code_reasoning.execution_flow_mapper import map_execution_flow
from odin_backend.core.copilot.code_reasoning.repository_graph import build_repository_graph
from odin_backend.core.copilot.code_reasoning.semantic_code_map import build_semantic_map
from odin_backend.core.copilot.code_reasoning.service_relationships import map_services


class RepositoryGraphRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def analyze(self, *, repo: str, files: list[str]) -> dict[str, Any]:
        if not getattr(self._app.settings, "repository_graph_enabled", False):
            return {"accepted": False, "reason": "repository_graph_disabled"}
        graph = build_repository_graph(repo=repo, files=files)
        semantic = build_semantic_map(files=files)
        deps = build_dependency_graph(files=files)
        services = map_services(files=files)
        flow = map_execution_flow(files=files)
        apis = map_api_contracts(files=files)
        prior = None
        if hasattr(self._app, "engineering_memory"):
            prior = self._app.engineering_memory._repos.latest(repo)
        drift = detect_drift(current=graph, prior=prior.get("structure") if prior else None)
        if drift.get("drift_detected"):
            self._emit("architecture_drift_detected", drift)
        self._emit("repository_graph_updated", {"repo": repo, "nodes": graph.get("nodes", 0)})
        return {
            "accepted": True,
            "graph": graph,
            "semantic": semantic,
            "dependencies": deps,
            "services": services,
            "flow": flow,
            "apis": apis,
            "drift": drift,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": getattr(self._app.settings, "repository_graph_enabled", False)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="repository_graph")
