"""Prompt assembly for reasoning — decoupled from provider."""

from odin_backend.ai.prompts.templates import PLANNING_SYSTEM_PROMPT, PLANNING_USER_TEMPLATE


class PromptManager:
  def build_planning_messages(self, objective: str, context: str = "") -> list[dict[str, str]]:
    return [
      {"role": "system", "content": PLANNING_SYSTEM_PROMPT},
      {
        "role": "user",
        "content": PLANNING_USER_TEMPLATE.format(
          objective=objective,
          context=context or "No additional context.",
        ),
      },
    ]
