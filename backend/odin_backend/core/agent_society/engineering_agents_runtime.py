"""Engineering agents orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.agent_society.engineering_agents import AGENTS, route_engineering_task


class EngineeringAgentsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._delegations = 0

    async def delegate(self, *, task: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_agents_enabled", False):
            return {"accepted": False, "reason": "engineering_agents_disabled"}
        routed = route_engineering_task(task)
        self._delegations += 1
        if hasattr(self._app, "autonomy_reliability"):
            viability = await self._app.autonomy_reliability.assess_task(
                complexity=1.0 - routed["score"], action=task, destructive=False
            )
            routed["viability"] = viability
        return {"accepted": True, **routed, "agents_available": len(AGENTS), "supervised": True}

    def snapshot(self) -> dict[str, Any]:
        return {"delegations": self._delegations, "agents": len(AGENTS)}
