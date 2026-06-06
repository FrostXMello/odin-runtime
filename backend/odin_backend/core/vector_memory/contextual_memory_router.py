"""Route memory queries to appropriate stores."""

from __future__ import annotations

from typing import Any


def route_query(*, query: str, has_project: bool, session_active: bool) -> dict[str, Any]:
    stores = ["long_term", "semantic"]
    if has_project:
        stores.append("project")
    if session_active:
        stores.insert(0, "active_session")
    if "yesterday" in query.lower() or "last week" in query.lower():
        stores.append("episodic")
    return {"stores": stores, "boost_session": session_active}
