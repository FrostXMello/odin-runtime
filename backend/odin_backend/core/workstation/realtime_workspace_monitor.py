from __future__ import annotations

from typing import Any


def monitor_snapshot(snapshot: dict) -> dict[str, Any]:
    return {"app": snapshot.get("app"), "engineering_session": "code" in str(snapshot.get("title", "")).lower()}
