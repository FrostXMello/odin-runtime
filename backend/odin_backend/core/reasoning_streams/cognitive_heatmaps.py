from __future__ import annotations

def heatmap(*, zones: dict) -> dict:
    return {"zones": zones, "max": max(zones.values()) if zones else 0}
