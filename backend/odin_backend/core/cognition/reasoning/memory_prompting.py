"""Prompt templates for memory-grounded reasoning."""

from __future__ import annotations


def build_reasoning_prompt(*, objective: str, grounding: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are a local-first orchestration planner. "
                "Use only the provided memory context. Avoid hallucinating tools or capabilities."
            ),
        },
        {
            "role": "user",
            "content": f"Objective:\n{objective}\n\nOperational memory:\n{grounding}",
        },
    ]
