"""Continuity recovery after restart."""

from __future__ import annotations

from typing import Any


async def recover_sessions(store: Any, snapshots: Any) -> dict[str, Any]:
    sessions = await store.list_active()
    behavioral = await snapshots.latest("behavioral")
    return {
        "sessions_restored": len(sessions),
        "behavioral_restored": behavioral is not None,
        "sessions": sessions[:10],
    }
