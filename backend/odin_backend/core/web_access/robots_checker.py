"""Robots.txt respect stub."""

from __future__ import annotations


def allows_fetch(url: str) -> bool:
    return not url.lower().endswith("/admin") and "private" not in url.lower()
