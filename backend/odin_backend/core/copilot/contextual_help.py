"""Contextual help generation."""

from __future__ import annotations

from typing import Any


def generate_help(*, app: str, task: str) -> dict[str, Any]:
    return {"app": app, "help": f"Assistance for {task} in {app}", "simulation_only": True}
