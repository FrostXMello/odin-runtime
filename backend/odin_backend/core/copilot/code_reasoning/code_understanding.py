"""Code understanding helpers."""

from __future__ import annotations

from typing import Any


def understand_code(*, content: str, path: str) -> dict[str, Any]:
    lines = content.splitlines()
    funcs = sum(1 for l in lines if l.strip().startswith(("def ", "async def ", "function ", "class ")))
    return {
        "path": path,
        "lines": len(lines),
        "symbols": funcs,
        "language": path.split(".")[-1] if "." in path else "unknown",
    }
