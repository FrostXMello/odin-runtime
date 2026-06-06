from __future__ import annotations

def stream_config(*, mode: str = "balanced") -> dict:
    return {"chunk_ms": 40 if mode == "balanced" else 25, "local_only": True}
