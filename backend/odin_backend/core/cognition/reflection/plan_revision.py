"""Generate plan revisions from reflection."""

from __future__ import annotations


def revision_prompt(*, plan: str, critique: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "Revise the plan based on critique. Keep changes minimal and actionable.",
        },
        {"role": "user", "content": f"Plan:\n{plan}\n\nCritique:\n{critique}"},
    ]
