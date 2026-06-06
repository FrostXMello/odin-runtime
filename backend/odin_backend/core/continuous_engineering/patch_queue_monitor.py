from __future__ import annotations
from typing import Any


def monitor(app: Any) -> dict:
    pending = 0
    if hasattr(app, "autonomous_patching"):
        snap = app.autonomous_patching.snapshot()
        pending = len(snap.get("proposals", [])) if isinstance(snap, dict) else 0
    return {"pending_patches": pending, "auto_apply": False}
