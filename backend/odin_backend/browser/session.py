"""Browser session models and clustering."""

from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class BrowserTab(BaseModel):
    id: str | None = None
    title: str = ""
    url: str = ""


class BrowserSession(BaseModel):
    tabs: list[BrowserTab] = Field(default_factory=list)
    clusters: dict[str, list[str]] = Field(default_factory=dict)
    insight: str = ""
    research_topics: list[str] = Field(default_factory=list)


def cluster_tabs(tabs: list[BrowserTab]) -> dict[str, list[str]]:
    """Group tabs by domain / keyword heuristics."""
    clusters: dict[str, list[str]] = {}
    for tab in tabs:
        domain = urlparse(tab.url).netloc or "local"
        key = domain.replace("www.", "")
        clusters.setdefault(key, []).append(tab.url)
    return clusters


def detect_research_topics(tabs: list[BrowserTab]) -> list[str]:
    keywords = ("github", "docs", "research", "arxiv", "stackoverflow", "medium", "wiki")
    topics: list[str] = []
    for tab in tabs:
        lower = (tab.title + " " + tab.url).lower()
        for kw in keywords:
            if kw in lower and kw not in topics:
                topics.append(kw)
    return topics


def generate_session_insight(tabs: list[BrowserTab], topics: list[str]) -> str:
    if not tabs:
        return "No active browser tabs detected."
    if topics:
        return f"User appears to be researching: {', '.join(topics)} ({len(tabs)} tabs open)."
    domains = {urlparse(t.url).netloc for t in tabs if t.url}
    return f"Browsing session with {len(tabs)} tabs across {len(domains)} domains."
