from __future__ import annotations

from typing import Any


def stream_reason(*, prompt: str, depth: str) -> list[str]:
    return [f"[{depth}]{prompt[:40]}"]
