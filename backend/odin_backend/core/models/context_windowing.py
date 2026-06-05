"""Context truncation and token budgeting."""

from __future__ import annotations

from odin_backend.core.models.tokenizer import estimate_messages_tokens, estimate_tokens


def truncate_text(text: str, *, max_tokens: int) -> tuple[str, bool]:
    if estimate_tokens(text) <= max_tokens:
        return text, False
    ratio = max_tokens / max(1, estimate_tokens(text))
    cut = max(32, int(len(text) * ratio))
    return text[:cut] + "\n...[truncated]", True


def fit_messages(
    messages: list[dict[str, str]],
    *,
    max_tokens: int,
    reserve_output: int = 512,
) -> tuple[list[dict[str, str]], bool]:
    budget = max(256, max_tokens - reserve_output)
    if estimate_messages_tokens(messages) <= budget:
        return messages, False
    system = [m for m in messages if m.get("role") == "system"]
    rest = [m for m in messages if m.get("role") != "system"]
    kept: list[dict[str, str]] = list(system)
    used = estimate_messages_tokens(kept)
    truncated = False
    for msg in reversed(rest):
        cost = estimate_tokens(msg.get("content", "")) + 4
        if used + cost > budget:
            truncated = True
            break
        kept.insert(len(system), msg)
        used += cost
    if not kept and messages:
        content, _ = truncate_text(messages[-1].get("content", ""), max_tokens=budget)
        kept = [{"role": messages[-1].get("role", "user"), "content": content}]
        truncated = True
    return kept, truncated
