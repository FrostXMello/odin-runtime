"""Long-horizon planning — decomposition, waves, replanning."""

from typing import Any

from pydantic import BaseModel, Field

from odin_backend.models.mission import Mission
from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus


class PlanningWave(BaseModel):
    wave_index: int
    task_ids: list[str] = Field(default_factory=list)


class HorizonPlan(BaseModel):
    objective: str
    task_graph: TaskGraph
    waves: list[PlanningWave] = Field(default_factory=list)
    milestones: list[str] = Field(default_factory=list)
    retry_strategy: dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "cooldown_seconds": 5})


class LongHorizonPlanner:
    """
    Deterministic objective decomposition for mission execution.

    Supports partial completion, replanning, and interruption recovery without
    requiring live LLM calls (kernel/router may augment in production).
    """

    def decompose(self, objective: str, *, mission_id: str | None = None) -> HorizonPlan:
        segments = self._segment_objective(objective)
        if len(segments) < 2:
            segments = [
                f"Analyze objective: {objective[:120]}",
                f"Execute plan for: {objective[:120]}",
                f"Verify completion: {objective[:80]}",
            ]

        graph = TaskGraph()
        prev_id: str | None = None
        for i, segment in enumerate(segments):
            out: dict = {
                "wave": 0,
                "mission_id": mission_id,
                "step_kind": "mission_step",
            }
            if "Execute" in segment or i == 1:
                out.update(
                    {
                        "type": "execution",
                        "capability": "python.safe",
                        "params": {"code": f"print({repr(segment[:100])})"},
                        "parallelizable": False,
                        "blocking": True,
                    }
                )
            else:
                out["tool"] = "noop"
            node = TaskNode(
                goal=segment,
                dependencies=[prev_id] if prev_id else [],
                priority=max(10, 90 - i * 10),
                output=out,
            )
            graph.add_node(node)
            prev_id = node.id

        waves = self._build_waves(graph)
        milestones = [f"Milestone {i + 1}: {w.task_ids[0]}" for i, w in enumerate(waves) if w.task_ids]

        return HorizonPlan(
            objective=objective,
            task_graph=graph,
            waves=waves,
            milestones=milestones,
        )

    def replan(self, mission: Mission, *, reason: str = "") -> HorizonPlan:
        """Adaptive replan from remaining pending/failed nodes."""
        graph = TaskGraph()
        pending = [
            n
            for n in mission.task_graph.nodes.values()
            if n.status in (TaskNodeStatus.PENDING, TaskNodeStatus.FAILED)
        ]
        if not pending:
            plan = self.decompose(mission.objective, mission_id=mission.mission_id)
            mission.append_reasoning("replan_full_decompose", detail={"reason": reason})
            return plan

        completed_ids = {
            nid
            for nid, n in mission.task_graph.nodes.items()
            if n.status == TaskNodeStatus.COMPLETE
        }
        for node in pending:
            if node.status == TaskNodeStatus.FAILED and node.retry_count < mission.max_retries:
                retry = TaskNode(
                    goal=f"Retry: {node.goal[:100]}",
                    dependencies=list(node.dependencies),
                    priority=node.priority + 5,
                    retry_count=node.retry_count + 1,
                    output={**node.output, "retry_of": node.id, "tool": "noop"},
                )
                graph.add_node(retry)
            else:
                graph.add_node(node.model_copy())

        for node in graph.nodes.values():
            node.dependencies = [d for d in node.dependencies if d in completed_ids or d in graph.nodes]

        waves = self._build_waves(graph)
        mission.append_reasoning("replan_partial", detail={"reason": reason, "pending": len(pending)})
        return HorizonPlan(
            objective=mission.objective,
            task_graph=graph,
            waves=waves,
            milestones=[f"Recovery wave {w.wave_index}" for w in waves],
        )

    def _segment_objective(self, objective: str) -> list[str]:
        text = objective.strip()
        for sep in (" then ", ";", "\n", " and then "):
            if sep in text.lower():
                parts = [p.strip() for p in text.replace(sep, "|").split("|") if p.strip()]
                if len(parts) >= 2:
                    return parts
        if "." in text:
            parts = [p.strip() for p in text.split(".") if p.strip()]
            if len(parts) >= 2:
                return parts
        return [text] if text else []

    def _build_waves(self, graph: TaskGraph) -> list[PlanningWave]:
        waves: list[PlanningWave] = []
        assigned: set[str] = set()
        wave_idx = 0
        while len(assigned) < len(graph.nodes):
            ready = [
                n
                for n in graph.nodes.values()
                if n.id not in assigned and all(d in assigned for d in n.dependencies)
            ]
            if not ready:
                break
            waves.append(PlanningWave(wave_index=wave_idx, task_ids=[n.id for n in ready]))
            for n in ready:
                n.output["wave"] = wave_idx
                assigned.add(n.id)
            wave_idx += 1
        return waves
