"""Stitched multimodal context for reasoning."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class MultimodalContext:
    def __init__(self) -> None:
        self._blocks: dict[str, Any] = {}
        self._updated_at: datetime | None = None

    def stitch(self, **blocks: Any) -> None:
        for key, value in blocks.items():
            if value:
                self._blocks[key] = value
        self._updated_at = datetime.now(timezone.utc)

    def snapshot(self) -> dict[str, Any]:
        return {
            "blocks": list(self._blocks.keys()),
            "updated_at": self._updated_at.isoformat() if self._updated_at else None,
            "summary": self._summarize(),
        }

    def _summarize(self) -> str:
        parts: list[str] = []
        if "desktop" in self._blocks:
            d = self._blocks["desktop"]
            parts.append(f"Active: {d.get('active_window', 'unknown')}")
        if "workspace" in self._blocks:
            w = self._blocks["workspace"]
            parts.append(f"Session: {w.get('session_id', '—')}")
        if "visual" in self._blocks:
            parts.append(f"Visual memories: {len(self._blocks['visual'])}")
        return "; ".join(parts) or "No multimodal context yet"

    def prompt_block(self) -> str:
        return self._summarize()
