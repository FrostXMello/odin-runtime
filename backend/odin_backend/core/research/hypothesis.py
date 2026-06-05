"""Hypothesis generation for local research."""

from __future__ import annotations


def generate_hypothesis(topic: str, *, context: str = "", iteration: int = 0) -> str:
    prefix = f"Iteration {iteration}: " if iteration else ""
    if context:
        return f"{prefix}Hypothesis for '{topic}': based on {context[:120]}, strategy adjustment may reduce failures."
    return f"{prefix}Hypothesis: improving '{topic}' via memory-grounded planner feedback."
