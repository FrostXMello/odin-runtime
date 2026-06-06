"""Operator shell orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.operator_shell.command_router import route_command
from odin_backend.core.operator_shell.natural_command_parser import parse_natural
from odin_backend.core.operator_shell.quick_actions import list_actions
from odin_backend.core.operator_shell.runtime_search_router import search_route
from odin_backend.core.operator_shell.semantic_shortcuts import SHORTCUTS


class OperatorShellRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._history: list[str] = []

    async def execute(self, command: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "operator_shell_enabled", False):
            return {"accepted": False, "reason": "operator_shell_disabled"}
        self._history.append(command)
        routed = route_command(command)
        parsed = parse_natural(command)
        result: dict[str, Any] = {"route": routed, "parsed": parsed}
        if parsed["intent"] == "resume" and hasattr(self._app, "copilot_production"):
            result["action"] = await self._app.copilot_production.resume_session()
        elif parsed["intent"] == "optimize" and hasattr(self._app, "performance"):
            result["action"] = await self._app.performance.optimize()
        elif parsed["intent"] == "diagnostics" and hasattr(self._app, "runtime_guardian"):
            result["action"] = await self._app.runtime_guardian.supervise()
        else:
            result["action"] = await search_route(self._app, command)
        self._emit("command_executed", {"command": command[:80], "intent": parsed["intent"]})
        return {"accepted": True, **result}

    def quick_actions(self) -> list[dict[str, Any]]:
        return list_actions()

    def shortcuts(self) -> dict[str, str]:
        return dict(SHORTCUTS)

    def snapshot(self) -> dict[str, Any]:
        return {"history": len(self._history), "shortcuts": len(SHORTCUTS)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="operator_shell")
