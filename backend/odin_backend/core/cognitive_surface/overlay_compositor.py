from __future__ import annotations

def compose(*, layers: list[str]) -> dict:
    return {"layers": layers, "gpu_safe": True}
