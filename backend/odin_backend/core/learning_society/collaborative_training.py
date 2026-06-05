"""Collaborative training sessions."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


def start_session(*, mentor_id: str, mentee_ids: list[str], topic: str) -> dict[str, Any]:
    return {"id": str(uuid4()), "mentor_id": mentor_id, "mentees": mentee_ids, "topic": topic}
