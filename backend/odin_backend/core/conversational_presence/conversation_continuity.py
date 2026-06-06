from __future__ import annotations
from typing import Any


async def restore_context(app: Any) -> dict[str, Any]:
    if hasattr(app, "conversational_os") and hasattr(app.conversational_os, "restore"):
        return await app.conversational_os.restore(thread_id="")
    if hasattr(app, "persistent_cognition"):
        return await app.persistent_cognition.rehydrate_session()
    return {"restored": False}
