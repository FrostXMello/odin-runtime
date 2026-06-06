from __future__ import annotations
from typing import Any


class RefactorSimulationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def simulate(self, *, scope: str) -> dict[str, Any]:
        if hasattr(self._app, "self_improvement_sandbox"):
            await self._app.self_improvement_sandbox.experiment(name="refactor-sim")
        return {"accepted": True, "scope": scope[:120], "sandbox_branch": True}
