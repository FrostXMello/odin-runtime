"""Web access runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.web_access.cache import FetchCache
from odin_backend.core.web_access.rate_limiter import RateLimiter
from odin_backend.core.web_access.request_scheduler import RequestScheduler
from odin_backend.core.web_access.safe_fetch import safe_fetch
from odin_backend.core.web_access.search_provider import search as search_provider


class WebAccessRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._limiter = RateLimiter(max_per_minute=getattr(app.settings, "web_rate_limit_per_minute", 20))
        self._cache = FetchCache()
        self._scheduler = RequestScheduler(app)

    async def fetch(self, url: str) -> dict[str, Any]:
        if not self._limiter.allow():
            return {"status": "rate_limited", "blocked": True, "url": url}
        cached = self._cache.get(url)
        if cached:
            return {**cached, "cached": True}
        result = await self._scheduler.run(safe_fetch(self._app, url))
        if result.get("status") in ("ok", "stub"):
            self._cache.set(url, result)
        return result

    async def search(self, topic: str) -> list[dict[str, Any]]:
        if not self._limiter.allow():
            return []
        return await search_provider(topic)

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": getattr(self._app.settings, "web_access_enabled", False),
            "read_only": True,
            "cache_size": len(self._cache._cache),
        }
