"""Builds WorkflowPlan from structured LLM or rule-based output."""

from typing import Any

from odin_backend.models.task import AgentId
from odin_backend.models.workflow import StepStatus, WorkflowPlan, WorkflowPlanStep
from odin_backend.orchestrator.reasoning.tool_selector import TOOL_AGENT_MAP, ToolSelector


class WorkflowBuilder:
    def __init__(self) -> None:
        self._selector = ToolSelector()

    def from_llm_json(self, data: dict[str, Any], correlation_id: str | None = None) -> WorkflowPlan:
        objective = data.get("objective", "Unnamed objective")
        raw_steps = data.get("steps", [])
        steps: list[WorkflowPlanStep] = []

        for i, raw in enumerate(raw_steps, start=1):
            agent_str = str(raw.get("agent", "VALKYRIE")).upper()
            try:
                agent = AgentId(agent_str.lower())
            except ValueError:
                agent = AgentId.VALKYRIE

            tool = raw.get("tool", "")
            if tool and tool not in TOOL_AGENT_MAP:
                agent = self._selector.agent_for_tool(tool)
            elif tool:
                agent = TOOL_AGENT_MAP.get(tool, agent)

            steps.append(
                WorkflowPlanStep(
                    step_id=int(raw.get("step_id", i)),
                    agent=agent,
                    tool=tool,
                    description=raw.get("description", ""),
                    params=raw.get("params", {}),
                    status=StepStatus(raw.get("status", "pending")),
                    depends_on=raw.get("depends_on", []),
                )
            )

        return WorkflowPlan(objective=objective, steps=steps, correlation_id=correlation_id)

    def from_rule_based(self, objective: str, correlation_id: str | None = None) -> WorkflowPlan:
        """Deterministic fallback when LLM unavailable."""
        selector = ToolSelector()
        hints = selector.suggest_tools(objective)
        steps: list[WorkflowPlanStep] = []

        if not hints:
            steps.append(
                WorkflowPlanStep(
                    step_id=1,
                    agent=AgentId.HUGIN,
                    tool="search_web",
                    description="Research objective",
                    params={"query": objective},
                )
            )
            steps.append(
                WorkflowPlanStep(
                    step_id=2,
                    agent=AgentId.MUNIN,
                    tool="summarize_content",
                    description="Summarize findings",
                    params={"text": "{{step_1.output}}"},
                    depends_on=[1],
                )
            )
        else:
            for i, (tool, agent) in enumerate(hints, start=1):
                steps.append(
                    WorkflowPlanStep(
                        step_id=i,
                        agent=agent,
                        tool=tool,
                        description=f"Execute {tool}",
                        params={"query": objective} if tool == "search_web" else {},
                        depends_on=[i - 1] if i > 1 else [],
                    )
                )

        # Browser tab + email pattern
        lower = objective.lower()
        if "browser" in lower and "tab" in lower:
            steps = [
                WorkflowPlanStep(
                    step_id=1,
                    agent=AgentId.VALKYRIE,
                    tool="get_browser_tabs",
                    description="Collect open browser tabs",
                ),
                WorkflowPlanStep(
                    step_id=2,
                    agent=AgentId.HUGIN,
                    tool="extract_tab_content",
                    description="Extract tab content",
                    depends_on=[1],
                ),
                WorkflowPlanStep(
                    step_id=3,
                    agent=AgentId.MUNIN,
                    tool="summarize_content",
                    description="Summarize important findings",
                    depends_on=[2],
                ),
            ]
            if "email" in lower:
                steps.append(
                    WorkflowPlanStep(
                        step_id=4,
                        agent=AgentId.BRAGI,
                        tool="generate_email",
                        description="Generate email with findings",
                        depends_on=[3],
                    )
                )

        return WorkflowPlan(objective=objective, steps=steps, correlation_id=correlation_id)
