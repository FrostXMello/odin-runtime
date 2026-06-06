from __future__ import annotations

from typing import Any


def learn_habit(*, action: str, hour: int) -> dict[str, Any]:
    return {"action": action, "hour": hour, "pattern": f"often_{action}_at_{hour}"}
