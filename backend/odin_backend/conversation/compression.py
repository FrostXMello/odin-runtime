"""Context compression for long conversations."""

from odin_backend.conversation.sessions import ConversationMessage


def compress_messages(messages: list[ConversationMessage], max_chars: int = 4000) -> str:
    """Token-efficient stitching via extractive summary."""
    if not messages:
        return ""
    parts: list[str] = []
    total = 0
    for msg in reversed(messages):
        line = f"{msg.role.value}: {msg.content[:500]}"
        if total + len(line) > max_chars:
            break
        parts.insert(0, line)
        total += len(line)
    if len(messages) > len(parts):
        parts.insert(0, f"[...{len(messages) - len(parts)} earlier turns omitted]")
    return "\n".join(parts)


def summarize_for_continuity(messages: list[ConversationMessage], max_sentences: int = 6) -> str:
    combined = " ".join(m.content for m in messages[-20:])
    sentences = [s.strip() for s in combined.replace("\n", " ").split(".") if s.strip()]
    return ". ".join(sentences[:max_sentences]) + ("." if sentences else "")
