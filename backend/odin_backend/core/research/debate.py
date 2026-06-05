"""Multi-agent debate for research."""

from __future__ import annotations

from typing import Any


async def run_debate(app: Any, *, topic: str, hypothesis: str) -> dict[str, str]:
    researcher = await app.cognitive_agents._agents["researcher"].run(objective=f"{topic}: {hypothesis}")
    critic = await app.cognitive_agents._agents["critic"].run(
        objective=topic, context={"plan": researcher.content}
    )
    synth = await app.cognitive_agents._agents["synthesizer"].run(
        objective=topic,
        context={"steps": [{"content": researcher.content}, {"content": critic.content}]},
    )
    return {
        "researcher": researcher.content,
        "critic": critic.content,
        "synthesizer": synth.content,
    }
