from __future__ import annotations
from typing import Any


async def strategy(app: Any) -> dict:
    if hasattr(app, "operator_productivity"):
        return await app.operator_productivity.summary()
    return {"strategy": "25m focus blocks"}
