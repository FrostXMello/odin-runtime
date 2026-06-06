from __future__ import annotations

from typing import Any


def allocate_budget(*, vram_mb: int, on_battery: bool) -> dict[str, Any]:
    tokens = 2048 if vram_mb < 4096 or on_battery else 4096
    return {"context_tokens": tokens, "cpu_fallback": on_battery}
