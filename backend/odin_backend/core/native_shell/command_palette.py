from __future__ import annotations
from typing import Any

def palette(*, query: str, workspace: dict | None = None) -> dict[str, Any]:
    ws = workspace or {}
    actions = ["open mission", "run benchmark", "toggle focus mode", "restore session"]
    matched = [a for a in actions if query.lower() in a or not query]
    return {"query": query[:80], "actions": matched[:8], "workspace_app": ws.get("active_app", "unknown")}
