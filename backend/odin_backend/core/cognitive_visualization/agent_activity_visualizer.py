from __future__ import annotations

def agent_graph(*, agents: list[str]) -> dict:
    return {"agents": agents, "links": len(agents)}
