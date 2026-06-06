from __future__ import annotations

from typing import Any


def recover_interruption(*, state: dict) -> dict[str, Any]:
    return {"recovered": bool(state), "continuity": True, "resume_hint": state.get("focus", "previous task")}
