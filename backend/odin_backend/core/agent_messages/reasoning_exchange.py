"""Reasoning exchange between agents."""

from __future__ import annotations

from typing import Any


def share_reasoning(*, agent_id: str, chain: list[str]) -> dict[str, Any]:
    return {"agent_id": agent_id, "reasoning_chain": chain[:10], "shared": True}
