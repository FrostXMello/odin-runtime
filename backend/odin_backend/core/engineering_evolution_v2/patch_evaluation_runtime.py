from __future__ import annotations
from typing import Any

from odin_backend.core.engineering_evolution_v2.upgrade_safety_analyzer import analyze


class PatchEvaluationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def evaluate(self, *, patch: str) -> dict[str, Any]:
        safety = analyze(patch=patch)
        return {"accepted": True, "patch": patch[:120], "safety": safety, "approval_checkpoint": True}
