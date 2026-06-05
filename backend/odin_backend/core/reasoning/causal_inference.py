"""Simple causal relationship inference."""

from __future__ import annotations

from typing import Any


def infer_causal(facts: list[dict[str, Any]]) -> list[dict[str, str]]:
    links: list[dict] = []
    for f in facts:
        text = str(f.get("fact", "")).lower()
        if "because" in text or "causes" in text or "leads to" in text:
            links.append({"entity": f.get("entity", ""), "relation": "causal_hint", "fact": f.get("fact", "")[:120]})
    return links
