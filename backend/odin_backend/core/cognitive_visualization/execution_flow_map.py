from __future__ import annotations

def flow_map(*, steps: list[str]) -> dict:
    return {"steps": steps, "active": steps[0] if steps else None}
