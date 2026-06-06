from __future__ import annotations

from typing import Any


def isolate_branch(*, prefix: str = "odin-patch") -> dict[str, Any]:
    return {"branch": f"{prefix}-isolated", "isolated": True, "main_protected": True}
