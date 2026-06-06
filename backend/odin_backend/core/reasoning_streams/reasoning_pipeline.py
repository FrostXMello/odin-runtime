from __future__ import annotations

def pipeline(*, steps: list[str]) -> dict:
    return {"steps": steps[:12], "explainable": True}
