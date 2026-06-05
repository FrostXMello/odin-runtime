"""Convert recorded steps into parameterized macros."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


def steps_to_macro(steps: list[dict[str, Any]], *, name: str) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "name": name,
        "steps": steps,
        "parameters": _infer_parameters(steps),
        "version": 1,
    }


def _infer_parameters(steps: list[dict[str, Any]]) -> list[str]:
    params: set[str] = set()
    for step in steps:
        for key in step.get("payload", {}):
            if key in ("url", "text", "selector", "title"):
                params.add(key)
    return sorted(params)
