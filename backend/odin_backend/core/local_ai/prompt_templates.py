"""Prompt templating system."""

from __future__ import annotations

from typing import Any

TEMPLATES: dict[str, str] = {
    "reasoning": "Analyze the following with step-by-step reasoning:\n{input}",
    "planning": "Create a bounded plan for:\n{input}",
    "code": "Write safe, reviewed code for:\n{input}",
    "summary": "Summarize concisely:\n{input}",
}


def render(template: str, **kwargs: Any) -> str:
    tpl = TEMPLATES.get(template, "{input}")
    return tpl.format(**kwargs)
