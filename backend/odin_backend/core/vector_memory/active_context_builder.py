"""Build active context from session + project + retrieval."""

from __future__ import annotations

from typing import Any


def build_active_context(
    *,
    session: dict[str, Any] | None,
    project: dict[str, Any] | None,
    retrieval: list[dict[str, Any]],
) -> dict[str, Any]:
    ctx: dict[str, Any] = {"memories": retrieval[:8], "tokens_estimate": 0}
    if session:
        ctx["session"] = session
        ctx["tokens_estimate"] += 200
    if project:
        ctx["project"] = {"id": project.get("id"), "name": project.get("name")}
        ctx["tokens_estimate"] += 150
    ctx["tokens_estimate"] += len(retrieval) * 80
    return ctx
