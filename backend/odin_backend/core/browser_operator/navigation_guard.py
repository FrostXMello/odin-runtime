"""Browser navigation safety restrictions."""

from __future__ import annotations

_BLOCKED_DOMAINS = ("malware", "phishing", "credential-harvest")
_BLOCKED_SCHEMES = ("file://", "javascript:")


def allow_navigation(url: str) -> tuple[bool, str]:
    lower = url.lower().strip()
    for scheme in _BLOCKED_SCHEMES:
        if lower.startswith(scheme):
            return False, f"blocked_scheme:{scheme}"
    for domain in _BLOCKED_DOMAINS:
        if domain in lower:
            return False, f"blocked_domain:{domain}"
    return True, "ok"
