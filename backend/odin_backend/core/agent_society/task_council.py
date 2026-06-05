"""Task council for role negotiation."""

from __future__ import annotations

from typing import Any


class TaskCouncil:
    async def negotiate_roles(self, agents: list[dict[str, Any]], *, task: str) -> list[dict[str, str]]:
        assignments: list[dict] = []
        for i, agent in enumerate(agents):
            role = agent.get("role", "generalist")
            assignments.append(
                {
                    "agent_id": agent.get("agent_id", ""),
                    "assigned_role": role,
                    "task_slice": f"{task} (part {i + 1})",
                }
            )
        return assignments
