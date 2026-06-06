from __future__ import annotations
from typing import Any


async def overnight(app: Any) -> dict:
    if hasattr(app, "continuous_engineering"):
        return await app.continuous_engineering.overnight()
    return {"analysis": "lightweight overnight scan"}
