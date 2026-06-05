"""Safe HTTP fetch — read-only, policy bounded."""

from __future__ import annotations

from typing import Any

from odin_backend.core.web_access.content_extractor import extract_text
from odin_backend.core.web_access.domain_policy import check_domain
from odin_backend.core.web_access.robots_checker import allows_fetch


async def safe_fetch(app: Any, url: str) -> dict[str, Any]:
    ok, reason = check_domain(url, app.settings)
    if not ok:
        return {"status": "blocked", "blocked": True, "reason": reason, "url": url}
    if not allows_fetch(url):
        return {"status": "blocked", "blocked": True, "reason": "robots_disallow", "url": url}
    if not getattr(app.settings, "web_access_enabled", False):
        return {
            "status": "stub",
            "url": url,
            "text": f"[read-only stub] fetched content for {url}",
            "simulated": True,
        }
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            resp = await client.get(url, headers={"User-Agent": "Odin-Research/1.0"})
            text = extract_text(resp.text)
            return {"status": "ok", "url": url, "text": text, "code": resp.status_code}
    except Exception as exc:
        return {"status": "error", "url": url, "text": "", "error": str(exc)}
