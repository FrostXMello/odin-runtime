"""Task queue — Redis-backed work distribution."""

from odin_backend.events.redis_client import RedisClient
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import Task, TaskCreate, TaskPriority, TaskStatus
from odin_backend.events.bus import EventBus
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_PRIORITY_SCORE = {
    TaskPriority.CRITICAL: 0,
    TaskPriority.HIGH: 1,
    TaskPriority.NORMAL: 2,
    TaskPriority.LOW: 3,
}


class TaskQueue:
    """Manages task persistence and queue operations."""

    def __init__(self, redis_client: RedisClient, event_bus: EventBus) -> None:
        self._redis = redis_client
        self._event_bus = event_bus
        self._local_tasks: dict[str, Task] = {}

    async def create(self, create: TaskCreate, *, created_by: AgentId = AgentId.ODIN) -> Task:
        task = Task(
            title=create.title,
            description=create.description,
            assigned_agent=create.assigned_agent,
            parent_task_id=create.parent_task_id,
            workflow_id=create.workflow_id,
            priority=create.priority,
            payload=create.payload,
            required_tools=create.required_tools,
            metadata=create.metadata,
            timeout_seconds=create.timeout_seconds,
            created_by=created_by,
            status=TaskStatus.QUEUED,
        )
        await self._persist(task)
        score = _PRIORITY_SCORE.get(task.priority, 2)
        try:
            await self._redis.enqueue_task(task.id, score)
        except RuntimeError:
            pass  # Redis unavailable — task remains in local store for in-process dequeue
        await self._event_bus.publish(
            Event(
                type=EventType.TASK_CREATED,
                source=created_by,
                task_id=task.id,
                payload=task.model_dump(mode="json"),
            )
        )
        logger.info("task_created", task_id=task.id, title=task.title)
        return task

    async def get(self, task_id: str) -> Task | None:
        if task_id in self._local_tasks:
            return self._local_tasks[task_id]
        data = await self._redis.get_task(task_id)
        if data is None:
            return None
        task = Task.model_validate(data)
        self._local_tasks[task_id] = task
        return task

    async def update(self, task: Task) -> Task:
        task.touch()
        await self._persist(task)
        return task

    async def dequeue(self) -> Task | None:
        try:
            task_id = await self._redis.dequeue_task()
        except RuntimeError:
            task_id = None
        if task_id is None:
            # Fallback: dequeue oldest queued task from local store
            for tid, t in sorted(self._local_tasks.items(), key=lambda x: x[1].created_at):
                if t.status == TaskStatus.QUEUED:
                    return t
            return None
        return await self.get(task_id)

    async def list_tasks(
        self,
        *,
        status: TaskStatus | None = None,
        limit: int = 50,
    ) -> list[Task]:
        tasks = list(self._local_tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]

    async def _persist(self, task: Task) -> None:
        self._local_tasks[task.id] = task
        try:
            await self._redis.store_task(task.id, task.model_dump(mode="json"))
        except RuntimeError:
            pass
