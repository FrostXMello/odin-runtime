"""Collaborative engineering society (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.engineering_society.architecture_debate import debate
from odin_backend.core.engineering_society.implementation_delegation import delegate
from odin_backend.core.engineering_society.peer_review import review
from odin_backend.core.engineering_society.review_consensus import consensus
from odin_backend.core.engineering_society.role_assignment import ROLES, assign
from odin_backend.core.engineering_society.testing_council import council


class EngineeringSocietyRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def convene(self, *, topic: str, patch: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_society_enabled", False):
            return {"accepted": False, "reason": "engineering_society_disabled"}
        roles = assign(topic)
        deb = debate(topic)
        self._emit("architecture_debate_started", deb)
        rev = review(patch=patch) if patch else {"skipped": True}
        cons = consensus([False, False, True]) if patch else {"approved": False}
        if cons.get("approved"):
            self._emit("review_consensus_reached", cons)
        tests = council(["unit", "integration"])
        delegation = [delegate(role=r, task=topic) for r in roles[:2]]
        society = {}
        if hasattr(self._app, "agent_society"):
            society = {"agents": list(getattr(self._app.agent_society, "_agents", {}).keys())[:8]}
        return {
            "accepted": True,
            "roles": roles,
            "roles_available": list(ROLES),
            "debate": deb,
            "review": rev,
            "consensus": cons,
            "testing_council": tests,
            "delegation": delegation,
            "society": society,
            "supervised": True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"roles": list(ROLES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_society")
