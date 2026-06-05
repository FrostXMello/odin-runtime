"""Sequential workflow execution — plan → agents → tools (never direct ODIN execution)."""

import re
from typing import Any

from odin_backend.agents.registry import AgentRegistry
from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, Task, TaskPriority, TaskStatus
from odin_backend.models.workflow import StepStatus, WorkflowPlan, WorkflowRun, WorkflowRunStatus
from odin_backend.monitoring.logging import get_logger
from odin_backend.monitoring.tracing import TraceManager

logger = get_logger(__name__)

_TEMPLATE = re.compile(r"\{\{step_(\d+)\.(\w+)\}\}")


class WorkflowRunner:
    """
    Executes WorkflowPlan sequentially via assigned agents.

    Flow: LLM → WorkflowPlan → Runner → Agent.handle_task → RuntimeToolExecutor → Tool
    """

    def __init__(
        self,
        event_bus: EventBus,
        agent_registry: AgentRegistry,
        memory: MimirCoordinator,
        trace_manager: TraceManager,
    ) -> None:
        self._event_bus = event_bus
        self._agents = agent_registry
        self._memory = memory
        self._trace = trace_manager
        self._runs: dict[str, WorkflowRun] = {}

    def get_run(self, run_id: str) -> WorkflowRun | None:
        return self._runs.get(run_id)

    def list_runs(self, limit: int = 20) -> list[WorkflowRun]:
        return list(self._runs.values())[-limit:]

    async def execute_plan(self, plan: WorkflowPlan) -> WorkflowRun:
        run = WorkflowRun(plan_id=plan.id, objective=plan.objective)
        self._runs[run.id] = run
        run.status = WorkflowRunStatus.RUNNING

        await self._event_bus.publish(
            Event(
                type=EventType.WORKFLOW_CREATED,
                source=AgentId.ODIN,
                workflow_id=run.id,
                correlation_id=plan.correlation_id,
                payload={"objective": plan.objective, "steps": len(plan.steps)},
            )
        )
        await self._memory.record_workflow(
            run.id, "workflow.created", {"objective": plan.objective}
        )

        step_outputs: dict[int, dict[str, Any]] = {}

        try:
            for step in sorted(plan.steps, key=lambda s: s.step_id):
                for dep in step.depends_on:
                    if step_outputs.get(dep, {}).get("success") is False:
                        step.status = StepStatus.SKIPPED
                        continue

                agent = self._agents.get(step.agent)
                if agent is None:
                    step.status = StepStatus.FAILED
                    run.status = WorkflowRunStatus.FAILED
                    run.error = f"No agent registered: {step.agent}"
                    break

                step.status = StepStatus.RUNNING
                run.current_step = step.step_id

                await self._event_bus.publish(
                    Event(
                        type=EventType.WORKFLOW_STEP_STARTED,
                        source=step.agent,
                        workflow_id=run.id,
                        payload={"step_id": step.step_id, "tool": step.tool, "agent": str(step.agent)},
                    )
                )

                params = self._resolve_params(step.params, step_outputs)
                params = self._enrich_params(step.tool, params, step_outputs, step.step_id)

                task = Task(
                    title=f"{step.tool}: {step.description or plan.objective}",
                    description=step.description,
                    assigned_agent=step.agent,
                    workflow_id=run.id,
                    status=TaskStatus.ASSIGNED,
                    required_tools=[step.tool],
                    payload={
                        "tool": step.tool,
                        "params": params,
                        "user_confirmed": step.params.get("user_confirmed", False),
                    },
                    metadata={"step_id": step.step_id, "plan_id": plan.id},
                    priority=TaskPriority.NORMAL,
                )

                self._trace.start_trace(
                    tool_name=step.tool,
                    workflow_id=run.id,
                    agent_id=str(step.agent),
                    correlation_id=plan.correlation_id,
                )

                task_result = await agent.handle_task(task)
                tool_output = task_result.output.get(step.tool, {}) if task_result.output else {}
                data = tool_output.get("data", tool_output) if isinstance(tool_output, dict) else {}

                step_outputs[step.step_id] = {
                    "success": task_result.success,
                    "data": data,
                    "errors": [task_result.error] if task_result.error else [],
                    "output": task_result.output,
                }
                run.step_results[step.step_id] = step_outputs[step.step_id]

                if task_result.success:
                    step.status = StepStatus.COMPLETED
                    await self._event_bus.publish(
                        Event(
                            type=EventType.WORKFLOW_STEP_COMPLETED,
                            source=step.agent,
                            workflow_id=run.id,
                            payload={"step_id": step.step_id, "tool": step.tool},
                        )
                    )
                else:
                    step.status = StepStatus.FAILED
                    run.status = WorkflowRunStatus.FAILED
                    run.error = task_result.error or "Agent step failed"
                    await self._event_bus.publish(
                        Event(
                            type=EventType.WORKFLOW_FAILED,
                            source=AgentId.ODIN,
                            workflow_id=run.id,
                            payload={"step_id": step.step_id, "error": run.error},
                        )
                    )
                    break

                await self._memory.record_workflow(
                    run.id,
                    f"step.{step.step_id}.completed",
                    {"tool": step.tool, "agent": str(step.agent), "success": task_result.success},
                )

            if run.status != WorkflowRunStatus.FAILED:
                run.status = WorkflowRunStatus.COMPLETED
                await self._event_bus.publish(
                    Event(
                        type=EventType.WORKFLOW_COMPLETED,
                        source=AgentId.ODIN,
                        workflow_id=run.id,
                        payload={"objective": plan.objective},
                    )
                )
                await self._memory.save_memory(
                    f"Workflow completed: {plan.objective}",
                    category="workflow",
                    metadata={"run_id": run.id},
                )

        except Exception as exc:
            run.status = WorkflowRunStatus.FAILED
            run.error = str(exc)
            logger.exception("workflow_run_failed", run_id=run.id)
            await self._event_bus.publish(
                Event(
                    type=EventType.WORKFLOW_FAILED,
                    source=AgentId.ODIN,
                    workflow_id=run.id,
                    payload={"error": str(exc)},
                )
            )

        return run

    def _enrich_params(
        self,
        tool: str,
        params: dict[str, Any],
        outputs: dict[int, dict[str, Any]],
        step_id: int,
    ) -> dict[str, Any]:
        enriched = dict(params)
        if tool in ("summarize_content", "generate_email") and "text" not in enriched:
            prior = outputs.get(step_id - 1, {}).get("data", {})
            if "contents" in prior:
                enriched["contents"] = prior["contents"]
            elif "summary" in prior:
                enriched["text"] = prior["summary"]
                enriched["prior"] = prior
            elif "tabs" in prior:
                enriched["urls"] = [t.get("url") for t in prior.get("tabs", []) if t.get("url")]
            elif prior:
                enriched["text"] = str(prior)
                enriched["prior"] = prior
        return enriched

    def _resolve_params(
        self, params: dict[str, Any], outputs: dict[int, dict[str, Any]]
    ) -> dict[str, Any]:
        resolved = dict(params)
        for key, val in list(resolved.items()):
            if isinstance(val, str):
                m = _TEMPLATE.search(val)
                if m:
                    sid, field = int(m.group(1)), m.group(2)
                    prior = outputs.get(sid, {}).get("data", {})
                    resolved[key] = prior.get(field, prior.get("output", ""))
        return resolved
