from __future__ import annotations

def resume(*, chains: list[dict]) -> dict:
    return {"chains": len(chains), "resumed": bool(chains)}
