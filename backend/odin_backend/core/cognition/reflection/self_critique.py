"""Self-critique prompts for local models."""

from __future__ import annotations


def critique_prompt(*, plan: str, objective: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "Critique the plan. List risks, missing validations, and improvement suggestions.",
        },
        {"role": "user", "content": f"Objective: {objective}\n\nPlan:\n{plan}"},
    ]
