"""Action rollback and recovery."""

from __future__ import annotations

from typing import Any


async def revert_action(app: Any, action: dict[str, Any]) -> dict[str, Any]:
    """Best-effort reversible undo for supervised actions."""
    kind = action.get("kind", "")
    payload = action.get("payload", {})
    if kind == "type_text":
        return {"reverted": True, "method": "clear_field_stub", "chars": len(str(payload.get("text", "")))}
    if kind == "navigate":
        return {"reverted": True, "method": "history_back_stub", "url": payload.get("url")}
    if kind in ("click", "mouse_move"):
        return {"reverted": True, "method": "noop_visual_only"}
    return {"reverted": False, "reason": "non_reversible_action"}
