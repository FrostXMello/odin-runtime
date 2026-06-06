from __future__ import annotations

from typing import Any


def replay_failure(*, command: str) -> dict[str, Any]:
    return {"command": command, "replayed": True, "sandbox": True}
