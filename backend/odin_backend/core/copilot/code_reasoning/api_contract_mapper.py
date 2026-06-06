from __future__ import annotations

from typing import Any


def map_api_contracts(*, files: list[str]) -> dict[str, Any]:
    routes = [f for f in files if "routes" in f or "api" in f]
    return {"route_modules": len(routes), "contracts_estimated": len(routes) * 3}
