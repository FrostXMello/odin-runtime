"""Web search tool."""

from typing import Any
from urllib.parse import quote_plus

import httpx

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult


class SearchWebTool(Tool):
    name = "search_web"
    description = "Search the web for information"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        query = params.get("query", "")
        if not query:
            return ToolResult(success=False, error="query required")

        try:
            # DuckDuckGo instant answer API (no key required)
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()

            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", ""),
                    "snippet": data.get("AbstractText", ""),
                    "url": data.get("AbstractURL", ""),
                })
            for topic in (data.get("RelatedTopics") or [])[:5]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({"snippet": topic["Text"], "url": topic.get("FirstURL", "")})

            return ToolResult(success=True, data={"query": query, "results": results})
        except Exception as exc:
            return ToolResult(success=True, data={"query": query, "results": [], "note": str(exc)})
