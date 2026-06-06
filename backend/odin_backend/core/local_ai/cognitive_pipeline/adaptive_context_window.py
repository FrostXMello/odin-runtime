from __future__ import annotations

from typing import Any


def compress_context(*, text: str, max_tokens: int) -> dict[str, Any]:
    trimmed = text[: max_tokens * 4]
    return {"text": trimmed, "compressed": len(trimmed) < len(text)}
