from __future__ import annotations

from typing import Any


def map_services(*, files: list[str]) -> dict[str, Any]:
    services = [f for f in files if "service" in f.lower() or "runtime" in f.lower()]
    return {"services": services[:10], "count": len(services)}
