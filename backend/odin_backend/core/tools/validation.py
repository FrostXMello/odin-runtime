"""Tool input/output validation helpers."""

from __future__ import annotations

from typing import Any


def validate_tool_input(spec: dict[str, Any], params: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = spec.get("required") or []
    properties = spec.get("properties") or {}
    if isinstance(required, list):
        for key in required:
            if key not in params:
                errors.append(f"missing required param: {key}")
    for key, val in params.items():
        if key in properties:
            ptype = properties[key].get("type")
            if ptype == "string" and not isinstance(val, str):
                errors.append(f"{key} must be string")
    return len(errors) == 0, errors


def validate_tool_output(data: dict[str, Any], *, schema: dict[str, Any] | None = None) -> tuple[bool, str]:
    if not data:
        return False, "empty output"
    if data.get("error"):
        return False, str(data["error"])
    if schema and schema.get("required"):
        for key in schema["required"]:
            if key not in data:
                return False, f"missing output key: {key}"
    return True, "ok"
