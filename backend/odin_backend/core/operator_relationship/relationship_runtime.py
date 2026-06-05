"""Operator relationship orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.operator_relationship.adaptive_assistance import suggest_assistance
from odin_backend.core.operator_relationship.collaboration_style import adapt_style
from odin_backend.core.operator_relationship.interaction_memory import InteractionMemory
from odin_backend.core.operator_relationship.operator_preferences import OperatorPreferences
from odin_backend.core.operator_relationship.operator_profile import OperatorProfileStore
from odin_backend.core.operator_relationship.workflow_patterns import WorkflowPatterns


class OperatorRelationshipRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._store = OperatorProfileStore(app.settings)
        self._interactions = InteractionMemory()
        self._workflows = WorkflowPatterns()
        self._prefs = OperatorPreferences()
        self._operator_id = "default"

    async def connect(self) -> None:
        await self._store.connect()

    async def disconnect(self) -> None:
        await self._store.disconnect()

    async def record_interaction(self, *, kind: str, detail: str) -> dict[str, Any]:
        entry = self._interactions.record(kind=kind, detail=detail)
        pattern = self._workflows.observe(kind)
        self._emit("operator_pattern_learned", pattern)
        profile = {
            "operator_id": self._operator_id,
            "interaction_count": len(self._interactions.recent(1000)),
            "preferences": self._prefs.get(),
            "style": adapt_style(len(self._interactions.recent(1000))),
        }
        await self._store.save(self._operator_id, profile)
        return entry

    async def snapshot(self) -> dict[str, Any]:
        profile = await self._store.get(self._operator_id)
        style = adapt_style(len(self._interactions.recent(1000)))
        assistance = suggest_assistance(style=style, context="runtime")
        return {
            "profile": profile,
            "preferences": self._prefs.get(),
            "style": style,
            "assistance": assistance,
            "top_patterns": self._workflows.top(),
            "recent_interactions": len(self._interactions.recent()),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_relationship")
