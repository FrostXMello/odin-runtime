from __future__ import annotations
from typing import Any


class ContinuousReasoningRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def update(self, *, thought: str) -> dict[str, Any]:
        if hasattr(self._app, "cognitive_streams"):
            await self._app.cognitive_streams.push(thought=thought)
        return {"accepted": True, "thought": thought[:120]}
