"""Browser automation via Playwright — safe navigation only."""

from typing import Any

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult

_playwright = None
_browser = None


async def _get_browser():
    global _playwright, _browser
    if _browser is not None:
        return _browser
    try:
        from playwright.async_api import async_playwright

        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
        return _browser
    except Exception:
        return None


class OpenBrowserTool(Tool):
    name = "open_browser"
    description = "Open a URL in controlled browser"
    permission_class = PermissionClass.CONFIRM_REQUIRED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        url = params.get("url", "")
        if not url.startswith(("http://", "https://")):
            return ToolResult(success=False, error="Invalid URL")

        browser = await _get_browser()
        if browser is None:
            return ToolResult(
                success=True,
                data={"url": url, "note": "Playwright not available — install playwright"},
            )

        try:
            page = await browser.new_page()
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            title = await page.title()
            await page.close()
            return ToolResult(success=True, data={"url": url, "title": title})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class GetBrowserTabsTool(Tool):
    name = "get_browser_tabs"
    description = "List open browser tabs via Chrome DevTools Protocol"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        from odin_backend.browser.cdp_client import CDPClient
        from odin_backend.config import get_settings

        settings = get_settings()
        cdp = CDPClient(settings.chrome_cdp_url)
        tabs = await cdp.get_active_tabs()
        if not tabs and params.get("urls"):
            tabs = [{"id": str(i), "url": u, "title": u} for i, u in enumerate(params["urls"])]
        return ToolResult(
            success=True,
            data={"tabs": tabs, "source": "cdp" if tabs else "empty"},
        )


class ExtractTabContentTool(Tool):
    name = "extract_tab_content"
    description = "Extract text content from URLs"
    permission_class = PermissionClass.SAFE

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        urls = params.get("urls") or []
        if not urls and "url" in params:
            urls = [params["url"]]

        browser = await _get_browser()
        contents: list[dict] = []

        if browser and urls:
            for url in urls[:5]:
                try:
                    page = await browser.new_page()
                    await page.goto(url, timeout=20000, wait_until="domcontentloaded")
                    text = await page.inner_text("body")
                    contents.append({"url": url, "text": text[:15000]})
                    await page.close()
                except Exception as exc:
                    contents.append({"url": url, "error": str(exc)})
        else:
            # Fallback: use prior step output
            text = params.get("text", params.get("content", ""))
            if text:
                contents.append({"url": "inline", "text": str(text)[:15000]})

        return ToolResult(success=True, data={"contents": contents})
