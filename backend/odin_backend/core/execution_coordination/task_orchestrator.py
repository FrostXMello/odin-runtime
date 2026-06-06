from __future__ import annotations

from typing import Any


def orchestrate(*, steps: list[str]) -> dict[str, Any]:
    return {"steps": steps, "sequence": list(range(len(steps)))}
