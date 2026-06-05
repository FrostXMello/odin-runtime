"""Memory chunking with importance scoring."""

from __future__ import annotations

from typing import Any


def chunk_with_importance(text: str, *, chunk_size: int = 512) -> list[dict[str, Any]]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size // 5):
        segment = " ".join(words[i : i + chunk_size // 5])
        if segment.strip():
            importance = min(1.0, len(segment) / 1000 + 0.3)
            chunks.append({"text": segment, "importance": round(importance, 4)})
    return chunks or [{"text": text[:chunk_size], "importance": 0.5}]
