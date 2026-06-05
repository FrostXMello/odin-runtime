"""Mission checkpointing — snapshots for restart recovery."""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from odin_backend.models.mission import Mission, MissionCheckpoint, MissionLifecycle


class MissionCheckpointEngine:
    """Persist mission cognition snapshots for continuation after restart."""

    def __init__(self, store: Any) -> None:
        self._store = store

    def create_checkpoint(
        self,
        mission: Mission,
        *,
        label: str = "wave",
        metadata: dict[str, Any] | None = None,
    ) -> MissionCheckpoint:
        mission.sync_task_lists()
        ckpt = MissionCheckpoint(
            id=str(uuid4()),
            label=label,
            state=mission.current_state,
            task_graph=mission.task_graph.snapshot(),
            reasoning_snapshot=mission.reasoning_log[-20:],
            metadata=metadata or {},
        )
        mission.checkpoints.append(ckpt)
        if len(mission.checkpoints) > 50:
            mission.checkpoints = mission.checkpoints[-50:]
        return ckpt

    async def persist(self, mission: Mission, checkpoint: MissionCheckpoint) -> None:
        payload = checkpoint.model_dump(mode="json")
        await self._store.save_checkpoint(mission.mission_id, payload)
        await self._store.save(mission)

    async def restore_latest(self, mission: Mission) -> Mission | None:
        records = await self._store.list_checkpoints(mission.mission_id, limit=1)
        if not records:
            return mission
        from odin_backend.models.task_graph import TaskGraph

        ckpt = MissionCheckpoint.model_validate(records[0])
        mission.current_state = ckpt.state
        from odin_backend.models.task_graph import TaskNode

        nodes_raw = ckpt.task_graph.get("nodes", {})
        nodes = {k: TaskNode.model_validate(v) for k, v in nodes_raw.items()}
        mission.task_graph = TaskGraph(nodes=nodes)
        mission.reasoning_log = list(ckpt.reasoning_snapshot)
        mission.append_history("checkpoint_restored", {"checkpoint_id": ckpt.id})
        return mission

    async def rollback_to(self, mission: Mission, checkpoint_id: str) -> bool:
        records = await self._store.list_checkpoints(mission.mission_id, limit=50)
        match = next((r for r in records if r.get("id") == checkpoint_id), None)
        if not match:
            return False
        from odin_backend.models.task_graph import TaskGraph

        ckpt = MissionCheckpoint.model_validate(match)
        mission.current_state = ckpt.state
        from odin_backend.models.task_graph import TaskNode

        nodes_raw = ckpt.task_graph.get("nodes", {})
        nodes = {k: TaskNode.model_validate(v) for k, v in nodes_raw.items()}
        mission.task_graph = TaskGraph(nodes=nodes)
        mission.append_history("checkpoint_rollback", {"checkpoint_id": checkpoint_id})
        await self._store.save(mission)
        return True
