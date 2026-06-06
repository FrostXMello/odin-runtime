from __future__ import annotations
from typing import Any


async def reflect(app: Any) -> dict:
    if hasattr(app, "cognitive_streams"):
        return await app.cognitive_streams.reflect_stream(summary="background reflection")
    return {"reflection": "deferred"}
