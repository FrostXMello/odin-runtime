"""Retrieve and normalize web content."""

from __future__ import annotations

from typing import Any


async def retrieve_sources(app: Any, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    web = getattr(app, "web_access", None)
    out: list[dict] = []
    for src in sources[:5]:
        url = src.get("url", "")
        if web:
            fetched = await web.fetch(url)
            out.append({**src, "content": fetched.get("text", "")[:2000], "status": fetched.get("status")})
        else:
            out.append({**src, "content": f"[stub] content for {url}", "status": "stub"})
    return out
