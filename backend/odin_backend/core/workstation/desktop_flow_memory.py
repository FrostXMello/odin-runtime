from __future__ import annotations

from typing import Any


def record_flow(*, from_app: str | None, to_app: str) -> dict[str, Any]:
    return {"from": from_app, "to": to_app, "switch": from_app is not None and from_app != to_app}
