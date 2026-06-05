"""Execution strategy selection and recommendations."""

from typing import Any

from odin_backend.execution_intelligence.reliability import ToolReliabilityScore

FALLBACK_MAP: dict[str, list[str]] = {
    "extract_tab_content": ["search_web", "summarize_content"],
    "search_web": ["summarize_content"],
    "execute_terminal": ["get_system_info"],
}


class ExecutionStrategySelector:
    def __init__(self, reliability_threshold: float = 0.6) -> None:
        self._threshold = reliability_threshold

    def select_tool(
        self,
        preferred: str,
        scores: list[ToolReliabilityScore],
    ) -> tuple[str, str | None]:
        score_map = {s.tool_name: s for s in scores}
        pref = score_map.get(preferred)
        if pref and pref.sample_size >= 3 and pref.success_rate < self._threshold:
            fallbacks = FALLBACK_MAP.get(preferred, [])
            for fb in fallbacks:
                fb_score = score_map.get(fb)
                if not fb_score or fb_score.success_rate >= self._threshold:
                    return fb, f"Fallback: {preferred} reliability {pref.success_rate:.0%}"
        return preferred, None

    def recommend_parallelization(self, step_count: int, avg_latency_ms: float) -> str | None:
        if step_count >= 3 and avg_latency_ms > 2000:
            return "Parallel execution could reduce latency for independent steps."
        return None

    def analyze_bottlenecks(self, step_results: dict[str, Any]) -> list[str]:
        findings: list[str] = []
        slow = [
            sid
            for sid, r in step_results.items()
            if isinstance(r, dict) and r.get("latency_ms", 0) > 5000
        ]
        if slow:
            findings.append(f"Bottleneck steps (high latency): {slow}")
        failed = [
            sid for sid, r in step_results.items() if isinstance(r, dict) and not r.get("success")
        ]
        if failed:
            findings.append(f"Failed steps: {failed}")
        return findings
