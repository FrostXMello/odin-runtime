from __future__ import annotations

def presence(*, energy: float = 0.5) -> dict:
    return {"energy": round(energy, 3), "simulated": True, "disclosure": "runtime_presence"}
