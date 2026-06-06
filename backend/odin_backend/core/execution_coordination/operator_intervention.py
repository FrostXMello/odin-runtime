from __future__ import annotations

from typing import Any


def intervention_checkpoint(*, approved: bool) -> dict[str, Any]:
    return {"allowed": approved, "checkpoint": "operator_intervention"}
