"""Federation governance runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.federation_governance.audit_fabric import AuditFabric
from odin_backend.core.federation_governance.constitutional_policies import POLICIES
from odin_backend.core.federation_governance.escalation_rules import should_escalate
from odin_backend.core.federation_governance.federation_guardrails import FederationGuardrails
from odin_backend.core.federation_governance.permission_matrix import check_permission
from odin_backend.core.federation_governance.trust_engine import TrustEngine


class FederationGovernanceRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._trust = TrustEngine()
        self._guardrails = FederationGuardrails(app.settings)
        self._audit = AuditFabric()
        self._quarantined: set[str] = set()
        self._violations: dict[str, int] = {}

    def allow_connection(self, node_name: str) -> tuple[bool, str]:
        ok, reason = self._guardrails.allow_operation("connect")
        if not ok:
            self._record_violation(node_name)
            return False, reason
        return True, "ok"

    def allow_remote_op(self, node_id: str, action: str, level: str = "read") -> tuple[bool, str]:
        if node_id in self._quarantined:
            return False, "node_quarantined"
        if self._guardrails.is_shutdown():
            return False, "federation_shutdown"
        if not check_permission(level, action):
            self._record_violation(node_id)
            self._emit("governance_violation", {"node_id": node_id, "action": action})
            return False, "permission_denied"
        self._audit.record(action=action, node_id=node_id)
        return True, "ok"

    def quarantine(self, node_id: str) -> dict[str, Any]:
        self._quarantined.add(node_id)
        self._trust.score(node_id, delta=-0.3)
        self._audit.record(action="quarantine", node_id=node_id)
        self._emit("node_quarantined", {"node_id": node_id})
        return {"node_id": node_id, "status": "quarantined"}

    def update_trust(self, node_id: str, *, delta: float) -> dict[str, Any]:
        score = self._trust.score(node_id, delta=delta)
        self._emit("trust_score_changed", {"node_id": node_id, "trust": score})
        return {"node_id": node_id, "trust": score}

    def _record_violation(self, node_id: str) -> None:
        self._violations[node_id] = self._violations.get(node_id, 0) + 1
        trust = self._trust.get(node_id)
        esc = should_escalate(trust=trust, violation_count=self._violations[node_id])
        if esc.get("action") == "quarantine":
            self.quarantine(node_id)

    def snapshot(self) -> dict[str, Any]:
        return {
            "trust_scores": self._trust.snapshot(),
            "quarantined": list(self._quarantined),
            "violations": dict(self._violations),
            "policies": POLICIES,
            "audit_recent": self._audit.recent(),
            "shutdown": self._guardrails.is_shutdown(),
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="federation_governance")
