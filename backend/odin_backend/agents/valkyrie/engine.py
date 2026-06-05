"""Valkyrie execution engine — never bypasses governor, gate, or Heimdall."""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from odin_backend.core.execution_gate.gate import GateDecision
from odin_backend.core.governor.decisions import ExecutionRequest
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ValkyrieActionResult(BaseModel):
    success: bool
    execution_trace_id: str
    governor_decision: str = ""
    gate_decision: str = ""
    heimdall_check_result: str = "delegated_to_pipeline"
    tool_output: dict[str, Any] = Field(default_factory=dict)
    valkyrie_trace: list[str] = Field(default_factory=list)


class ValkyrieExecutionEngine:
    """
    Real execution layer for VALKYRIE.

    Flow: Kernel context → Governor (in pipeline) → ExecutionGate → Heimdall → Tool
    """

    def __init__(self, app: Any) -> None:
        self._app = app

    async def execute_task(
        self,
        *,
        tool_name: str,
        params: dict | None = None,
        user_confirmed: bool = False,
        task_id: str | None = None,
    ) -> ValkyrieActionResult:
        if not self._app.env_config.valkyrie_enabled:
            return ValkyrieActionResult(
                success=False,
                execution_trace_id=str(uuid4()),
                valkyrie_trace=["valkyrie_disabled"],
            )
        return await self._run_governed(
            tool_name,
            params or {},
            user_confirmed=user_confirmed,
            task_id=task_id,
            action="execute_task",
        )

    async def execute_tool_chain(
        self,
        steps: list[dict[str, Any]],
        *,
        user_confirmed: bool = False,
    ) -> list[ValkyrieActionResult]:
        results: list[ValkyrieActionResult] = []
        for step in steps:
            result = await self.execute_task(
                tool_name=step["tool"],
                params=step.get("params", {}),
                user_confirmed=user_confirmed or step.get("user_confirmed", False),
                task_id=step.get("task_id"),
            )
            results.append(result)
            if not result.success:
                break
        return results

    async def execute_desktop_action(
        self,
        action: str,
        params: dict | None = None,
        *,
        user_confirmed: bool = False,
    ) -> ValkyrieActionResult:
        if not self._app.env_config.allows_desktop_execution():
            return ValkyrieActionResult(
                success=False,
                execution_trace_id=str(uuid4()),
                valkyrie_trace=["desktop_control_blocked"],
            )
        tool_map = {
            "screenshot": "get_system_info",
            "list": "list_directory",
            "read": "read_file",
        }
        tool_name = tool_map.get(action, "list_directory")
        return await self._run_governed(
            tool_name,
            params or {},
            user_confirmed=user_confirmed,
            action=f"desktop.{action}",
        )

    async def execute_browser_action(
        self,
        action: str,
        params: dict | None = None,
        *,
        user_confirmed: bool = False,
    ) -> ValkyrieActionResult:
        if not self._app.env_config.desktop_control_enabled:
            return ValkyrieActionResult(
                success=False,
                execution_trace_id=str(uuid4()),
                valkyrie_trace=["browser_blocked"],
            )
        tool_map = {
            "open": "open_browser",
            "tabs": "get_browser_tabs",
            "extract": "extract_tab_content",
        }
        tool_name = tool_map.get(action, "get_browser_tabs")
        return await self._run_governed(
            tool_name,
            params or {},
            user_confirmed=user_confirmed,
            action=f"browser.{action}",
        )

    async def _run_governed(
        self,
        tool_name: str,
        params: dict,
        *,
        user_confirmed: bool,
        task_id: str | None,
        action: str,
    ) -> ValkyrieActionResult:
        trace_id = str(uuid4())
        trace = [f"valkyrie:{action}", f"tool:{tool_name}"]

        gate = self._app.execution_gate.validate(
            self._app,
            ExecutionRequest(
                tool_name=tool_name,
                agent_id=str(AgentId.VALKYRIE),
                params=params,
                task_id=task_id,
                user_confirmed=user_confirmed,
            ),
        )
        trace.append(f"gate:{gate.decision.value}")

        if gate.decision != GateDecision.ALLOW:
            return ValkyrieActionResult(
                success=False,
                execution_trace_id=trace_id,
                gate_decision=gate.decision.value,
                valkyrie_trace=trace,
                tool_output={"reason": gate.reason},
            )

        pipeline_result = await self._app.live_tools.execute_with_trace(
            self._app,
            tool_name,
            params,
            agent_id=str(AgentId.VALKYRIE),
            task_id=task_id,
            user_confirmed=user_confirmed,
            execution_trace_id=trace_id,
        )

        trace.extend(pipeline_result.get("valkyrie_trace", []))
        return ValkyrieActionResult(
            success=pipeline_result.get("success", False),
            execution_trace_id=trace_id,
            governor_decision=pipeline_result.get("governor_decision", ""),
            gate_decision=gate.decision.value,
            heimdall_check_result=pipeline_result.get("heimdall_check_result", ""),
            tool_output=pipeline_result.get("tool_output", {}),
            valkyrie_trace=trace,
        )
