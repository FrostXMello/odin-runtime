"""Sandboxed execution — profiles enforced via Heimdall."""

from pathlib import Path
from typing import Any

from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.sandbox.profiles import SandboxPolicy, SandboxProfile
from odin_backend.sandbox.snapshots import ExecutionSnapshot
from odin_backend.tools.base import ToolContext
from odin_backend.tools.runtime.executor import RuntimeToolExecutor
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class SandboxExecutor:
    def __init__(self, settings: Settings, event_bus: EventBus, tool_executor: RuntimeToolExecutor) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._tools = tool_executor
        self._work_root = Path(settings.sandbox_work_dir)
        self._work_root.mkdir(parents=True, exist_ok=True)
        self._snapshots: list[ExecutionSnapshot] = []

    def _policy_for(self, profile: SandboxProfile) -> SandboxPolicy:
        work_dir = str(self._work_root / profile.value)
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        return SandboxPolicy.from_profile(profile, work_dir)

    async def execute_in_sandbox(
        self,
        profile: SandboxProfile,
        tool_name: str,
        params: dict[str, Any],
        context: ToolContext,
    ) -> dict[str, Any]:
        policy = self._policy_for(profile)
        if tool_name not in policy.allowed_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not allowed in profile {profile.value}",
            }

        snapshot = ExecutionSnapshot(
            tool_name=tool_name,
            before_state={"cwd": policy.working_directory, "params": params},
        )

        if profile == SandboxProfile.DEV_SANDBOX and tool_name == "execute_terminal":
            params = {**params, "cwd": policy.working_directory}

        result = await self._tools.execute(
            tool_name, params, context, timeout=float(policy.max_execution_seconds)
        )

        snapshot.after_state = {"success": result.success, "data": result.data}
        snapshot.rollback_available = tool_name == "write_file"
        self._snapshots.append(snapshot)

        await self._event_bus.publish(
            Event(
                type=EventType.SANDBOX_EXECUTION,
                source=AgentId.HEIMDALL,
                payload={
                    "profile": profile.value,
                    "tool": tool_name,
                    "success": result.success,
                    "snapshot_id": snapshot.id,
                },
            )
        )
        return result.model_dump()

    def list_snapshots(self, limit: int = 50) -> list[dict]:
        return [s.model_dump(mode="json") for s in self._snapshots[-limit:]]
