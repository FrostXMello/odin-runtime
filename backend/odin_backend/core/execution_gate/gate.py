"""Execution gate — environment-aware safety before VALKYRIE dispatch."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.governor.decisions import ExecutionRequest

OS_MUTATION_TOOLS = frozenset(
    {
        "execute_terminal",
        "write_file",
        "open_browser",
        "take_screenshot",
    }
)
DESKTOP_TOOLS = frozenset(
    {
        "take_screenshot",
        "open_browser",
        "get_browser_tabs",
        "extract_tab_content",
    }
)
READ_ONLY_TOOLS = frozenset(
    {
        "read_file",
        "list_directory",
        "get_system_info",
        "search_web",
        "summarize_content",
    }
)


class GateDecision(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"
    ESCALATE = "escalate"
    REQUIRE_CONFIRMATION = "require_confirmation"


class GateResult(BaseModel):
    decision: GateDecision
    reason: str
    explainable: dict[str, Any] = Field(default_factory=dict)


class ExecutionGate:
    """Validates execution against environment config, autonomy, and risk."""

    def validate(self, app: Any, request: ExecutionRequest) -> GateResult:
        env = app.env_config
        explain: dict[str, Any] = {
            "tool": request.tool_name,
            "env_snapshot": env.snapshot(),
        }

        if not env.valkyrie_enabled and request.tool_name not in READ_ONLY_TOOLS:
            return GateResult(
                decision=GateDecision.BLOCK,
                reason="VALKYRIE disabled — only read-only tools permitted",
                explainable=explain,
            )

        if request.tool_name in DESKTOP_TOOLS and not env.desktop_control_enabled:
            return GateResult(
                decision=GateDecision.BLOCK,
                reason="Desktop control disabled (ODIN_DESKTOP_CONTROL_ENABLED=false)",
                explainable=explain,
            )

        if request.tool_name in OS_MUTATION_TOOLS:
            if not env.allows_os_mutation():
                return GateResult(
                    decision=GateDecision.BLOCK,
                    reason="OS-level mutation blocked by environment policy",
                    explainable=explain,
                )
            if not request.user_confirmed:
                return GateResult(
                    decision=GateDecision.REQUIRE_CONFIRMATION,
                    reason=f"High-risk tool '{request.tool_name}' requires explicit confirmation",
                    explainable=explain,
                )

        if app.autonomy.current_level <= 1 and request.tool_name not in READ_ONLY_TOOLS:
            return GateResult(
                decision=GateDecision.BLOCK,
                reason="Autonomy level too low for this execution",
                explainable=explain,
            )

        state = app.kernel.get_state()
        if state.coherence_snapshot.get("conflicts"):
            return GateResult(
                decision=GateDecision.ESCALATE,
                reason="Coherence conflicts must be resolved before real execution",
                explainable={**explain, "conflicts": state.coherence_conflicts},
            )

        if state.system_health.get("degraded") and request.tool_name in OS_MUTATION_TOOLS:
            return GateResult(
                decision=GateDecision.ESCALATE,
                reason="System degraded — OS actions escalated to user",
                explainable=explain,
            )

        return GateResult(
            decision=GateDecision.ALLOW,
            reason="Execution gate open",
            explainable=explain,
        )
