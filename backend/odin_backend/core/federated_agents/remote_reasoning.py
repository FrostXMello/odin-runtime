"""Remote reasoning delegation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class RemoteReasoning:
    def __init__(self) -> None:
        self._requests: list[dict[str, Any]] = []

    def request(self, *, from_node: str, to_node: str, query: str, mission_id: str | None = None) -> dict[str, Any]:
        req = {
            "id": str(uuid4()),
            "from_node": from_node,
            "to_node": to_node,
            "query": query,
            "mission_id": mission_id,
            "status": "pending",
            "requested_at": datetime.now(timezone.utc).isoformat(),
        }
        self._requests.append(req)
        return req

    def complete(self, request_id: str, *, result: str, confidence: float) -> dict[str, Any] | None:
        for r in self._requests:
            if r["id"] == request_id:
                r["status"] = "completed"
                r["result"] = result
                r["confidence"] = confidence
                r["completed_at"] = datetime.now(timezone.utc).isoformat()
                return r
        return None

    def list_for_mission(self, mission_id: str) -> list[dict[str, Any]]:
        return [r for r in self._requests if r.get("mission_id") == mission_id]
