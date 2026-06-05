"""Semantic grounding from cognitive memory."""

from __future__ import annotations

from typing import Any


def format_grounding_block(
    *,
    similar: list[dict[str, Any]],
    failures: list[dict[str, Any]],
    strategies: list[dict[str, Any]],
    capability_stats: dict[str, Any],
) -> str:
    lines: list[str] = []
    if similar:
        lines.append("Past successful executions:")
        for s in similar[:3]:
            lines.append(f"  - {s.get('label', '')[:100]} (conf={s.get('confidence')})")
    if failures:
        lines.append("Known failure patterns:")
        for f in failures[:3]:
            lines.append(f"  - {f.get('label', '')[:100]}")
    if strategies:
        lines.append("Recalled strategies:")
        for st in strategies[:3]:
            lines.append(f"  - {st.get('label', '')} (conf={st.get('confidence')})")
    if capability_stats:
        lines.append("Capability statistics:")
        for cap, stats in list(capability_stats.items())[:5]:
            lines.append(f"  - {cap}: reliability={stats.get('reliability', stats.get('success_rate'))}")
    return "\n".join(lines)
