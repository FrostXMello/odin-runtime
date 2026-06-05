"""DOM/page parsing stubs."""

from __future__ import annotations

from typing import Any


def parse_page(content: str) -> dict[str, Any]:
    return {
        "title": _extract_title(content),
        "links": content.count("href="),
        "forms": content.count("<form"),
        "summary": content[:300],
    }


def _extract_title(content: str) -> str:
    if "<title>" in content.lower():
        start = content.lower().index("<title>") + 7
        end = content.lower().find("</title>", start)
        if end > start:
            return content[start:end].strip()
    return ""
