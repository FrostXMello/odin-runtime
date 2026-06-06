from __future__ import annotations
from typing import Any


def visualize_upgrade(snapshot: dict) -> dict[str, Any]:
    return {"nodes": list(snapshot.keys())[:8], "approval_required": True}
