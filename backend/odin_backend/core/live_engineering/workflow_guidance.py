from __future__ import annotations

def guide(*, step: str) -> dict:
    return {"step": step, "next": "validate" if step == "patch" else "test"}
