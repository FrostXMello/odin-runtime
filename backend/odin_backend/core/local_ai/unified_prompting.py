"""Unified prompting facade."""

from __future__ import annotations

from typing import Any

from odin_backend.core.local_ai.context_manager import truncate_context
from odin_backend.core.local_ai.prompt_templates import render


def build_prompt(*, template: str, input_text: str, context: list[dict] | None = None, max_tokens: int = 4096) -> dict[str, Any]:
    messages = context or []
    messages.append({"role": "user", "content": render(template, input=input_text)})
    truncated = truncate_context(messages, max_tokens=max_tokens)
    return {"messages": truncated, "template": template}
