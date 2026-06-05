"""Execution policy — dangerous objective blocking and approval gates."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyVerdict(StrEnum):
    ALLOW = "allow"
    APPROVAL_REQUIRED = "approval_required"
    DENY = "deny"
    SANDBOX_ONLY = "sandbox_only"


RESTRICTED_PATTERNS: list[tuple[re.Pattern[str], RiskLevel, str]] = [
    (re.compile(r"\bdelete\s+(the\s+)?database\b", re.I), RiskLevel.CRITICAL, "database_deletion"),
    (re.compile(r"\bwipe\s+memory\b", re.I), RiskLevel.CRITICAL, "memory_wipe"),
    (re.compile(r"\b(drop|truncate)\s+table\b", re.I), RiskLevel.CRITICAL, "sql_destruction"),
    (re.compile(r"\brm\s+-rf\b", re.I), RiskLevel.CRITICAL, "filesystem_destruction"),
    (re.compile(r"\bformat\s+(disk|drive)\b", re.I), RiskLevel.CRITICAL, "disk_format"),
    (re.compile(r"\b(exfiltrat|leak|dump).{0,20}(credential|password|secret|api.?key)\b", re.I), RiskLevel.CRITICAL, "credential_exposure"),
    (re.compile(r"\bshell\s+escalat", re.I), RiskLevel.CRITICAL, "shell_escalation"),
    (re.compile(r"\bshutdown\s+(production|server|system)\b", re.I), RiskLevel.HIGH, "system_shutdown"),
    (re.compile(r"\bdelete\s+production\b", re.I), RiskLevel.CRITICAL, "production_delete"),
]

RESTRICTED_TOOLS = frozenset(
    {
        "execute_terminal",
        "write_file",
        "delete_file",
    }
)


class PolicyAssessment(BaseModel):
    verdict: PolicyVerdict
    risk_level: RiskLevel = RiskLevel.LOW
    reasons: list[str] = Field(default_factory=list)
    matched_rules: list[str] = Field(default_factory=list)
    requires_human_approval: bool = False
    sandbox_only: bool = False


class ExecutionPolicyEnforcer:
    """Mandatory policy layer before mission planning/execution."""

    def __init__(self) -> None:
        self._violations: list[dict[str, Any]] = []

    @property
    def violation_count(self) -> int:
        return len(self._violations)

    def assess_objective(self, objective: str, *, human_approved: bool = False) -> PolicyAssessment:
        reasons: list[str] = []
        rules: list[str] = []
        risk = RiskLevel.LOW

        for pattern, level, rule_id in RESTRICTED_PATTERNS:
            if pattern.search(objective):
                rules.append(rule_id)
                reasons.append(f"matched restricted pattern: {rule_id}")
                if level == RiskLevel.CRITICAL:
                    risk = RiskLevel.CRITICAL
                elif level == RiskLevel.HIGH and risk != RiskLevel.CRITICAL:
                    risk = RiskLevel.HIGH

        if risk == RiskLevel.CRITICAL:
            if not human_approved:
                self._log_violation(objective, "approval_required", rules)
                return PolicyAssessment(
                    verdict=PolicyVerdict.APPROVAL_REQUIRED,
                    risk_level=risk,
                    reasons=reasons,
                    matched_rules=rules,
                    requires_human_approval=True,
                )
            self._log_violation(objective, "critical_approved", rules)
            return PolicyAssessment(
                verdict=PolicyVerdict.SANDBOX_ONLY,
                risk_level=risk,
                reasons=reasons + ["human approved — sandbox execution only"],
                matched_rules=rules,
                sandbox_only=True,
            )

        if risk == RiskLevel.HIGH and not human_approved:
            return PolicyAssessment(
                verdict=PolicyVerdict.APPROVAL_REQUIRED,
                risk_level=risk,
                reasons=reasons,
                matched_rules=rules,
                requires_human_approval=True,
            )

        return PolicyAssessment(verdict=PolicyVerdict.ALLOW, risk_level=risk, reasons=reasons, matched_rules=rules)

    def assess_tool(self, tool_name: str, objective: str, *, human_approved: bool) -> PolicyAssessment:
        base = self.assess_objective(objective, human_approved=human_approved)
        if base.verdict != PolicyVerdict.ALLOW:
            return base
        if tool_name in RESTRICTED_TOOLS:
            obj_assess = self.assess_objective(objective, human_approved=human_approved)
            if obj_assess.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                return obj_assess
            if not human_approved:
                return PolicyAssessment(
                    verdict=PolicyVerdict.APPROVAL_REQUIRED,
                    risk_level=RiskLevel.MEDIUM,
                    reasons=[f"restricted tool {tool_name} requires approval"],
                    requires_human_approval=True,
                )
        return base

    def _log_violation(self, objective: str, action: str, rules: list[str]) -> None:
        entry = {
            "action": action,
            "objective_preview": objective[:120],
            "rules": rules,
        }
        self._violations.append(entry)
        logger.warning("execution_policy_violation", **entry)
