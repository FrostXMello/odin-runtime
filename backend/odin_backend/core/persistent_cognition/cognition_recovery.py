from __future__ import annotations

def recover(*, checkpoints: list[dict]) -> dict:
    return {"recovered": bool(checkpoints), "count": len(checkpoints)}
