from __future__ import annotations

from typing import Any


def merge_contexts(*, ide: dict | None, terminal: dict | None, browser: dict | None) -> dict[str, Any]:
    sources = []
    signals: list[str] = []
    active_app = "unknown"
    if ide:
        sources.append("ide")
        active_app = ide.get("editor", active_app)
        if ide.get("debugging"):
            signals.append("debugging")
    if terminal:
        sources.append("terminal")
        signals.append("terminal_active")
    if browser:
        sources.append("browser")
    return {"sources": sources, "active_app": active_app, "signals": signals, "local_only": True}
