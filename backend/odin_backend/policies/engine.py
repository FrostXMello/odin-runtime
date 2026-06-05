"""Contextual policy engine — explainable security decisions."""

from pathlib import Path
from typing import Any

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.permissions.heimdall import HeimdallService
from odin_backend.policies.models import PolicyDecision, PolicyRule, PolicyScope
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

DEFAULT_POLICIES: list[PolicyRule] = [
    PolicyRule(
        id="terminal_workspace",
        name="Terminal restricted to workspace",
        scope=PolicyScope.TERMINAL,
        description="Terminal execution only within sandbox work directory",
        constraints={"allowed_cwd_prefix": "./data/sandbox"},
    ),
    PolicyRule(
        id="browser_domain",
        name="Browser automation domain restrictions",
        scope=PolicyScope.BROWSER,
        description="Block automation on sensitive domains",
        constraints={"blocked_domains": ["bank", "paypal", "auth"]},
    ),
    PolicyRule(
        id="fs_write_sandbox",
        name="Filesystem write restrictions",
        scope=PolicyScope.FILESYSTEM,
        description="Writes limited to project and data directories",
        constraints={"writable_prefixes": ["./data", "./odin"]},
    ),
    PolicyRule(
        id="workflow_approval",
        name="Dangerous workflow approval",
        scope=PolicyScope.WORKFLOW,
        description="High-risk tools require explicit approval",
        constraints={"require_approval_tools": ["execute_terminal", "send_email", "write_file"]},
    ),
]


class PolicyEngine:
    """Evaluates contextual policies before Heimdall execution."""

    def __init__(
        self,
        settings: Settings,
        event_bus: EventBus,
        heimdall: HeimdallService,
    ) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._heimdall = heimdall
        self._rules: dict[str, PolicyRule] = {r.id: r for r in DEFAULT_POLICIES}
        self._workflow_scopes: dict[str, dict[str, Any]] = {}

    def list_policies(self) -> list[PolicyRule]:
        return list(self._rules.values())

    def set_workflow_scope(self, workflow_id: str, scope: dict[str, Any]) -> None:
        self._workflow_scopes[workflow_id] = scope

    async def evaluate(
        self,
        tool_name: str,
        *,
        params: dict[str, Any] | None = None,
        workflow_id: str | None = None,
        agent_id: AgentId = AgentId.ODIN,
    ) -> PolicyDecision:
        params = params or {}

        if tool_name == "execute_terminal":
            decision = self._check_terminal(params)
            if not decision.allowed:
                await self._emit_denied(decision, tool_name)
                return decision

        if tool_name in ("open_browser", "extract_tab_content", "get_browser_tabs"):
            url = str(params.get("url", ""))
            decision = self._check_browser(url)
            if not decision.allowed:
                await self._emit_denied(decision, tool_name)
                return decision

        if tool_name == "write_file":
            path = str(params.get("path", ""))
            decision = self._check_filesystem(path)
            if not decision.allowed:
                await self._emit_denied(decision, tool_name)
                return decision

        wf_rule = self._rules.get("workflow_approval")
        if wf_rule and wf_rule.enabled and tool_name in wf_rule.constraints.get(
            "require_approval_tools", []
        ):
            return PolicyDecision(
                allowed=True,
                rule_id=wf_rule.id,
                rule_name=wf_rule.name,
                reason="Requires Heimdall user confirmation",
                explainable={
                    "policy": wf_rule.name,
                    "workflow_id": workflow_id,
                    "tool": tool_name,
                },
                remediation="Confirm execution in the permissions panel",
            )

        return PolicyDecision(allowed=True, reason="Policy checks passed")

    def _check_terminal(self, params: dict[str, Any]) -> PolicyDecision:
        rule = self._rules["terminal_workspace"]
        cwd = str(params.get("cwd", ""))
        prefix = rule.constraints.get("allowed_cwd_prefix", "")
        if cwd and prefix and not cwd.replace("\\", "/").startswith(prefix.replace("\\", "/")):
            return PolicyDecision(
                allowed=False,
                rule_id=rule.id,
                rule_name=rule.name,
                reason=f"Terminal cwd '{cwd}' outside allowed workspace",
                explainable={"cwd": cwd, "allowed_prefix": prefix},
                remediation=f"Set cwd under {prefix} or use DEV_SANDBOX profile",
            )
        return PolicyDecision(allowed=True)

    def _check_browser(self, url: str) -> PolicyDecision:
        rule = self._rules["browser_domain"]
        blocked = rule.constraints.get("blocked_domains", [])
        url_lower = url.lower()
        for domain in blocked:
            if domain in url_lower:
                return PolicyDecision(
                    allowed=False,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    reason=f"Browser automation blocked for domain pattern '{domain}'",
                    explainable={"url": url, "blocked_pattern": domain},
                    remediation="Use read-only tab inspection or manual browsing",
                )
        return PolicyDecision(allowed=True)

    def _check_filesystem(self, path: str) -> PolicyDecision:
        rule = self._rules["fs_write_sandbox"]
        prefixes = rule.constraints.get("writable_prefixes", [])
        normalized = Path(path).as_posix()
        if not any(normalized.startswith(p.replace("\\", "/")) for p in prefixes):
            return PolicyDecision(
                allowed=False,
                rule_id=rule.id,
                rule_name=rule.name,
                reason=f"Write to '{path}' outside allowed directories",
                explainable={"path": path, "allowed_prefixes": prefixes},
                remediation="Write files under ./data or project directory only",
            )
        return PolicyDecision(allowed=True)

    async def _emit_denied(self, decision: PolicyDecision, tool_name: str) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.POLICY_DENIED,
                source=AgentId.HEIMDALL,
                payload={
                    "tool": tool_name,
                    "decision": decision.model_dump(),
                },
            )
        )

    def explain_block(self, decision: PolicyDecision) -> dict[str, Any]:
        return {
            "blocked": not decision.allowed,
            "rule": decision.rule_name,
            "reason": decision.reason,
            "explainable": decision.explainable,
            "how_to_proceed": decision.remediation,
        }
