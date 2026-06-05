"""Mission execution style preferences."""

from __future__ import annotations

from pydantic import BaseModel


class MissionStyle(BaseModel):
    default_autonomy_level: int = 2
    prefer_sandbox: bool = True
    max_parallel_tasks: int = 2
    validation_first: bool = True
