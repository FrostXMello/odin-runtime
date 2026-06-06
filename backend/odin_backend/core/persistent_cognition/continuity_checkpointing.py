from __future__ import annotations
from uuid import uuid4

def checkpoint(*, state: dict) -> dict:
    return {"checkpoint_id": str(uuid4()), "keys": list(state.keys())[:20], "created_at": state.get("created_at")}
