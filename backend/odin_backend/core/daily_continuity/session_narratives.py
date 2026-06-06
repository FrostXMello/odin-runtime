from __future__ import annotations

def narrative(*, sessions: list[dict]) -> dict:
    return {"narrative": f"{len(sessions)} recent sessions", "sessions": len(sessions)}
