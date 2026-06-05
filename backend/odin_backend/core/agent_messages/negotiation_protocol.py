"""Role negotiation protocol messages."""

from __future__ import annotations

from typing import Any


def negotiate_proposal(*, proposer: str, role: str, task: str) -> dict[str, Any]:
    return {"proposer": proposer, "proposed_role": role, "task": task, "status": "proposed"}


def negotiate_accept(proposal: dict[str, Any]) -> dict[str, Any]:
    return {**proposal, "status": "accepted"}
