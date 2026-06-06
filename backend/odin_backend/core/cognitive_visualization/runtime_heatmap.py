from __future__ import annotations

def heatmap(*, load: float) -> dict:
    return {"load": round(load, 3), "zones": ["cognition", "memory", "execution"]}
