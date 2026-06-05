"""Entity extraction from text."""

from __future__ import annotations

import re


def extract_entities(text: str) -> list[str]:
    if not text:
        return []
    candidates = re.findall(r"\b[A-Z][a-zA-Z0-9_-]{2,}\b", text)
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    stop = {"that", "this", "with", "from", "have", "been", "will", "about"}
    entities = list(dict.fromkeys(candidates + [w for w in words if w not in stop]))
    return entities[:20]
