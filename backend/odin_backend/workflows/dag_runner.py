"""DAG workflow runner — parallel, sequential, and hybrid execution."""

import asyncio
import re
from collections import defaultdict
from typing import Any

from odin_backend.agents.registry import AgentRegistry
from odin_backend.cognition.stream import CognitionStream
from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, Task, TaskPriority, TaskStatus
from odin_backend.models.trace import TraceContext
from odin_backend.models.workflow import StepStatus, WorkflowPlan, WorkflowRun, WorkflowRunStatus
from odin_backend.monitoring.logging import get_logger
from odin_backend.monitoring.metrics import MetricsCollector
from odin_backend.monitoring.tracing import TraceManager
from odin_backend.workflows.runner import WorkflowRunner

logger = get_logger(__name__)

_TEMPLATE = re.compile(r"\{\{step_(\d+)\.(\w+)\}\}")


class DAGWorkflowRunner(WorkflowRunner):
    """
    Extends sequential runner with dependency-graph parallel execution.

    Supports: sequential | parallel | hybrid (level-based parallelism)
    """

    def __init__(
        self,
        event_bus: EventBus,
        agent_registry: AgentRegistry,
        memory: MimirCoordinator,
        trace_manager: TraceManager,
        cognition: CognitionStream,
        metrics: MetricsCollector,
        max_parallel: int = 5,
    ) -> None:
        super().__init__(event_bus, agent_registry, memory, trace_manager)
        self._cognition = cognition
        self._metrics = metrics
        self._max_parallel = max_parallel

    async def execute_plan(
        self,
        plan: WorkflowPlan,
        *,
        mode: str = "hybrid",
        trace: TraceContext | None = None,
    ) -> WorkflowRun:
        trace = trace or TraceContext(correlation_id=plan.correlation_id, workflow_id=None)
        run = WorkflowRun(plan_id=plan.id, objective=plan.objective, trace_id=trace.trace_id)
        self._runs[run.id] = run
        trace.workflow_id = run.id
        run.status = WorkflowRunStatus.RUNNING

        await self._cognition.emit("Executing workflow", stage="workflow.start", trace=trace)
        await self._emit_workflow_created(run, plan)

        step_outputs: dict[int, dict[str, Any]] = {}
        levels = self._build_levels(plan) if mode != "sequential" else [[s] for s in sorted(plan.steps, key=lambda x: x.step_id)]

        try:
            for level in levels:
                if mode == "sequential":
                    for step in level:
                        ok = await self._execute_step(step, plan, run, step_outputs, trace)
                        if not ok:
                            break
                    if run.status == WorkflowRunStatus.FAILED:
                        break
                else:
                    # Parallel within level (bounded)
                    sem = asyncio.Semaphore(self._max_parallel)
                    results = await asyncio.gather(
                        *[self._execute_step_guarded(sem, s, plan, run, step_outputs, trace) for s in level],
                        return_exceptions=True,
                    )
                    if any(r is False or isinstance(r, Exception) for r in results):
                        if run.status != WorkflowRunStatus.FAILED:
                            run.status = WorkflowRunStatus.FAILED
                            run.error = run.error or "Parallel step failure"
                        break

            if run.status != WorkflowRunStatus.FAILED:
                run.status = WorkflowRunStatus.COMPLETED
                await self._finalize_success(run, plan, trace)
        except Exception as exc:
            run.status = WorkflowRunStatus.FAILED
            run.error = str(exc)
            await self._emit_failed(run, {"error": str(exc)})

        self._metrics.record_workflow(run.status.value)
        return run

    def _build_levels(self, plan: WorkflowPlan) -> list[list]:
        """Topological levels for DAG execution."""
        steps = {s.step_id: s for s in plan.steps}
        in_degree = {sid: len(s.depends_on) for sid, s in steps.items()}
        level_map: dict[int, int] = {}

        def depth(sid: int) -> int:
            if sid in level_map:
                return level_map[sid]
            deps = steps[sid].depends_on
            d = max([depth(d) for d in deps], default=-1) + 1
            level_map[sid] = d
            return d

        for sid in steps:
            depth(sid)

        by_level: dict[int, list] = defaultdict(list)
        for sid, lvl in level_map.items():
            by_level[lvl].append(steps[sid])
        return [by_level[i] for i in sorted(by_level.keys())]

    async def _execute_step_guarded(self, sem, step, plan, run, outputs, trace):
        async with sem:
            return await self._execute_step(step, plan, run, outputs, trace)

    async def _execute_step(self, step, plan, run, step_outputs, trace) -> bool:
        for dep in step.depends_on:
            if step_outputs.get(dep, {}).get("success") is False:
                step.status = StepStatus.SKIPPED
                return True

        agent = self._agents.get(step.agent)
        if not agent:
            run.status = WorkflowRunStatus.FAILED
            run.error = f"No agent: {step.agent}"
            return False

        step.status = StepStatus.RUNNING
        run.current_step = step.step_id
        await self._cognition.emit(
            f"Delegating step {step.step_id} to {step.agent}",
            stage="workflow.delegate",
            trace=trace,
            payload={"tool": step.tool},
        )

        params = self._resolve_params(step.params, step_outputs)
        params = self._enrich_params(step.tool, params, step_outputs, step.step_id)

        task = Task(
            title=f"{step.tool}: {step.description or plan.objective}",
            assigned_agent=step.agent,
            workflow_id=run.id,
            status=TaskStatus.ASSIGNED,
            required_tools=[step.tool],
            payload={"tool": step.tool, "params": params, "user_confirmed": step.params.get("user_confirmed", False)},
            metadata={"step_id": step.step_id, "trace_id": trace.trace_id},
        )

        step_trace = trace.child(task_id=task.id)
        self._trace.start_trace(tool_name=step.tool, workflow_id=run.id, agent_id=str(step.agent))

        task_result = await agent.handle_task(task)
        tool_output = task_result.output.get(step.tool, {}) if task_result.output else {}
        data = tool_output.get("data", tool_output) if isinstance(tool_output, dict) else {}

        step_outputs[step.step_id] = {
            "success": task_result.success,
            "data": data,
            "errors": [task_result.error] if task_result.error else [],
        }
        run.step_results[step.step_id] = step_outputs[step.step_id]

        if task_result.success:
            step.status = StepStatus.COMPLETED
            await self._event_bus.publish(
                Event(
                    type=EventType.WORKFLOW_STEP_COMPLETED,
                    source=step.agent,
                    workflow_id=run.id,
                    payload={"step_id": step.step_id},
                    metadata={"trace_id": trace.trace_id},
                )
            )
            return True

        step.status = StepStatus.FAILED
        run.status = WorkflowRunStatus.FAILED
        run.error = task_result.error or "Step failed"
        await self._emit_failed(run, {"step_id": step.step_id})
        return False

    async def _emit_workflow_created(self, run, plan) -> None:
        await self._event_bus.publish(
            Event(
                type=EventType.WORKFLOW_CREATED,
                source=AgentId.ODIN,
                workflow_id=run.id,
                payload={"objective": plan.objective, "steps": len(plan.steps)},
            )
        )

    async def _finalize_success(self, run, plan, trace) -> None:
        await self._cognition.emit("Workflow completed", stage="workflow.completed", trace=trace)
        await self._event_bus.publish(
            Event(type=EventType.WORKFLOW_COMPLETED, source=AgentId.ODIN, workflow_id=run.id)
        )
        await self.memory.save_memory(
            f"Workflow completed: {plan.objective}",
            category="workflow",
            metadata={"run_id": run.id, "project": plan.metadata.get("project")},
        )

    async def _emit_failed(self, run, payload) -> None:
        await self._event_bus.publish(
            Event(type=EventType.WORKFLOW_FAILED, source=AgentId.ODIN, workflow_id=run.id, payload=payload)
        )
