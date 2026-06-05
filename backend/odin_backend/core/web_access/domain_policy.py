"""Domain allow/deny rules."""

from __future__ import annotations

from typing import Any

_BLOCKED = ("malware", "phishing", "darkweb", "torrent")
_SUSPICIOUS = ("login", "signin", "account", "payment", "checkout")


_BLOCKED_SCHEMES = ("javascript:", "file://", "data:")


def check_domain(url: str, settings: Any) -> tuple[bool, str]:
    lower = url.lower().strip()
    for scheme in _BLOCKED_SCHEMES:
        if lower.startswith(scheme):
            return False, f"blocked_scheme:{scheme}"
    for b in _BLOCKED:
        if b in lower:
            return False, f"blocked_domain:{b}"
    allowlist = getattr(settings, "web_access_allowlist", "")
    if allowlist:
        allowed = [d.strip() for d in allowlist.split(",") if d.strip()]
        if allowed and not any(d in lower for d in allowed):
            return False, "not_in_allowlist"
    for s in _SUSPICIOUS:
        if s in lower:
            return False, f"suspicious_path:{s}"
    return True, "ok"
