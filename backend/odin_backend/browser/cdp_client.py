"""Chrome DevTools Protocol client — inspect real browser sessions."""

from typing import Any

import httpx

from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class CDPClient:
    def __init__(self, cdp_url: str = "http://127.0.0.1:9222") -> None:
        self._cdp_url = cdp_url.rstrip("/")

    async def list_targets(self) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._cdp_url}/json/list")
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.debug("cdp_list_failed", error=str(exc))
            return []

    async def get_active_tabs(self) -> list[dict[str, Any]]:
        targets = await self.list_targets()
        tabs = []
        for t in targets:
            if t.get("type") in ("page", "tab") or "url" in t:
                url = t.get("url", "")
                if url.startswith(("http://", "https://", "chrome://")):
                    tabs.append({
                        "id": t.get("id"),
                        "title": t.get("title", ""),
                        "url": url,
                        "type": t.get("type", "page"),
                    })
        return tabs

    async def connect_playwright(self):
        """Connect Playwright over CDP if available."""
        try:
            from playwright.async_api import async_playwright

            pw = await async_playwright().start()
            browser = await pw.chromium.connect_over_cdp(self._cdp_url)
            return browser, pw
        except Exception as exc:
            logger.debug("playwright_cdp_failed", error=str(exc))
            return None, None
