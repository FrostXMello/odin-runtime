"""Evolution governance — approval checkpoints and audit trail."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.evolution_governance.modification_policies import policies
from odin_backend.core.evolution_governance.operator_review import review_packet
from odin_backend.core.evolution_governance.risk_scoring import LEVELS, score
from odin_backend.core.evolution_governance.safety_constraints import check


class EvolutionGovernanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._audit: list[dict] = []
        self._default_level = "proposal_only"

    async def review(self, *, proposal: dict, level: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "evolution_governance_enabled", False):
            return {"accepted": False, "reason": "evolution_governance_disabled"}
        lvl = level or getattr(self._app.settings, "evolution_approval_level", self._default_level)
        if lvl not in LEVELS:
            lvl = "proposal_only"
        risk = score(touches_core=proposal.get("touches_core", False), regression_risk=0.2)
        safety = check(direct_modify=proposal.get("direct_modify", False), recursion_depth=proposal.get("depth", 0))
        if not safety["allowed"]:
            return {"accepted": False, "reason": safety["blocked_reason"], "policies": policies()}
        packet = review_packet(proposal=proposal, risk=risk)
        entry = {"id": str(uuid4()), "level": lvl, "risk": risk, "packet": packet}
        self._audit.append(entry)
        return {
            "accepted": True,
            "level": lvl,
            "approval_required": lvl != "observe_only",
            "risk": risk,
            "review": packet,
            "policies": policies(),
            "audit_id": entry["id"],
        }

    async def approve(self, *, audit_id: str, operator: str = "default") -> dict[str, Any]:
        entry = next((a for a in self._audit if a["id"] == audit_id), None)
        if not entry:
            return {"accepted": False, "reason": "audit_not_found"}
        if entry["level"] == "observe_only":
            return {"accepted": False, "reason": "observe_only_level"}
        self._emit("optimization_applied", {"audit_id": audit_id, "operator": operator, "supervised": True})
        return {"accepted": True, "approved": True, "audit_id": audit_id, "no_main_commit": True}

    def snapshot(self) -> dict[str, Any]:
        return {"audit_len": len(self._audit), "default_level": self._default_level, "policies": policies()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="evolution_governance")
